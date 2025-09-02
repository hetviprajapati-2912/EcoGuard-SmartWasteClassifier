// ========== 🧠 CHATBOT ==========
function sendChat() {
  const input = document.getElementById("chatInput").value.trim();
  const chatBox = document.getElementById("chatBox");

  if (input === "") return;

  chatBox.innerHTML += `<p><strong>You:</strong> ${input}</p>`;

  let reply = "🌿 Try reducing waste, using public transport, and conserving energy!";
  const lowerInput = input.toLowerCase();
  if (lowerInput.includes("plastic")) {
    reply = "♻️ Switch to reusable containers and avoid single-use plastics!";
  } else if (lowerInput.includes("solar")) {
    reply = "☀️ Solar panels reduce fossil fuel dependence and save energy long-term!";
  } else if (lowerInput.includes("water")) {
    reply = "💧 Try using low-flow taps and avoid water wastage while brushing!";
  }

  chatBox.innerHTML += `<p><strong>EcoBot:</strong> ${reply}</p>`;
  chatBox.scrollTop = chatBox.scrollHeight;
  document.getElementById("chatInput").value = "";
}

/// 🌍 Fetch Air Quality & Pollution Levels using Location
function fetchEnvironmentalData(lat, lon) {
  const openWeatherKey = 'YOUR_OPENWEATHER_API_KEY';  // Replace with your API Key
  const airVisualKey = 'YOUR_AIRVISUAL_API_KEY';      // Replace with your API Key

  const alertsContainer = document.getElementById("location-alerts");

  // Fetch air quality from OpenWeatherMap
  fetch(`https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${openWeatherKey}`)
    .then(response => response.json())
    .then(data => {
      const aqi = data.list[0].main.aqi;
      let airStatus = ['Good 😌', 'Fair 🙂', 'Moderate 😐', 'Poor 😷', 'Very Poor 😵'][aqi - 1];

      alertsContainer.innerHTML = `
        <p>📍 Coordinates: ${lat.toFixed(2)}, ${lon.toFixed(2)}</p>
        <p>🌬️ Air Quality Index: <strong>${aqi}</strong> — ${airStatus}</p>
        <p>💧 Water Alert: Use water wisely today! 💦</p>
        <p>🗑️ Waste Tip: Segregate your waste properly ♻️</p>
      `;
    })
    .catch(err => {
      alertsContainer.innerHTML = `<p class="text-red-500">Failed to load air quality data.</p>`;
    });
}

// 🌐 Geolocation
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    position => {
      fetchEnvironmentalData(position.coords.latitude, position.coords.longitude);
    },
    error => {
      document.getElementById("location-alerts").innerHTML = "<p class='text-red-500'>Geolocation permission denied.</p>";
    }
  );
} else {
  document.getElementById("location-alerts").innerHTML = "<p class='text-red-500'>Geolocation not supported.</p>";
}

// ========== 📦 ECO PRODUCT RECOMMENDER ==========
function loadProducts() {
  const productList = document.getElementById("productList");
  productList.innerHTML = "";

  const products = [
    {
      name: "Bamboo Toothbrush",
      link: "https://earthhero.com/products/bamboo-toothbrush",
      rating: "⭐ 4.5",
    },
    {
      name: "Reusable Metal Straw Kit",
      link: "https://ecosia.org/s/metal-straw-kit",
      rating: "⭐ 4.7",
    },
    {
      name: "Eco Reusable Grocery Bags",
      link: "https://www.amazon.in/eco-reusable-bags",
      rating: "⭐ 4.6",
    }
  ];

  products.forEach((prod) => {
    productList.innerHTML += `
      <div class="border p-3 rounded-lg bg-gray-100">
        <a href="${prod.link}" target="_blank" class="text-blue-700 font-semibold hover:underline">${prod.name}</a>
        <p class="text-sm text-gray-600">${prod.rating}</p>
      </div>
    `;
  });
}

