function checkCouponValidity() {
    const totalAmtDiv = document.getElementById('total-amount');
    const resultDiv = document.getElementById('coupon-result');
    const discountedAmountDiv = document.getElementById('discounted-amount');
    const couponCode = document.getElementById('coupon_code').value;
    const orderAmount = parseFloat(document.getElementById('order_amount').value);

    resultDiv.innerHTML = '';
    discountedAmountDiv.innerHTML = '';
    totalAmtDiv.classList.remove('text-decoration-line-through');

    fetch('/event/apply_custom_coupon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ coupon_code: couponCode, order_amount: orderAmount }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.result.success) {
                totalAmtDiv.classList.add('text-decoration-line-through');
                resultDiv.innerHTML = `<div class="alert alert-success">${data.result.message}</div>`;
                discountedAmountDiv.innerHTML = `<span class="text-success">INR ${Number.parseFloat(data.result.discounted_amount).toFixed(2)}</span>`
            } else {
                resultDiv.innerHTML = `<div class="alert alert-danger">${data.result.message}</div>`;
            }
        });
}

function removeCoupon() {
    document.getElementById('total-amount').classList.remove('text-decoration-line-through');
    document.getElementById('coupon-result').innerHTML = '';
    document.getElementById('discounted-amount').innerHTML = '';
    document.getElementById('coupon_code').value = '';
}