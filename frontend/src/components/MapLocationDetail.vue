<template>
  <div class="fixed inset-0 z-50 flex justify-center max-w-md mx-auto">
    <!-- 배경 오버레이 -->
    <div class="absolute inset-0 bg-black bg-opacity-50" @click="$emit('close')"></div>
    
    <!-- 상세 정보 컨테이너 -->
    <div class="relative w-full bg-white h-full overflow-y-auto content-scroll">
      <!-- 헤더 영역 -->
      <header class="sticky top-0 bg-white z-10 px-4 py-3 border-b">
        <div class="flex justify-between items-center">
          <h1 class="text-xl font-bold">{{ location.name }}</h1>
          <button class="close-btn" @click="$emit('close')">
            <XIcon class="w-6 h-6" />
          </button>
        </div>
      </header>

      <!-- 기본 정보 영역 -->
      <section class="info-section p-4">
        <!-- 위치 정보 토글 -->
        <div class="location-toggle">
          <button @click="toggleLocation" 
                  class="w-full py-3 flex justify-between items-center">
            <div>
              <h3 class="flex items-center gap-2 text-lg font-semibold">
                <MapPinIcon class="w-5 h-5" /> 
                위치
              </h3>
              <p class="text-sm text-gray-600 mt-1">
                {{ location.address_road || location.address_land }}
              </p>
            </div>
            <ChevronDownIcon :class="['w-5 h-5 transition-transform', { 'rotate-180': isLocationOpen }]" />
          </button>
          
          <div class="facility-content mt-2">
            <div v-if="mapLoaded">
              <MapComponent 
                v-show="isLocationOpen" 
                :locations="[location]" 
                mapType="B" 
              />
            </div>
          </div>
        </div>

        <!-- 시설 정보 토글 -->
        <div class="facility-toggle mt-4 border-t">
          <button @click="toggleFacilities" 
                  class="w-full py-3 flex justify-between items-center">
            <h3 class="flex items-center gap-2 text-lg font-semibold">
                <FishIcon class="w-5 h-5" /> 
                시설 정보
              </h3>
            <ChevronDownIcon :class="['w-5 h-5 transition-transform', { 'rotate-180': isFacilitiesOpen }]" />
          </button>
          
          <div v-if="isFacilitiesOpen" class="space-y-4">
            <p style="font-size: 0.7rem;">
              출처 : LOCALDATA (2024.12월 기준) 
            </p>
            <!-- 이용료 섹션 -->
            <div class="facility-section" v-if="location.usage_fee">
              <h3 class="flex items-center gap-2 text-lg font-semibold">
                <WalletIcon class="w-5 h-5" />
                이용료
              </h3>
              <div class="facility-content mt-2">
                {{ location.usage_fee }}
              </div>
            </div>

            <!-- 주요어종 섹션 -->
            <div class="facility-section" v-if="location.main_fish_species">
              <h3 class="flex items-center gap-2 text-lg font-semibold">
                <FishIcon class="w-5 h-5" />
                주요 어종
              </h3>
              <div class="facility-tags mt-2">
                <span v-for="species in location.main_fish_species.split(/[+,]/).filter(Boolean)"
                      :key="species"
                      class="inline-block px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm mr-2 mb-2">
                  {{ species.trim() }}
                </span>
              </div>
            </div>

            <!-- 안전시설 섹션 -->
            <div class="facility-section" v-if="location.safety_facilities">
              <h3 class="flex items-center gap-2 text-lg font-semibold">
                <ShieldCheckIcon class="w-5 h-5" />
                안전 시설
              </h3>
              <div class="facility-tags mt-2">
                <span v-for="facility in location.safety_facilities.split(/[+,]/).filter(Boolean)"
                      :key="facility"
                      class="inline-block px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm mr-2 mb-2">
                  {{ facility.trim() }}
                </span>
              </div>
            </div>

            <!-- 편의시설 섹션 -->
            <div class="facility-section" v-if="location.convenience_facilities">
              <h3 class="flex items-center gap-2 text-lg font-semibold">
                <Coffee class="w-5 h-5" />
                편의시설
              </h3>
              <div class="facility-tags mt-2">
                <span v-for="facility in location.convenience_facilities.split(/[+,]/).filter(Boolean)"
                      :key="facility"
                      class="inline-block px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-sm mr-2 mb-2">
                  {{ facility.trim() }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 날씨 정보 토글 -->
        <div class="weather-toggle mt-4 border-t">
          <button @click="toggleWeather" 
                  class="w-full py-3 flex justify-between items-center">
            <h3 class="flex items-center gap-2 text-lg font-semibold">
              <CloudIcon class="w-5 h-5" /> 
              날씨 정보
            </h3>
            <ChevronDownIcon :class="['w-5 h-5 transition-transform', { 'rotate-180': isWeatherOpen }]" />
          </button>
          
          <div v-if="isWeatherOpen">
            <div v-if="weatherLoaded">
              <MapLocationWeatherLand 
                :spotlocation="[location.latitude, location.longitude]"
                v-model:weatherData="weatherData.land"
              />
            </div>
            <div v-if="weatherLoaded && location.type === '바다'">
              <MapLocationWeatherSea 
                :spotlocation="[location.latitude, location.longitude]"
                v-model:weatherData="weatherData.sea"
                @update:observationInfo="updateObservationInfo"
              />
              
              <!-- 관측소 정보 표시 -->
              <div v-if="observationInfo" class="mt-1">
                <div class="space-y-1">
                  <p v-if="observationInfo.tideStation" class="text-xs">
                    조석예보 기준 관측소: <strong>{{ observationInfo.tideStation }}</strong>
                    | <strong>{{ observationInfo.tideDistance?.toFixed(3) }} km</strong> 거리
                  </p>
                  <p class="text-xs">
                    실시간 바다 날씨 기준 관측소: <strong>{{ observationInfo.weatherStation }}</strong>
                    | <strong>{{ observationInfo.weatherDistance?.toFixed(3) }} km</strong> 거리
                  </p>
                </div>
              </div>
            </div>
            <!-- 출처 및 주의사항 -->
            <div class="mt-2">
              <p style="font-size: 0.65rem;" class="text-gray-500">
                출처 : {{ observationInfo ? '바다누리 해양정보 서비스 | ' : '' }}openweathermap.org 
              </p>
              <p style="font-size: 0.65rem;" class="text-gray-500">
                실시간 측정 API 특성상 일부 데이터에 <strong>결측</strong>이 있을 수 있습니다.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
// import { ref } from 'vue';
import { 
  XIcon, 
  MapPinIcon, 
  WalletIcon, 
  FishIcon, 
  ShieldCheckIcon,
  Coffee,
  CloudIcon,
  ChevronDownIcon
} from 'lucide-vue-next';
import MapLocationWeatherSea from './MapLocationWeatherSea.vue';
import MapLocationWeatherLand from './MapLocationWeatherLand.vue';
import MapComponent from './MapComponent.vue';

export default {
  name: 'MapLocationDetail',
  components: {
    MapLocationWeatherSea,
    MapLocationWeatherLand,
    MapComponent,
    XIcon,
    MapPinIcon,
    WalletIcon,
    FishIcon,
    ShieldCheckIcon,
    Coffee,
    CloudIcon,
    ChevronDownIcon
  },
  props: {
    location: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isLocationOpen: false,
      isFacilitiesOpen: false,
      isWeatherOpen: false,
      weatherData: {
        sea: null,
        land: null
      },
      weatherLoaded: false,
      mapLoaded: false,
      observationInfo: null
    }
  },
  methods: {
    toggleLocation() {
      this.isLocationOpen = !this.isLocationOpen;
    },
    toggleFacilities() {
      this.isFacilitiesOpen = !this.isFacilitiesOpen;
    },
    toggleWeather() {
      this.isWeatherOpen = !this.isWeatherOpen;
    },
    updateObservationInfo(info) {
      this.observationInfo = info;
    }
  },
  watch: {
    isLocationOpen(newValue) {
      if (newValue && !this.mapLoaded) {
        this.mapLoaded = true;
      }
    },
    isWeatherOpen(newValue) {
      if (newValue && !this.weatherLoaded) {
        this.weatherLoaded = true;
      }
    }
  }
}
</script>

<style scoped>
/* 사용되지 않는 스타일 제거 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #CBD5E0 transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #CBD5E0;
  border-radius: 3px;
}

/* content-scroll 클래스는 template에서 사용중이므로 유지 */
.content-scroll {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 60px;
}

/* 필요한 스타일만 유지 */
.rotate-180 {
  transform: rotate(180deg);
}

.facility-section {
  padding-bottom: 0.75rem;
}

.facility-content {
  margin-top: 0.25rem;
}

.facility-tags {
  margin-top: 0.25rem;
}
</style>