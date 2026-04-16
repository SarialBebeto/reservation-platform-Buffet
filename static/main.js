document.getElementById('reservation_form').addEventListener('submit', function(e) {
    e.preventDefault(); // Stop page from reloading

    // Change button text so the user knows it's working
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.innerText = "Processing...";
    submitBtn.disabled = true;

    // Collect form data
    const formData = new FormData(this);
    formData.append('package_type', document.getElementById('package_select').value);

    // Send data to FastAPI app
    fetch('/reserve', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            // Replace the form with a success message
            const formContainer = document.getElementById('form-container');
            formContainer.innerHTML = `
                <div class="text-center p-6 bg-green-50 rounded-lg border border-green-200">
                    <h3 class="text-2xl font-bold text-green-700 mb-2">Reservation Requested!</h3>
                    <p class="text-gray-700 mb-4">Your Transaction Code is:</p>
                    <div class="text-3xl font-mono font-bold text-indigo-600 mb-4 bg-white p-3 rounded border inline-block">
                        ${data.transaction_code}
                    </div>
                    <p class="text-sm text-gray-600 text-left">
                        <strong>Next Steps:</strong><br>
                        1. Please send the payment via PayPal directly to <strong>your.email@example.com</strong> or via Bank Transfer.<br>
                        2. <strong>Crucial:</strong> Put your Transaction Code in the transfer description.<br>
                        3. Once we receive the funds, we will email your official ticket.<br>
                        <em>Reservations without payment are canceled after 48 hours.</em>
                    </p>
                </div>
            `;
        } else {
            alert("Something went wrong. Please try again.");
            submitBtn.innerText = "Request Reservation";
            submitBtn.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Network error.");
        submitBtn.innerText = "Request Reservation";
        submitBtn.disabled = false;
    });

});

