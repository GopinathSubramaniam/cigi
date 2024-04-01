
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

    function buildProgressingBar(id) {
        const parent_elem = document.getElementById(id);
        if (parent_elem) {
            let obj = { progress_color: '#28A745', text_color: '#000', percent: 90 };
            let html = ` <div class="progress-group" id="progress-group">
                            <div class="circular-progress" >
                                <span class="circular-value" style="color:${obj.text_color}">${obj.percent}%</span>
                            </div>
                        </div>`;
            parent_elem.innerHTML = html;

            let elem = document.getElementById("progress-group");
            console.log('Elem = ', elem);

            if (elem) {
                let progressStartValue = 0;
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
            }
        }

    }

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

    buildProgressingBar('progressing-indicator');

});