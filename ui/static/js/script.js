document.addEventListener("DOMContentLoaded", function () {
    // Fetch streets from the server
    fetch('/api/streets/')
        .then(response => response.json())
        .then(data => {
            const streetSelect = document.getElementById('street-select');
            if (data && data.streets) {
                // Loop over the streets array and populate the select dropdown
                data.streets.forEach(street => {
                    const option = document.createElement('option');
                    option.value = street;
                    option.textContent = street;
                    streetSelect.appendChild(option);
                });
            } else {
                console.error('No streets data found');
            }
        })
        .catch(error => {
            console.error('Error fetching streets:', error);
        });

    // You can add more JavaScript functionality here
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

