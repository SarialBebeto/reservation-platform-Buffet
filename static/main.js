document.getElementById('resForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Stop page from reloading

    // Change button text so the user knows it's working
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.innerText = "Processing...";
    submitBtn.disabled = true;

    // Collect form data
    const formData = new FormData(this);
    // formData.append('package_type', document.getElementById('package_select').value);

    // Send data to FastAPI app
    fetch('/reserve', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            // Replace the form with a success message
            const container = document.getElementById('form-container');
            container.innerHTML = `
                <div class="text-center p-6 bg-green-50 rounded-lg border border-green-200">
                    <h3 class="text-2xl font-bold text-green-700 mb-2">Reservation Requested!</h3>
                    <p class="text-gray-700 mb-4">Your Transaction Code is:</p>
                    <div class="text-3xl font-mono font-bold text-indigo-600 mb-4 bg-white p-3 rounded border inline-block">
                        ${data.transaction_code}
                    </div>
                    <p class="text-[10px] text-indigo-500 mt-2 italic">Copy this code into your payment description</p>
                </div>

                <div class="text-left space-y-4">
                        <div class="border-t pt-4">
                            <h4 class="font-bold text-gray-800 flex items-center">
                                <span class="mr-2">🔵</span> Option 1: PayPal (Friends & Family)
                            </h4>
                            <p class="text-sm text-gray-600 ml-6 mt-1">
                                Send to: <strong class="text-indigo-600">My-paypalaccount@email.com</strong>
                                with Message: <strong> your ${data.transaction_code}</strong>
                            </p>
                        </div>

                        <div class="border-t pt-4">
                            <h4 class="font-bold text-gray-800 flex items-center">
                                <span class="mr-2">🏦</span> Option 2: Bank Transfer (SEPA)
                            </h4>
                            <div class="text-sm text-gray-600 ml-6 mt-1 space-y-1">
                                <p>Bank: <strong>Your Bank Name</strong></p>
                                <p>IBAN: <strong>DE00 0000 0000 0000 0000 00</strong></p>
                                <p>BIC: <strong>ABCDEFGHXXX</strong></p>
                                <p>Verwendungszweck: <strong> your ${data.transaction_code}</strong></p>
                            </div>
                        </div>
                    </div>

                    <div class="mt-8 pt-4 border-t text-[11px] text-gray-400">
                        Once confirmed, your official ticket will be sent to your email address automatically.
                    </div>
                </div>
            `;
        } else {
            console.log(data);
            alert("Error: " + JSON.stringify(data.detail));
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

