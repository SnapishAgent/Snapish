<template>
  <div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-else-if="weatherData" class="weather-container">
      <h3 class="weather-title">현재 날씨 정보</h3>
      
      <div v-if="weatherData.weather" class="weather-content">
        <!-- 일출/일몰 정보 -->
        <div class="time-box">
          <div class="time-item">
            <SunriseIcon class="icon" />
            <span>{{ weatherData.weather.sunrise }}</span>
          </div>
          <div class="time-item">
            <SunsetIcon class="icon" />
            <span>{{ weatherData.weather.sunset }}</span>
          </div>
        </div>

        <!-- 날씨 정보 그리드 -->
        <div class="info-box">
          <div class="info-item">
            <ThermometerIcon class="icon" />
            <span class="label">기온</span>
            <span class="value">{{ weatherData.weather.temp }}°C</span>
          </div>
          <div class="info-item">
            <DropletIcon class="icon" />
            <span class="label">습도</span>
            <span class="value">{{ weatherData.weather.humidity }}%</span>
          </div>
          <div class="info-item">
            <WindIcon class="icon" />
            <span class="label">풍속</span>
            <span class="value">{{ weatherData.weather.wind_speed }}m/s</span>
          </div>
          <div class="info-item">
            <CompassIcon class="icon" />
            <span class="label">풍향</span>
            <span class="value">{{ weatherData.weather.wind_deg }}</span>
          </div>
          <div class="info-item">
            <CloudIcon class="icon" />
            <span class="label">날씨</span>
            <span class="value">{{ weatherData.weather.weather }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="loading">
      날씨 정보를 불러오는 중...
    </div>
  </div>
</template>

<script>
import { fetchWeatherByCoordinates } from '@/services/weatherService';
import { 
  SunriseIcon, 
  SunsetIcon, 
  ThermometerIcon, 
  DropletIcon, 
  WindIcon, 
  CompassIcon, 
  CloudIcon 
} from 'lucide-vue-next';

export default {
  components: {
    SunriseIcon,
    SunsetIcon,
    ThermometerIcon,
    DropletIcon,
    WindIcon,
    CompassIcon,
    CloudIcon
  },
  props: {
    spotlocation: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      weatherData: null,
      error: null,
    };
  },
  watch: {
    spotlocation: {
      immediate: true,
      handler: 'fetchWeather',
    },
  },
  methods: {
    async fetchWeather() {
      if (this.spotlocation && this.spotlocation.length === 2) {
        try {
          this.error = null;
          this.weatherData = null;
          const [lat, lon] = this.spotlocation;
          this.weatherData = await fetchWeatherByCoordinates(lat, lon);
        } catch (error) {
          console.error('날씨 정보를 가져오는데 실패했습니다:', error);
          this.error = '날씨 정보를 가져오는데 실패했습니다.';
        }
      }
    },
  },
};
</script>

<style scoped>
.weather-container {
  padding: 16px;
}

.weather-title {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 12px;
}

.weather-content {
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.time-box {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-item span {
  font-size: 1.1rem;
  font-weight: 500;
}

.info-box {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  padding: 12px;
  gap: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.icon {
  width: 16px;
  height: 16px;
  color: #666;
}

.label {
  font-size: 0.75rem;
  color: #666;
}

.value {
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
}

.error-message {
  color: #dc3545;
  padding: 12px;
  font-size: 0.9rem;
}

.loading {
  padding: 12px;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}
</style>

  