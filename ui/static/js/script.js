// Dev Response Box Management Functions
function hideDevResponse() {
    const devResponseBox = document.getElementById("dev-response");
    const toggleDevViewButton = document.getElementById("toggleDevView");
    
    devResponseBox.classList.remove("dev-response-visible");
    devResponseBox.classList.add("dev-response-hidden");
    toggleDevViewButton.textContent = "Expand Dev View";
}

function showDevResponse() {
    const devResponseBox = document.getElementById("dev-response");
    const toggleDevViewButton = document.getElementById("toggleDevView");
    
    devResponseBox.classList.remove("dev-response-hidden");
    devResponseBox.classList.add("dev-response-visible");
    toggleDevViewButton.textContent = "Collapse Dev View";
}

function toggleDevResponse() {
    const devResponseBox = document.getElementById("dev-response");
    
    if (devResponseBox.classList.contains("dev-response-hidden")) {
        showDevResponse();
    } else {
        hideDevResponse();
    }
}

function setDevResponseContent(content) {
    const devResponseBox = document.getElementById("dev-response");
    devResponseBox.innerText = content;
}

// Error Handling Functions
function handleError(error, userMessage = "An error occurred. Please try again.") {
    console.error("Error:", error);
    
    // Show error in dev response box
    setDevResponseContent(`Error: ${error.message || error}`);
    showDevResponse();
    
    // Show user-friendly message in map container if it exists
    const cityMapBox = document.getElementById("city-map");
    if (cityMapBox && userMessage) {
        cityMapBox.innerHTML = `<p style="color: red;">${userMessage}</p>`;
    }
}

// Street Management Functions
function updateStreetOptions(streets) {
    const streetSelect = document.getElementById('street-select');
    
    // Clear current options
    streetSelect.innerHTML = '<option value="">Select a street</option>';
    
    // Append the filtered streets
    streets.forEach(street => {
        const option = document.createElement('option');
        option.value = street;
        option.textContent = street;
        streetSelect.appendChild(option);
    });
}

function loadStreets() {
    fetch('/api/streets/')
        .then(response => response.json())
        .then(data => {
            const streets = data.streets || [];
            updateStreetOptions(streets);
        })
        .catch(error => {
            handleError(error, null); // No user message needed for street loading
        });
}

// Map Management Functions
function initializeMap() {
    const cityMapBox = document.getElementById("city-map");
    
    // Clear previous content and show loading state
    cityMapBox.innerHTML = `<div id="map"></div>`;
    cityMapBox.classList.add("visible");
    
    // Initialize map
    const map = L.map('map').setView([32.0699, 34.7735], 16); // Center Tel Aviv
    
    // Add OSM tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors & CartoDB',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);
    
    return map;
}

function addRadiusCircle(map, center, radiusInMeters) {
    // Add a gray circle to show the search radius
    const radiusCircle = L.circle(center, {
        color: '#333333',
        fillColor: '#888888',
        fillOpacity: 0.3,
        weight: 1,
        radius: radiusInMeters
    }).addTo(map);
    
    return radiusCircle;
}

function calculatePolygonCenter(data) {
    // Calculate the center point of all polygons
    let totalLat = 0;
    let totalLng = 0;
    let pointCount = 0;
    
    data.forEach(item => {
        if (item.geometry && item.geometry.rings) {
            item.geometry.rings.forEach(ring => {
                ring.forEach((point, index) => {
                    // Ensure we have valid coordinates
                    if (Array.isArray(point) && point.length >= 2) {
                        totalLat += point[0]; // Latitude (was point[1])
                        totalLng += point[1]; // Longitude (was point[0])
                        pointCount++;
                    }
                });
            });
        }
    });
    
    if (pointCount > 0) {
        const center = [totalLat / pointCount, totalLng / pointCount];
        return center;
    }
    
    // Fallback to Tel Aviv center if no valid points found
    return [32.0699, 34.7735];
}

function addPolygonsToMap(map, data) {
    const addedPolygons = [];
    
    data.forEach(item => {
        // Ensure the 'attributes' and 'geometry' exist before accessing
        if (item.attributes && item.geometry && item.geometry.rings) {
            const color = item.attributes.sw_tama_38 === "כן" ? 'red' : 'yellow';
            const {rings} = item.geometry;
            
            const polygon = L.polygon(rings, {
                color: color,
                fillColor: color,
                fillOpacity: 0.5,
                weight: 2
            })
            .addTo(map)
            .bindPopup(`${item.attributes.addresses}<br>Tama 38: ${item.attributes.sw_tama_38}`);
            
            addedPolygons.push(polygon);
        } else {
            console.warn("Skipping item due to missing attributes or geometry:", item);
        }
    });
    
    // Zoom or fit map to all polygons
    if (addedPolygons.length > 0) {
        const polygonGroup = L.featureGroup(addedPolygons);
        map.fitBounds(polygonGroup.getBounds().pad(0.5));
    } else {
        alert("No valid polygons found in the response to display.");
    }
}

// Form Processing Functions
function processAnalyzeResponse(data, map, radius) {
    // Display raw JSON response for dev
    setDevResponseContent(JSON.stringify(data, null, 2));
    
    if (!Array.isArray(data) || data.length === 0) {
        alert("No problematic addresses found nearby.");
        return;
    }
    
    // Add radius circle first (so it appears behind polygons)
    const center = calculatePolygonCenter(data);
    const radiusInMeters = parseInt(radius);
    
    let radiusCircle = null;
    if (center && radiusInMeters > 0) {
        radiusCircle = addRadiusCircle(map, center, radiusInMeters);
    } else {
        console.error("Invalid center or radius for circle:", center, radiusInMeters);
    }
    
    // Add polygons to map
    addPolygonsToMap(map, data);
    
    // Fit map to show both polygons and radius circle
    if (radiusCircle) {
        const polygons = [];
        data.forEach(item => {
            if (item.attributes && item.geometry && item.geometry.rings) {
                polygons.push(L.polygon(item.geometry.rings));
            }
        });
        
        if (polygons.length > 0) {
            const allFeatures = [...polygons, radiusCircle];
            const group = L.featureGroup(allFeatures);
            map.fitBounds(group.getBounds().pad(0.5));
        }
    }
}

function submitAddressForm(event) {
    event.preventDefault();
    
    const street = document.getElementById("street-select").value;
    const houseNumber = document.getElementById("houseNumber").value;
    const radius = document.getElementById("radius").value;
    
    // Reset dev view on new submission
    hideDevResponse();
    
    // Initialize map
    const map = initializeMap();
    
    // Fetch and process data
    fetch('/api/analyze/', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ street: street, houseNumber: houseNumber, radius: radius }),
    })
    .then(response => response.json())
    .then(data => processAnalyzeResponse(data, map, radius))
    .catch(error => handleError(error));
}

// Main Initialization
document.addEventListener("DOMContentLoaded", function () {
    const toggleDevViewButton = document.getElementById("toggleDevView");
    
    // Initialize dev view
    hideDevResponse();
    
    // Set up dev view toggle
    toggleDevViewButton.addEventListener("click", toggleDevResponse);
    
    // Load streets
    loadStreets();
    
    // Set up form submission
    document.getElementById("addressForm").addEventListener("submit", submitAddressForm);
});