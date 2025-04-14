document.addEventListener("DOMContentLoaded", function () {
    const streetSelect = document.getElementById('street-select');

    // Fetch streets from the server
    fetch('/api/streets/')
        .then(response => response.json())
        .then(data => {
            const streets = data.streets || [];

            // Function to update the dropdown options based on filtered streets
            function updateStreetOptions(filteredStreets) {
                // Clear current options
                streetSelect.innerHTML = '<option value="">Select a street</option>';

                // Append the filtered streets
                filteredStreets.forEach(street => {
                    const option = document.createElement('option');
                    option.value = street;
                    option.textContent = street;
                    streetSelect.appendChild(option);
                });
            }

            // Initial population of all streets
            updateStreetOptions(streets);

        })
        .catch(error => {
            console.error('Error fetching streets:', error);
        });
});


document.getElementById("addressForm").addEventListener("submit", function (event) {
    event.preventDefault();

    let street = document.getElementById("street-select").value;
    let houseNumber = document.getElementById("houseNumber").value;
    let radius = document.getElementById("radius").value

    fetch("/api/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ street: street, houseNumber: houseNumber, radius: radius }),
    })
        .then(response => response.json())
        .then(data => {
            const devResponseBox = document.getElementById("dev-response");
            devResponseBox.classList.add("visible");
            devResponseBox.innerText = JSON.stringify(data, null, 2);

            if (!Array.isArray(data) || data.length === 0) {
                userResponseBox.innerHTML = "<p>No problematic addresses found. + </p>";
                return;
            }

            const addressListHTML = `
            <div>
                <p>The following addresses are problematic:</p>
                <ul>
                    ${data.map(entry => {
                const details = Object.entries(entry)
                    .map(([key, value]) => {
                        const fieldName = key.replace(/_/g, ' ').toUpperCase();
                        const fieldValue = value || `No ${fieldName} provided`;
                        return `${fieldName}: ${fieldValue}`;
                    })
                    .join(', ');
                return `<li>${details}</li>`;
            }).join('')}
                </ul>
            </div>
            `;

            const userResponseBox = document.getElementById("user-response");
            userResponseBox.classList.add("visible");
            userResponseBox.innerHTML = addressListHTML;

        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById("user-response").innerHTML = `<p style="color: red;">An error occurred. Please try again.</p>`;
        });
});

