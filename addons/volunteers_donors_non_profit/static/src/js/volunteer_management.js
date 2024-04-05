
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

buildProgressingBar('progressing-indicator');
buildProgressingBar('progressing-indicator-campaign');