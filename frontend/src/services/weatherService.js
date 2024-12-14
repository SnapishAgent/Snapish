const apiBaseUrl = process.env.VUE_APP_WEATHER_URL;

export async function fetchWeatherByCoordinates(lat, lon) {
  try {
    const response = await fetch(`${apiBaseUrl}?lat=${lat}&lon=${lon}`);
    if (!response.ok) throw new Error(`Error: ${response.status}`);
      const data = await response.json();
      console.log("weatherservice : Getweather")
    return data;
  } catch (error) {
      console.error("Error fetching weather data:", error);
    return { error: error.message };
  }
}