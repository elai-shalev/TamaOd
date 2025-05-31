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


// COMBINED EVENT LISTENER FOR FORM SUBMISSION
document.getElementById("addressForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    const street = document.getElementById("street-select").value;
    const houseNumber = document.getElementById("houseNumber").value;
    const radius = document.getElementById("radius").value;

    const devResponseBox = document.getElementById("dev-response"); // Get dev box
    const cityMapBox = document.getElementById("city-map"); // Get the map container

    // Clear previous map/content and show loading state if desired
    cityMapBox.innerHTML = `<div id="map" style="height: 400px;"></div>`;
    cityMapBox.classList.add("visible");
    devResponseBox.classList.remove("visible"); // Hide dev response initially or clear it

    // Initialize map immediately
    const map = L.map('map').setView([32.0699, 34.7735], 16); // Center Tel Aviv

    // OSM tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors & CartoDB',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    fetch('/api/analyze/', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ street: street, houseNumber: houseNumber, radius: radius }),
    })
        .then(response => response.json())
        .then(data => {
            // Display raw JSON response for dev
            devResponseBox.classList.add("visible");
            devResponseBox.innerText = JSON.stringify(data, null, 2);

            if (!Array.isArray(data) || data.length === 0) {
                alert("No problematic addresses found nearby."); // Use alert or update a specific message div
                // Optional: clear map or display a message on the map container
                // map.remove(); // if you want to completely remove the map if no results
                // cityMapBox.innerHTML = "<p>No problematic addresses found.</p>";
                return;
            }

            const addedPolygons = []; // Array to store polygon objects for fitBounds

            // Add polygons to the map based on backend response
            data.forEach(item => {
                // Ensure the 'attributes' and 'geometry' exist before accessing
                if (item.attributes && item.geometry && item.geometry.rings) {
                    const color = item.attributes.sw_tama_38 === "כן" ? 'red' : 'yellow';
                    const rings = item.geometry.rings;

                    const polygon = L.polygon(rings, {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.5,
                        weight: 2
                    })
                    .addTo(map)
                    .bindPopup(`${item.attributes.addresses}<br>Tama 38: ${item.attributes.sw_tama_38}`);

                    addedPolygons.push(polygon); // Store the created polygon
                } else {
                    console.warn("Skipping item due to missing attributes or geometry:", item);
                }
            });

            // Zoom or fit map to all polygons
            if (addedPolygons.length > 0) {
                const polygonGroup = L.featureGroup(addedPolygons);
                map.fitBounds(polygonGroup.getBounds().pad(0.5));
            } else {
                // If data was not empty but no polygons were added (e.g., due to filtering/missing data)
                alert("No valid polygons found in the response to display.");
            }


        })
        .catch(error => {
            console.error("Error fetching data:", error);
            // Update the map container with an error message, or use an alert
            cityMapBox.innerHTML = `<p style="color: red;">An error occurred. Please try again.</p>`;
            devResponseBox.classList.add("visible");
            devResponseBox.innerText = `Error: ${error.message || error}`;
        });
});