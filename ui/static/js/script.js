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
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(`Failed to load streets (${response.status}): ${errorData.error || response.statusText}`);
                }).catch(() => {
                    throw new Error(`Failed to load streets (${response.status}): ${response.statusText}`);
                });
            }
            return response.json();
        })
        .then(data => {
            const streets = data.streets || [];
            updateStreetOptions(streets);
        })
        .catch(error => {
            console.error("Error loading streets:", error);
            // Show error but don't block the UI
            handleError(error, null);
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
    // Calculate the center point of all polygons and markers
    let totalLat = 0;
    let totalLng = 0;
    let pointCount = 0;
    
    data.forEach(item => {
        if (item.geometry && item.geometry.rings) {
            // Handle polygons with rings
            item.geometry.rings.forEach(ring => {
                ring.forEach((point, index) => {
                    // Ensure we have valid coordinates
                    if (Array.isArray(point) && point.length >= 2) {
                        totalLat += point[0]; // Latitude
                        totalLng += point[1]; // Longitude
                        pointCount++;
                    }
                });
            });
        } else if (item.attributes) {
            // Handle markers - use attributes coordinates or estimate from address
            const lat = item.attributes.lat;
            const lng = item.attributes.lng;
            if (lat && lng) {
                totalLat += parseFloat(lat);
                totalLng += parseFloat(lng);
                pointCount++;
            }
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
        // Ensure the 'attributes' exists
        if (!item.attributes) {
            console.warn("Skipping item due to missing attributes:", item);
            return;
        }
        
        const color = item.attributes.sw_tama_38 === "כן" ? 'red' : 'yellow';
        const address = item.attributes.addresses || "Unknown address";
        const popupText = `${address}<br>Tama 38: ${item.attributes.sw_tama_38 || "N/A"}`;
        
        // If geometry with rings exists, add polygon
        if (item.geometry && item.geometry.rings) {
            const {rings} = item.geometry;
            
            const polygon = L.polygon(rings, {
                color: color,
                fillColor: color,
                fillOpacity: 0.5,
                weight: 2
            })
            .addTo(map)
            .bindPopup(popupText);
            
            addedPolygons.push(polygon);
        } else {
            // If no geometry, add a marker instead (for mock data)
            // Try to get coordinates from attributes or use a default location
            const lat = item.attributes.lat || 32.0699;  // Tel Aviv center
            const lng = item.attributes.lng || 34.7735;
            
            const marker = L.marker([lat, lng], {
                icon: L.divIcon({
                    className: 'custom-marker',
                    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
                    iconSize: [20, 20]
                })
            })
            .addTo(map)
            .bindPopup(popupText);
            
            addedPolygons.push(marker);
        }
    });
    
    // Return the array of added polygons/markers
    return addedPolygons;
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
        // UPDATED: Make the radius circle much larger to encompass all addresses
        // Triple the size to ensure all addresses are definitely within the circle
        const displayRadius = Math.round(radiusInMeters * 1.5);
        radiusCircle = addRadiusCircle(map, center, displayRadius);
    } else {
        console.error("Invalid center or radius for circle:", center, radiusInMeters);
    }
    
    // Add polygons to map and get the array of added features
    const addedPolygons = addPolygonsToMap(map, data);
    
    // Fit map to show both polygons/markers and radius circle
    if (radiusCircle && addedPolygons.length > 0) {
        const allFeatures = [...addedPolygons, radiusCircle];
        const group = L.featureGroup(allFeatures);
        map.fitBounds(group.getBounds().pad(0.5));
    } else if (addedPolygons.length > 0) {
        // If no radius circle, just fit to polygons/markers
        const group = L.featureGroup(addedPolygons);
        map.fitBounds(group.getBounds().pad(0.5));
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
    .then(response => {
        if (!response.ok) {
            // If response is not OK, try to get error message from JSON
            return response.json().then(errorData => {
                throw new Error(`API Error (${response.status}): ${errorData.error || response.statusText}`);
            }).catch(() => {
                // If error response is not JSON, throw with status text
                throw new Error(`API Error (${response.status}): ${response.statusText}`);
            });
        }
        return response.json();
    })
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