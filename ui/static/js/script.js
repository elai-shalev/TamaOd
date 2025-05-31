document.addEventListener("DOMContentLoaded", function () {
    const streetSelect = document.getElementById('street-select');
    const devResponseBox = document.getElementById("dev-response");
    const toggleDevViewButton = document.getElementById("toggleDevView");

    // --- Dev View Control Setup ---
    // Initially hide the dev response box
    devResponseBox.classList.add("dev-response-hidden");
    devResponseBox.classList.remove("dev-response-visible"); // Ensure it doesn't have the visible class
    toggleDevViewButton.textContent = "Expand Dev View"; // Set initial button text

    // Add event listener to toggle the dev view
    toggleDevViewButton.addEventListener("click", function() {
        if (devResponseBox.classList.contains("dev-response-hidden")) {
            // If currently hidden, show it
            devResponseBox.classList.remove("dev-response-hidden");
            devResponseBox.classList.add("dev-response-visible");
            toggleDevViewButton.textContent = "Collapse Dev View";
        } else {
            // If currently visible, hide it
            devResponseBox.classList.remove("dev-response-visible");
            devResponseBox.classList.add("dev-response-hidden");
            toggleDevViewButton.textContent = "Expand Dev View";
        }
    });
    // --- End Dev View Control Setup ---

    // Fetch streets from the server (your existing code)
    fetch('/api/streets/')
        .then(response => response.json())
        .then(data => {
            const streets = data.streets || [];
            // Function to update the dropdown options based on filtered streets
            function updateStreetOptions(filteredStreets) { // Corrected parameter name
                // Clear current options
                streetSelect.innerHTML = '<option value="">Select a street</option>';
                // Append the filtered streets
                filteredStreets.forEach(street => { // <-- THIS LINE WAS THE TYPO
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
            // Optionally, show error in dev response box if it's meant to capture all errors
            devResponseBox.innerText = `Error fetching streets: ${error.message || error}`;
            devResponseBox.classList.remove("dev-response-hidden"); // Make visible if there's an error
            devResponseBox.classList.add("dev-response-visible");
            toggleDevViewButton.textContent = "Collapse Dev View"; // Update button text
        });
});

// COMBINED EVENT LISTENER FOR FORM SUBMISSION
document.getElementById("addressForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    const street = document.getElementById("street-select").value;
    const houseNumber = document.getElementById("houseNumber").value;
    const radius = document.getElementById("radius").value;

    const devResponseBox = document.getElementById("dev-response");
    const toggleDevViewButton = document.getElementById("toggleDevView");
    const cityMapBox = document.getElementById("city-map");

    // --- Reset Dev View on new Submission ---
    // Hide the dev response box and reset button text when a new search begins
    devResponseBox.classList.remove("dev-response-visible");
    devResponseBox.classList.add("dev-response-hidden");
    toggleDevViewButton.textContent = "Expand Dev View";
    // --- End Reset Dev View ---

    // Clear previous map/content and show loading state if desired
    cityMapBox.innerHTML = `<div id="map" style="height: 400px;"></div>`;
    cityMapBox.classList.add("visible");

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
            // Display error message in the map container (user-facing)
            cityMapBox.innerHTML = `<p style="color: red;">An error occurred. Please try again.</p>`;
            
            // Also display error in the dev response box and make it visible
            devResponseBox.innerText = `Error: ${error.message || error}`;
            devResponseBox.classList.remove("dev-response-hidden");
            devResponseBox.classList.add("dev-response-visible");
            toggleDevViewButton.textContent = "Collapse Dev View"; // Update button text
        });
});