<template>
  <div class="container">
    <div v-if="loading" class="loading">정보를 가져오는 중...</div>
    <div v-else-if="mulddae" class="content">
      <div class="left-panel">
        <span class="moon-icon">{{ getMoonIcon(mulddae.moon_phase) }}</span>
      </div>
      <div class="right-panel">
        <div class="date-info">
          <h1>{{ currentDate }}</h1>
          <h2>음력 {{ mulddae.lunar_date }}</h2>
        </div>
        <div class="mulddae-info">
          <h2>{{ mulddae.other }} / 서해 : {{ mulddae.seohae }}</h2>
        </div>
      </div>
    </div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="no-data">물때 정보를 불러오지 못했습니다.</div>
  </div>
</template>
  
  <script>
  import { mapState, mapActions } from "vuex";

  const moonPhaseIcons = {
    "new": "🌑",        // New Moon
    "waxing_crescent": "🌒", // Waxing Crescent
    "first_quarter": "🌓",   // First Quarter
    "waxing_gibbous": "🌔",  // Waxing Gibbous
    "full": "🌕",       // Full Moon
    "waning_gibbous": "🌖",  // Waning Gibbous
    "last_quarter": "🌗",    // Last Quarter
    "waning_crescent": "🌘"  // Waning Crescent
  };
  
  export default {
    computed: {
      ...mapState(["currentlocation", "loading", "error", "mulddae"]),
      currentDate() {
        return new Date().toISOString().split("T")[0];
      },
    },
    methods: {
      ...mapActions(["fetchMulddae"]),
      fetchTodayMulddae() {
        const today = new Date().toISOString().split("T")[0]; // 오늘 날짜 (YYYY-MM-DD 형식)
        this.fetchMulddae(today);
    },
    getMoonIcon(phase) {
      if (phase === 0) return moonPhaseIcons["new"];
      if (phase > 0 && phase < 0.25) return moonPhaseIcons["waxing_crescent"];
      if (phase === 0.25) return moonPhaseIcons["first_quarter"];
      if (phase > 0.25 && phase < 0.5) return moonPhaseIcons["waxing_gibbous"];
      if (phase === 0.5) return moonPhaseIcons["full"];
      if (phase > 0.5 && phase < 0.75) return moonPhaseIcons["waning_gibbous"];
      if (phase === 0.75) return moonPhaseIcons["last_quarter"];
      if (phase > 0.75 && phase < 1) return moonPhaseIcons["waning_crescent"];
      return "❓"; // Unknown phase
    },
    mounted() {
      this.fetchTodayMulddae(); // 컴포넌트 로드 시 오늘 날짜로 물때 정보 요청
    },
    }
  };
  </script>
  <style scoped>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 20px;
  }
  
  .loading, .error, .no-data {
    font-size: 1.5em;
    color: #888;
    text-align: center;
  }
  
  .content {
    display: flex;
    width: 100%;
    max-width: 800px;
    gap: 20px;
  }
  
  .left-panel {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .right-panel {
    flex: 2;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  .moon-icon {
    font-size: 4em;
  }
  
  .date-info {
    text-align: center;
  }
  
  .mulddae-info {
    margin-top: 10px;
    text-align: center;
  }
  </style>
  