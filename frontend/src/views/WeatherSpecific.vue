<template>
  <div>
    <h1>임시페이지</h1>
    <!-- <div v-if="loading">로딩 중...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="weather">
      <h2>현재 날씨 정보</h2>
      <p>{{ weather }}</p>
    </div>
    <div v-else>날씨 정보를 불러올 수 없습니다.</div> -->
  </div>
</template>

<script>
export default {
//   computed: {
//     ...mapState(["weather", "loading", "error", "lastupdated"]),
//   },
//   methods: {
//     ...mapActions(["fetchWeather"]),
//     isWeatherDataStale() {
//       // console.log(this.lastupdated)
//       if (!this.lastupdated) return true;

//       const lastUpdate = new Date(this.lastupdated);
//       const now = new Date();
//       const diffMinutes = (now - lastUpdate) / 1000 / 60;
//       return diffMinutes > 10; // 10분 이상 차이
//     },
//   },
//   mounted() {
//     // lastupdated 기준으로 필요할 때만 fetchWeather 호출
//     if (!this.weather || this.isWeatherDataStale()) {
//       this.fetchWeather();
//     } else {
//       console.log("날씨 정보가 최신 상태입니다. API 호출 생략.");
//     }
//   },
};
</script>