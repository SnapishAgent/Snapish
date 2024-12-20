import axios from 'axios';

const apiWeatherBaseUrl = process.env.VUE_APP_WEATHER_URL;

export async function fetchWeatherByCoordinates(lat, lon) {
  try {
    const response = await axios.post(
      apiWeatherBaseUrl,
      new URLSearchParams({ lat: lat, lon: lon }).toString(),
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching weather data:", error);
    return { error: error.message };
  }
}