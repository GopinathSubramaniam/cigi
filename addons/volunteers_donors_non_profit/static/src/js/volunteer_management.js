let otpRes = { 'email': '', 'otp': '' };

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

function sendOTP(ev) {
    console.log('called');
    $('#send_otp_btn').attr('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> &nbsp; Send OTP')

    const email = $('#email').val();
    if (email) {
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
                } else {
                    console.log('Failed to send OTP');
                }
            }
        });
    }

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
                    const fields = ['phone', 'gender', 'country_id', 'city', 'qualification', 'function', 'res_volunteer_type_id',
                        'comment', 'street', 'state_id', 'website', 'specialization', 'company_name', 'mobile']

                    fields.forEach((field, i) => {
                        if (o[field]) $(`[name=${field}]`).val(o[field]);
                    });
                    // $('[name=res_volunteer_skill_ids]').val(o.res_volunteer_skill_ids);
                }
                $('.div_form').removeClass('d-none');
            }, 1000);
        }, 3000)
    } else {
        alert('Invalid OTP');
    }
}

buildProgressingBar('progressing-indicator');
buildProgressingBar('progressing-indicator-campaign');
getStates();