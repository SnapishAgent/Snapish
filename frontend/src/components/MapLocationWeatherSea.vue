 <template>
  <div style="display: flex; flex-direction: column; gap: 1rem;">
    <!-- Loading State -->
    <div v-if="isLoading">
      <p style="font-size: 0.8rem; text-align: center;">데이터를 불러오는 중입니다...</p>
    </div>

    <!-- Data Loaded State -->
    <div v-else-if="obsrecent">
      <!-- Table Section -->
      <div class="data-table" style="display: flex; gap: 2rem;">
        <!-- Tide Forecast -->
        <div style="flex: 1;">
          <h3>조석예보</h3>
          <table class="tide-pre-tab">
            <thead>
              <tr>
                <th colspan="3">{{ getCurrentDate() }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in obspretab?.api_response" :key="index">
                <td>{{ item?.tph_time?.split(' ')[1]?.slice(0, 5) }}</td>
                <td :class="{ 'high-tide': item.hl_code === '고조', 'low-tide': item.hl_code === '저조' }">
                  {{ item.hl_code }}
                </td>
                <td>{{ item.tph_level }} cm</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Real-Time Observations -->
        <div style="flex: 1;">
          <h3>실시간 날씨 예보</h3>
          <table class="tide-pre-tab">
            <thead>
              <tr>
                <th colspan="2">
                  {{ obsrecent?.api_response?.record_time?.split(' ')[1]?.slice(0, 5) || '-' }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>수온</td>
                <td>{{ obsrecent?.api_response?.water_temp ?? '-' }}°C</td>
              </tr>
              <tr>
                <td>기온</td>
                <td>{{ obsrecent?.api_response?.air_temp ?? '-' }}°C</td>
              </tr>
              <tr>
                <td>기압</td>
                <td>{{ obsrecent?.api_response?.air_press ?? '-' }}hPa</td>
              </tr>
              <tr>
                <td>조위</td>
                <td>{{ obsrecent?.api_response?.tide_level ?? '-' }}cm</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <!-- Location Info -->
        <div>
          <p v-if="obspretab?.api_response" style="font-size: 0.8rem;">
            조석예보 기준 관측소: <strong>{{ obspretab.obs_post_name }}</strong>
            | <strong>{{ obspretab.distance?.toFixed(3) }} km</strong> 거리
          </p>
          <p style="font-size: 0.8rem;">
            실시간 날씨 예보 기준 관측소: <strong>{{ obsrecent.obs_post_name }}</strong>
            | <strong>{{ obsrecent.distance?.toFixed(3) }} km</strong> 거리
          </p>
          <p style="font-size: 0.7rem;">
            출처 : 바다누리 해양정보 서비스 | 실시간 특성상 일부 데이터에 <strong>결측</strong>이 있을 수 있습니다.
          </p>
        </div>
    </div>

    <!-- Error State -->
    <div v-else>
      <p style="font-size: 0.8rem; text-align: center; color: red;">데이터를 불러오는 데 실패했습니다.</p>
    </div>
  </div>
</template>

<script>
import { fetchSeaPostidByCoordinates } from '../services/locationService';

export default {
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
      obsrecent: null,
      obspretab: null,
      isLoading: true,
    };
  },
  mounted() {
    this.fetchWeatherData();
  },
  methods: {
    async fetchWeatherData() {
      if (this.weatherData) {
        const { obsrecent, obspretab } = this.weatherData;
        this.obsrecent = obsrecent;
        this.obspretab = obspretab;
        this.isLoading = false;
        return;
      }

      try {
        const [lat, lon] = this.spotlocation;
        console.log(lat, lon)
        const response = await fetchSeaPostidByCoordinates(lat, lon);
        const { obsrecent, obspretab } = response;
        this.obsrecent = obsrecent;
        this.obspretab = obspretab;
        this.$emit('update:weatherData', { obsrecent, obspretab });
      } catch (error) {
        console.error('Error fetching weather data:', error);
      } finally {
        this.isLoading = false;
      }
    },

    getCurrentDate() {
      const now = new Date();
      return now.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    },
  },
};
</script>

<style scoped>
.data-table {
  margin: 1rem 0;
}

.tide-pre-tab {
  width: 100%;
  border-collapse: collapse;
  font-size: 1rem;
}

.tide-pre-tab th, .tide-pre-tab td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

.tide-pre-tab th {
  background-color: #f4f4f4;
  font-weight: bold;
  text-transform: uppercase;
}

.tide-pre-tab tr:nth-child(even) {
  background-color: #f9f9f9;
}

.tide-pre-tab tr:hover {
  background-color: #f1f1f1;
}

.table-container {
  max-width: 100%;
  overflow-x: auto;
}

h3 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

p {
  font-size: 1rem;
  color: #555;
}

.high-tide {
  background-color: #e6f3ff;  /* 파란 배경 */
}

.low-tide {
  background-color: #ffe6e6;  /* 붉은 배경 */
}

.tide-pre-tab th {
  background-color: #f4f4f4;
  font-weight: bold;
  text-align: center;
  padding: 10px;
}
</style>
