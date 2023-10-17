// Create the Leaflet map
var map = L.map('mapid').setView([41.003799, -73.791214], 12);

// Add the tile layer to the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

// Get the locations from the data-location attributes of the anchor tags
var locations = Array.from(document.querySelectorAll('#locations a')).map(a => a.getAttribute('data-location'));

// Object to store the markers
var markers = {};

// Function to geocode a place name
function geocode(place) {
    return fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(place))
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                console.log('Geocoded location:', place, 'Coordinates:', [data[0].lat, data[0].lon]);  // Add this line
                markers[place] = L.marker([data[0].lat, data[0].lon]).addTo(map).bindPopup(place);
            } else {
                console.log('Could not geocode location:', place);  // Add this line
            }
        });
}


// Add a marker for each location
Promise.all(locations.map(geocode)).then(function () {
    // Add the mouseover event listeners to the anchor tags
    var anchors = document.querySelectorAll('#locations a');
    for (var i = 0; i < anchors.length; i++) {
        anchors[i].addEventListener('mouseover', function (e) {
            // Get the anchor tag element
            var anchor = e.currentTarget;
        
            // Get the location from the data-location attribute
            var location = anchor.getAttribute('data-location');
        
            // Find the corresponding marker and open its popup
            var marker = markers[location];
            if (marker) {
                marker.openPopup();
            }
        });
        
    }
});

