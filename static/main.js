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

function calculateTotal() {
    let total = 0;
    document.querySelectorAll('.item-qty').forEach(input => {
        total += parseInt(input.value) * parseFloat(input.dataset.price);
    });
    document.getElementById('total-display').innerText = total.toFixed(2);
    return total;
}

// Update total whenever quantity changes
document.addEventListener('input', (e) => {
    if (e.target.classList.contains('item-qty')) {
        calculateTotal();
    }
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

    let summary = "";
    document.querySelectorAll('.item-qty').forEach(input => {
        if (parseInt(input.value) > 0) {
            summary += `${input.name.replace('qty_', '')}: ${input.value},`;
        }
    });
    // formData.set('package_type', summary.slice(0, -2)); 
    let summaryParts = [];

    document.querySelectorAll('.item-qty').forEach(input => {
        const qty = parseInt(input.value);
        if (qty > 0) {
            // Get the label or name
            const itemName = input.name.replace('qty_', '').replace('_', ' ');
            summaryParts.push(`${qty}x ${itemName}`);
        }
    });

    const finalPackageString = summaryParts.join(', ');
    formData.set('package_type', finalPackageString);

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

            const paypalEmail = "tsamosarial@yahoo.fr";
            const transactionCode = data.transaction_code;
            const totalPrice = calculateTotal();
            const currency = "EUR";

            // Create a helper function for copying

            function copyCode(code) {
                navigator.clipboard.writeText(code).then(() => {
                    alert("Transaction code copied to clipboard!");
                });
            }

            // Create a clickable PayPal link with the transaction code in the message
            const paypalLink = `https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=${encodeURIComponent(paypalEmail)}&amount=${totalPrice}&currency_code=${currency}&item_name=Reservation%20${transactionCode}&invoice=${transactionCode}`;

            container.innerHTML = `
                <div class="text-center p-6 bg-green-100 rounded-lg border-2 border-indigo-100 shadow-sm fade-in">

                    <div class="flex justify-center mb-4">
                        <div class="bg-green-100 p-3 rounded-full">
                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        </div>
                    </div>

                    <h3 class="text-2xl font-bold text-green-700 mb-2">Reservation Requested!</h3>
                    <p class="text-gray-600 mb-6 text-sm">Please complete your payment within 48 hours.</p>

                    <div class="bg-indigo-50 p-4 rounded-lg mb-6 border border-indigo-100">
                        <p class="text-xs uppercase tracking-wider text-indigo-600 font-bold mb-1">Your Payment Reference</p>
                        <div class="text-3xl font-mono font-black text-indigo-800">
                            ${transactionCode}
                        </div>
                        <button onclick="copyCode('${transactionCode}')" class="text-[10px] bg-indigo-200 text-indigo-700 px-2 py-1 rounded hover:bg-indigo-300 transition">
                            Copy Code
                        </button>
                    </div>
                    <p class="text-[10px] text-indigo-500 mt-2 italic">Copy this code into your payment description</p>
                </div>

                <div class="text-left space-y-4">
                        <div class="border-t pt-4">
                            <h4 class="font-bold text-gray-800 flex items-center">
                                <span class="mr-2">🔵</span> Option 1: PayPal (Friends & Family)
                            </h4>
                            <p class="text-sm text-gray-600 ml-6 mt-1">
                                <a href="${paypalLink}" target="_blank" class="inline-block bg-[#0070ba] text-white px-4 py-2 rounded-full font-bold text-xs hover:bg-[#005ea6] transition">
                                    Pay with PayPal
                                </a>
                                <br>
                                <span class="text-[10px] text-gray-400 mt-1 block">Don't forget to paste your reference code!</span>
                        </div>

                        <div class="border-t pt-4">
                            <h4 class="font-bold text-gray-800 flex items-center">
                                <span class="mr-2">🏦</span> Option 2: Bank Transfer (SEPA)
                            </h4>
                            <div class="text-sm text-gray-600 ml-6 mt-1 space-y-1">
                                <p>Bank: <strong>Your Bank Name</strong></p>
                                <p>IBAN: <strong>DE00 0000 0000 0000 0000 00</strong></p>
                                <p>BIC: <strong>ABCDEFGHXXX</strong></p>
                                <p>Verwendungszweck: <strong>${transactionCode}</strong></p>
                            </div>
                        </div>
                    </div>

                    <div class="mt-8 pt-4 border-t text-[11px] text-gray-400">
                        Once payment confirmed, your official ticket will be sent to your email address automatically.
                        A confirmation of these details has been sent to your email. 
                    </div>

                    <div class="mt-8 space-y-3">
                        <button onclick="window.location.reload()" class="w-full bg-gray-100 text-gray-700 font-bold py-3 rounded-lg hover:bg-gray-200 transition duration-300 border border-gray-300">
                            Make Another Reservation
                        </button>
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

