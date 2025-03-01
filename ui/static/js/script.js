document.addEventListener("DOMContentLoaded", function () {
    const streetSelect = document.getElementById('street-select');
    const streetInput = document.getElementById('street-input');

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

            // Filter streets as user types
            streetInput.addEventListener('input', function () {
                const filteredStreets = streets.filter(street =>
                    street.includes(searchValue)
                );

                updateStreetOptions(filteredStreets);
            });

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
        body: JSON.stringify({ "street": street, "houseNumber": houseNumber, "radius": radius }),
    })
        .then(response => response.json())
        .then(data => {
            const responseBox = document.getElementById("response");
            responseBox.classList.add("visible");
            responseBox.innerText = JSON.stringify(data, null, 2);
        });
});

