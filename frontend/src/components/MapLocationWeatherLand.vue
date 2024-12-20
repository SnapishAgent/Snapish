<template>
  <div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-else-if="localWeather" class="weather-container">
      <h3>현재 날씨 정보</h3>
      
      <div v-if="localWeather.weather" class="weather-content">
        <!-- 일출/일몰 정보 -->
        <div class="time-box">
          <div class="time-item">
            <SunriseIcon class="icon" />
            <span>{{ localWeather.weather.sunrise }}</span>
          </div>
          <div class="time-item">
            <SunsetIcon class="icon" />
            <span>{{ localWeather.weather.sunset }}</span>
          </div>
        </div>

        <!-- 날씨 정보 그리드 -->
        <div class="info-box">
          <div class="info-item">
            <ThermometerIcon class="icon" />
            <span class="label">기온</span>
            <span class="value">{{ localWeather.weather.temp }} <span class="unit">°C</span></span>
          </div>
          <div class="info-item">
            <DropletIcon class="icon" />
            <span class="label">습도</span>
            <span class="value">{{ localWeather.weather.humidity }} <span class="unit">%</span></span>
          </div>
          <div class="info-item">
            <WindIcon class="icon" />
            <span class="label">풍속</span>
            <span class="value">{{ localWeather.weather.wind_speed }} <span class="unit">m/s</span></span>
          </div>
          <div class="info-item">
            <CompassIcon class="icon" />
            <span class="label">풍향</span>
            <span class="value">{{ localWeather.weather.wind_deg }} </span>
          </div>
          <div class="info-item">
            <CloudIcon class="icon" />
            <span class="label">날씨</span>
            <span class="value">{{ localWeather.weather.weather }}</span>
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
    weatherData: Object,
  },
  emits: ['update:weatherData'],
  data() {
    return {
      localWeather: null,
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
        if (this.weatherData) {
          this.localWeather = this.weatherData;
          return;
        }

        try {
          this.error = null;
          const [lat, lon] = this.spotlocation;
          const response = await fetchWeatherByCoordinates(lat, lon);
          this.localWeather = response;
          this.$emit('update:weatherData', response);
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
h3 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.weather-container {
  padding: 16px 0;
  width: 100%;
  box-sizing: border-box;
}

.weather-content {
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
  width: 100%;
}

.time-box {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(to right, 
    rgba(255, 236, 179, 0.2), /* 일출: 밝은 노란색 */
    rgba(255, 148, 148, 0.2)  /* 일몰: 붉은색 */
  );
  border-bottom: 1px solid #eee;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 6px;
  background: transparent;
}

.time-item span {
  font-size: 1.1rem;
  font-weight: 500;
}

.info-box {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  padding: 16px;
  gap: 12px;
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

.unit {
  font-size: 0.7rem;
}
</style>

  