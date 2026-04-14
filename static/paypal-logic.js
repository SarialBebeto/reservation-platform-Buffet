paypal.Buttons({
    // Simple validation before opening Paypal window
    onclick: function(data, actions) {
        const first = document.getElementById('first_name').value;
        const last = document.getElementById('last_name').value;
        const email = document.getElementById('email').value;

        if (!first || !last || !email) {
            alert('Please fill in all required fields before proceeding to payment.');
            return actions.reject();
        }
        return actions.resolve();
    },

    // Dynamically set the amount based on the selected package
    createOrder: function(data, actions) {
        const select = document.getElementById('package_select');
        const price  = select.options[select.selectedIndex].getAttribute('data-price');
        const description = select.options[select.selectedIndex].text;

        return actions.order.create({
            purchase_units: [{
                amount: {
                    value: price
                },
                description: description
            }]
        });
    },

    // Backend Synchronization 

    onApprove: function(data, actions) {
        return actions.order.capture().then(function(details){

            // Generate automatic date and time
            const now = new Date();
            const autoDate = now.toISOString().split('T')[0]; // YYYY-MM-DD
            const autoTime = now.toTimeString().split(' ')[0].slice(0,5); // HH:MM


            const payload = {
                first_name: document.getElementById('first_name').value,
                last_name: document.getElementById('last_name').value,
                email: document.getElementById('email').value,
                package_type: document.getElementById('package_select').value,
                paypal_order_id: data.orderID,
                date: autoDate, 
                time: autoTime
            };

            fetch('/verify-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
                }).then(res => {
                    if(res.ok) {
                        document.getElementById('form-container').classList.add('hidden');
                        document.getElementById('success-message').classList.remove('hidden');
                    }
                    else {
                        alert("Payment verified but database update failed. Please contact support with your order ID: " + data.orderID);
                    }
                });

        });   
    }
}).render('#paypal-button-container');

