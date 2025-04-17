let otpRes = { 'email': '', 'otp': '' };
let existing_data = {};
let expanded = false;
let selectedVolunteerSkillIds = [];
let selectedVolunteerSkillNames = [];

$(function () {
    var options = {
        "key": "rzp_test_kPow8NV72MMXWb", // Enter the Key ID generated from the Dashboard
        "amount": "50000", // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
        "currency": "INR",
        "name": "Acme Corp", //your business name
        "description": "Test Transaction",
        "image": "https://example.com/your_logo",
        "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
        "callback_url": "http://localhost:8069/",
        "prefill": { //We recommend using the prefill parameter to auto-fill customer's contact information especially their phone number
            "name": "Gaurav Kumar", //your customer's name
            "email": "gaurav.kumar@example.com",
            "contact": "9000090000" //Provide the customer's phone number for better conversion rates 
        },
        "notes": {
            "address": "Razorpay Corporate Office"
        },
        "theme": {
            "color": "#3399cc"
        }
    };
    var rzp1 = new Razorpay(options);

    $('#initializeRazorpay').click((ev) => {
        rzp1.open();
        ev.preventDefault();
    });



    /* const progressBar = document.querySelector('.progress-bar__fill');

    function animateProgressBar() {
        let progress = 0;
        const increment = 1 / 100; // Adjust the increment value for desired smoothness.

        const interval = setInterval(() => {
            progress += increment;
            progressBar.style.width = `${progress * 100}%`;

            if (progress >= 1) {
                clearInterval(interval);
            }
        }, 10);
    }

    animateProgressBar(); */
});


function buildProgressingBar(class_name) {
    console.log('buildProgressingBar called');
    const elems = document.querySelectorAll('.' + class_name);
    if (elems && elems.length > 0) {
        for (let i = 0; i < elems.length; i++) {
            let percent = elems[i].attributes['data-percent'].value;
            elems[i].style.color = "white";
            // elems[i].style.backgroundColor = "black";
            let html = ` <div class="progress-group" id="progress-group">
                        <div class="circular-progress" >
                            <span class="circular-value" style="color: #000">${percent}%</span>
                        </div>
                    </div>`;
            elems[i].innerHTML = html;
            let el = elems[i].querySelector(".progress-group");
            console.log('el = ', el);
            if (el) {
                /* let progressStartValue = 0;
                let progressStartEnd = obj.percent;
                let speed = 50;
                let progessTimer = setInterval(() => {
                    progressStartValue++;
                    if (progressStartValue == progressStartEnd) {
                        clearInterval(progessTimer);
                    }
                    elem.querySelector(".circular-progress").style.background = `conic-gradient(${obj.progress_color} ${3.6 * progressStartValue}deg, #D5D5D5 0deg)`;
                    elem.querySelector(".circular-value").innerHTML = progressStartValue + "%";
                }, speed);
                let progressStartEnd = obj.percent;
                 */
                el.querySelector(".circular-progress").style.background = `conic-gradient(#28A745 ${3.6 * percent}deg, #D5D5D5 0deg)`;
                el.querySelector(".circular-value").innerHTML = percent + "%";
            }
        }
    }
}

function enableTaxBenefit(ev) {
    $('.tax_benefit').addClass('d-none');
    $('#country_of_residence, #id_number, #state_id, #city, #zip, #address').removeAttr('required');
    if (ev.checked) {
        $('.tax_benefit').removeClass('d-none');
        $('#country_of_residence, #id_number, #state_id, #city, #zip, #address').attr('required', 1);
    }
}

function getStates(ev) {
    $.ajax({
        url: '/app/get_states_by_country_code',
        type: 'GET',
        data: { 'country_code': 'IN' },
        success: function (data) {
            var $stateDropdown = $('#state_id');
            $stateDropdown.empty();

            if (data.states) {
                $stateDropdown.append('<option value="">-- Select a state --</option>');
                $.each(data.states, function (index, state) {
                    $stateDropdown.append('<option value="' + state.id + '">' + state.name + '</option>');
                });
            } else {
                $stateDropdown.append('<option value="">No states available</option>');
            }
        }
    });
}

function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function stripHTML(input) {
    return input.replace(/<\/?[^>]+(>|$)/g, "");
}

function sendOTP(ev) {
    console.log('called');
    $('#send_otp_btn').attr('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> &nbsp; Send OTP')

    const email = $('#email').val();
    if (!isValidEmail(email)) {
        $('#email').addClass('is-invalid');
        alert('Please enter a valid email address.');
        location.reload();
        $('#sent_otp_btn').attr('disabled', false).html('Sent OTP');
        return;
    }else {
        $('#email').removeClass('is-invalid');

    }
        $.ajax({
            url: '/web/volunteer/send_otp',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'email': email }),
            success: function (data) {
                if (data.otp) {
                    otpRes = data;
                    $('#send_otp_btn').attr('disabled', false).html('Send OTP')
                    $('#send_otp_form').addClass('d-none');
                    $('#verify_otp_form').removeClass('d-none');
                } else if (data.error) {
                    alert(data.error);
                    $('#send_otp_btn').attr('disabled', false).html('Send OTP');
                } else {
                    console.log('Failed to send OTP');
                }
            }
        });
    }

