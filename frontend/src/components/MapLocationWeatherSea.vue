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
                <td>{{ item.tph_level }} <span class="unit">cm</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Real-Time Observations -->
        <div style="flex: 1;">
          <h3>실시간 바다 날씨</h3>
          <table class="tide-pre-tab">
            <thead>
              <tr>
                <th colspan="2">
                  {{ obsrecent?.api_response?.record_time?.split(' ')[1]?.slice(0, 5) || '-' }}
                  기준 측정
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>수온</td>
                <td>{{ obsrecent?.api_response?.water_temp ?? '-' }} <span class="unit">°C</span></td>
              </tr>
              <tr>
                <td>기온</td>
                <td>{{ obsrecent?.api_response?.air_temp ?? '-' }} <span class="unit">°C</span></td>
              </tr>
              <tr>
                <td>기압</td>
                <td>{{ obsrecent?.api_response?.air_press ?? '-' }} <span class="unit">hPa</span></td>
              </tr>
              <tr>
                <td>조위</td>
                <td>{{ obsrecent?.api_response?.tide_level ?? '-' }} <span class="unit">cm</span></td>
              </tr>
            </tbody>
          </table>
        </div>
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
  emits: ['update:weatherData', 'update:observationInfo'],
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
        
        // 관측소 정보 전달
        this.$emit('update:observationInfo', {
          tideStation: obspretab?.obs_post_name,
          tideDistance: obspretab?.distance,
          weatherStation: obsrecent?.obs_post_name,
          weatherDistance: obsrecent?.distance
        });
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
/* 중복되는 스타일 통합 */
.tide-pre-tab {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
}

.tide-pre-tab th, 
.tide-pre-tab td {
  padding: 12px;
  text-align: center;
  border: none;
  border-bottom: 1px solid #eee;
  font-size: 0.9rem;  /* td에만 있던 스타일을 통합 */
}

.tide-pre-tab th {
  background-color: #f0f0f0;
  font-weight: bold;
  color: #333;
}

.tide-pre-tab tr {
  background-color: #f8f8f8;
}

.tide-pre-tab tr:last-child td {
  border-bottom: none;
}

/* 나머지 스타일은 그대로 유지 */
.data-table {
  margin: 1rem 0;
}

h3 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  font-weight: bold;
  color: #495057;
}

.high-tide {
  background-color: #e6f3ff;
}

.low-tide {
  background-color: #ffe6e6;
}

.unit {
  font-size: 0.7rem;
}
</style>
