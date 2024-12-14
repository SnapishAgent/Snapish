<template>
  <div>
    <div v-if="loading">정보를 가져오는 중...</div>
    <div v-if="weather && weather.location">
      <h2>{{ weather.location.name }}</h2>
      <p>기온 : {{ weather.current.temp_c }}°C</p>
      <p>지금은 {{ weather.current.condition.text }}</p>
      <p>업데이트 시각 : {{ weather.current.last_updated }}</p>
    </div>
    <div v-if="error">{{ error }}</div>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  computed: {
    ...mapState(["weather", "loading", "error", "lastupdated"]),
  },
  mounted() {
    if (this.shouldUpdateImmediately()) {
      this.updateWeather();
    }
    this.startAutoRefresh();
  },
  beforeUnmount() {
    if (this.autoRefreshInterval) clearInterval(this.autoRefreshInterval);
  },
  methods: {
    isWeatherDataStale() {
      if (!this.lastupdated) return true; // 업데이트 기록 없음

      const lastUpdate = new Date(this.lastupdated);
      const now = new Date();

      const diffMinutes = (now - lastUpdate) / 1000 / 60;
      console.log(`WeatherService.vue : Last update: ${lastUpdate}, Now: ${now}, Diff: ${diffMinutes} minutes`);

      // 미래 시간 감지
      if (diffMinutes < 0) {
        console.warn(`Future timestamp detected: ${lastUpdate}. Triggering data update.`);
        return true; // 갱신 필요
      }

      return diffMinutes > 10; // 10분 이상 경과 여부
    },

    shouldUpdateImmediately() {
      return !this.weather || this.isWeatherDataStale();
    },

    updateWeather() {
      console.log("WeatherService.vue : Fetching weather data...");
      this.$store.dispatch("fetchWeather");
    },

    startAutoRefresh() {
      if (this.autoRefreshInterval) return; // 중복 실행 방지

      this.autoRefreshInterval = setInterval(() => {
        if (this.isWeatherDataStale()) {
          console.log("Interval condition met: fetching new weather data...");
          this.updateWeather();
        }
      }, 600000); // 10분
    },
  },
};
</script>