function verifyOTP() {
    const email = $('#email').val();
    const entered_otp = $('#entered_otp').val();

    if (email == otpRes.email && entered_otp == otpRes.otp) {
        $('#verify_otp_btn').attr('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> &nbsp; Verify OTP')
        setTimeout(() => {
            $('#verify_otp_btn').attr('disabled', false).html('<i class="fa fa-check-circle"></i> &nbsp; Verify OTP')
            setTimeout(() => {
                $('#verify_otp_form').addClass('d-none');
                // Filling existing infromation
                if (otpRes.data) {
                    const o = otpRes.data;
                    existing_data = o;
                    const fields = ['phone', 'gender', 'country_id', 'qualification', 'function', 'res_volunteer_type_id',
                        'comment', 'street', 'state_id', 'website', 'specialization', 'company_name', 'mobile']

                        fields.forEach((field) => {
                            if (o[field]) {
                                let cleanValue = (field === 'comment') ? stripHTML(o[field]) : o[field];
                                $(`[name=${field}]`).val(cleanValue);
                            }
                        });    
                    
                    
                    $('#contact_picture').attr('src', `/web/volunteer/get_profile_picture/${o.id}`)

                    // <> Manage phone data
                    if (o.phone) {
                        const p_splitted = o.phone.split(' ');
                        if (p_splitted.length === 3) {
                            $('#phone_country_code').val(p_splitted[0].trim());
                            $('[name=phone]').val(p_splitted[1].trim() + p_splitted[2].trim());
                        }
                    }
                    // </>

                    // <> Manage mobile data
                    if (o.mobile) {
                        const m_splitted = o.mobile.split(' ');
                        if (m_splitted.length === 3) {
                            $('#mobile_country_code').val(m_splitted[0].trim());
                            $('[name=mobile]').val(m_splitted[1].trim() + m_splitted[2].trim());
                        }
                    }
                    // </>

                    if (o.res_volunteer_skill_ids) {
                        o.res_volunteer_skill_ids.forEach((id, idx) => {
                            $(`#check_${id}`).attr('checked', 'checked');
                        });
                        $('#default_option').html(o.volunteer_skill_names);

                        selectedVolunteerSkillNames = o.volunteer_skill_names.split(',');
                        selectedVolunteerSkillIds = o.res_volunteer_skill_ids;
                        $('[name=res_volunteer_skill_ids]').val(selectedVolunteerSkillIds.join(','));
                    }
                    onSelectCountry();
                }
                $('.div_form').removeClass('d-none');
            }, 500);
        }, 1000)
    } else {
        alert('Invalid OTP');
    }
}

function showCheckboxes() {
    var checkboxes = document.getElementsByClassName("checkboxes");
    $.each(checkboxes, function (idx, check) {
        if (check.style.display == "block") {
            check.style.display = "none";
            // check.style.display = "block";
            // expanded = true;
        } else {
            check.style.display = "block";
            // expanded = false;
        }
    });
}

function handleCheckboxChange(event) {
    if (event.target.checked) {
        selectedVolunteerSkillIds.push(Number(event.target.value));
        selectedVolunteerSkillNames.push(event.target.attributes.data.value);
    } else {
        const idx = selectedVolunteerSkillIds.indexOf(event.target.value);
        if (idx > -1) {
            selectedVolunteerSkillIds.splice(idx, 1);
            selectedVolunteerSkillNames.splice(idx, 1);
        }
    }
    const html = selectedVolunteerSkillNames.length > 0 ? selectedVolunteerSkillNames.join(',') : '--Select Skills--';
    $('#default_option').html(html);
    $('[name=res_volunteer_skill_ids]').val(selectedVolunteerSkillIds.join(','));
}

function onSelectCountry(e) {
    if (e && e.selectedOptions && e.selectedOptions.length > 0 && e.selectedOptions[0].attributes.data) {
        if (e.selectedOptions[0].attributes.data.value == 'IN')
            $('#state_id').removeClass('d-none');
        else
            $('#state_id').addClass('d-none');
    }

    let country_id = (e && e.value) ? e.value : $('#country_id').val();
    $.ajax({
        url: '/city/bycountry/' + country_id,
        type: 'GET',
        success: function (data) {
            var $cityDropdown = $('#volunteer_form #city');
            $cityDropdown.empty();

            if (data && data.length > 0) {
                $cityDropdown.append('<option value="">-- Select a city --</option>');
                $.each(data, function (index, c) {
                    $cityDropdown.append('<option value="' + c.city_name + '">' + c.city_name + '</option>');
                });
                $('#city').val(existing_data.city);
            } else {
                $cityDropdown.append('<option value="">No cities available</option>');
            }
        }
    });
}

buildProgressingBar('progressing-indicator');
buildProgressingBar('progressing-indicator-campaign');
getStates();