// ========== 📍 REAL GEOLOCATION MAP WITH ECO LOCATIONS ==========
function initMap() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (position) {
        const userLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };

        const map = new google.maps.Map(document.getElementById("map"), {
          center: userLocation,
          zoom: 13
        });

        const userMarker = new google.maps.Marker({
          position: userLocation,
          map: map,
          title: "You are here",
          icon: "https://maps.google.com/mapfiles/ms/icons/green-dot.png"
        });

        const ecoLocations = [
          {
            name: "Green Market",
            lat: userLocation.lat + 0.005,
            lng: userLocation.lng + 0.005,
            type: "event"
          },
          {
            name: "Recycling Center",
            lat: userLocation.lat - 0.004,
            lng: userLocation.lng - 0.003,
            type: "center"
          },
          {
            name: "Tree Plantation Drive",
            lat: userLocation.lat + 0.002,
            lng: userLocation.lng - 0.006,
            type: "event"
          }
        ];

        ecoLocations.forEach(location => {
          const marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.name,
            icon: location.type === "center"
              ? "https://maps.google.com/mapfiles/ms/icons/blue-dot.png"
              : "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png"
          });

          const infoWindow = new google.maps.InfoWindow({
            content: `<strong>${location.name}</strong><br>Type: ${location.type}`
          });

          marker.addListener("click", () => {
            infoWindow.open(map, marker);
          });
        });
      },
      function () {
        handleLocationError(true);
      }
    );
  } else {
    handleLocationError(false);
  }
}

function handleLocationError(browserHasGeolocation) {
  alert(browserHasGeolocation
    ? "Geolocation service failed."
    : "Your browser doesn't support geolocation.");
}

// ========== 🔄 INIT ==========
window.onload = () => {
  loadProducts();
};

// ========== 📍 Manual City-Based Alerts ==========

function getGreenAlerts() {
  const city = document.getElementById("cityInput").value.trim();
  const output = document.getElementById("alertsOutput");

  if (!city) {
    output.innerHTML = "❗ Please enter a city.";
    return;
  }

  const apiKey = '575d1fd1ee02e7349da9a21bf494736a'; 

  fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}`)
    .then(res => res.json())
    .then(data => {
      if (!data.coord) {
        output.innerHTML = `❗ Could not find city: ${city}`;
        return;
      }

      const { lat, lon } = data.coord;

      fetch(`https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${apiKey}`)
        .then(res => res.json())
        .then(aqiData => {
          const aqi = aqiData.list[0].main.aqi;
          const airStatus = ['Good 😌', 'Fair 🙂', 'Moderate 😐', 'Poor 😷', 'Very Poor 😵'][aqi - 1];

          output.innerHTML = `
            <p>📍 Location: ${city}</p>
            <p>🌬️ Air Quality Index: <strong>${aqi}</strong> — ${airStatus}</p>
            <p>💧 Water Tip: Check for leaks and conserve water!</p>
            <p>🗑️ Waste Tip: Compost kitchen scraps for your plants 🪴</p>
          `;
        });
    })
    .catch(() => {
      output.innerHTML = `❗ Could not load data for ${city}`;
    });
}
async function getGreenAlerts() {
  const city = document.getElementById("cityInput").value.trim();
  const output = document.getElementById("alertsOutput");

  if (!city) {
    output.innerHTML = "Please enter a city name.";
    return;
  }

  const apiKey = 'YOUR_OPENWEATHER_API_KEY'; // Replace with your actual key
  const url = `https://api.openweathermap.org/data/2.5/air_pollution?appid=${apiKey}&q=${city}`;

  try {
    const geoRes = await fetch(`https://api.openweathermap.org/geo/1.0/direct?q=${city}&limit=1&appid=${apiKey}`);
    const geoData = await geoRes.json();
    
    if (!geoData.length) {
      output.innerHTML = "❌ Location not found.";
      return;
    }

    const { lat, lon } = geoData[0];

    const aqiRes = await fetch(`https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${apiKey}`);
    const aqiData = await aqiRes.json();

    const aqi = aqiData.list[0].main.aqi;

    let message = "";
    let level = "";
    if (aqi === 1) level = "Good 😊";
    else if (aqi === 2) level = "Fair 🙂";
    else if (aqi === 3) {
      level = "Moderate 😐";
      message = "— consider avoiding intense outdoor exercise.";
    }
    else if (aqi === 4) {
      level = "Poor 😷";
      message = "⚠️ Try to stay indoors and use masks.";
    }
    else if (aqi === 5) {
      level = "Very Poor ☠️";
      message = "⚠️ Dangerous air — avoid going outside.";
    }

    output.innerHTML = `⚠️ AQI in <strong>${city}</strong> is <strong>${aqi}</strong> (${level}) ${message}`;
  } catch (error) {
    console.error("Error fetching data:", error);
    output.innerHTML = "⚠️ Failed to fetch alerts. Please try again.";
  }
}
