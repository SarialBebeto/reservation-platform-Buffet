let iti;
document.addEventListener('DOMContentLoaded', () => {
    const phoneInput = document.querySelector("#phone");
    const phoneMsg = document.querySelector("#phone-msg");

    iti = window.intlTelInput(phoneInput, {
        initialCountry: "auto",
        separateDialCode: true,
        utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
    });

    const updateCounter = () => {
        if (phoneInput.value.trim()) {
            if (iti.isValidNumber()) {
                phoneMsg.textContent = "✅ Valid number";
                phoneMsg.classList.replace("text-gray-500", "text-green-600");
                phoneMsg.classList.remove("text-red-500");
            } else {
                const errorCode = iti.getValidationError();
                // Library returns codes: 2 = too short, 3 = too long
                if (errorCode === 2) {
                    phoneMsg.innerHTML = "⚠️ Number too short";
                } else if (errorCode === 3) {
                    phoneMsg.innerHTML = "⚠️ Number too long";
                } else {
                    phoneMsg.innerHTML = "❌ Invalid format";
                }
                phoneMsg.classList.add("text-red-500");
            }
        } else {
            phoneMsg.innerHTML = ""; 
        }
    };

    phoneInput.addEventListener('keyup', updateCounter);
    phoneInput.addEventListener('change', updateCounter);
    phoneInput.addEventListener('countrychange', updateCounter);
    
});


document.getElementById('resForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Stop page from reloading

    // Change button text so the user knows it's working
    const submitBtn = document.getElementById('submit-btn');
    const fullNumber = iti.getNumber();

    if (!iti.isValidNumber()) {
        alert("Please enter a valid phone number before submitting.");
        document.querySelector("#phone").focus();
        return;
    }

    submitBtn.innerText = "Processing...";
    submitBtn.disabled = true;

    // Collect form data
    const formData = new FormData(this);
    formData.set('phone', iti.getNumber()); // Update the phone field with the full number

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
                                with Message: <strong>  ${data.transaction_code}</strong>
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
                                <p>Verwendungszweck: <strong>  ${data.transaction_code}</strong></p>
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

