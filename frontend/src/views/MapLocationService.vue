<template>
  <div class="min-h-screen bg-gray-100 flex justify-center">
    <div class="w-full max-w-4xl bg-white shadow-lg overflow-hidden parent-container">
      <main class="pb-20 px-4">
        <section class="mb-3 pt-6">
          <div id="top-map">
            <!-- 버튼 추가 -->
            <button @click="toggleMapComponent" class="show-map-btn">
              전체 위치
            </button>
            <div v-if="isMapVisible && locations.length > 0" class="map-container">
              <MapComponent :locations="locations"></MapComponent>
            </div>
          </div>

          <div id="searchbar">
            <input v-model="searchQuery" type="text" placeholder="원하는 낚시터 이름을 넣어주세요" key="search-input"
              class="form-control search-input" @input="filterLocations" />
          </div>
        </section>
        <br />

        <section class="mb-3">
          <div id="middle-list" :style="{
            maxHeight: `${dynamicMaxHeight}px`,
            overflowY: 'scroll',
            paddingRight: '10px'
          }">
            <div>
              <ul class="location-list">
                <li v-for="(location, index) in filteredLocations" :key="index" class="location-item"
                  @click="showDetails(location)">
                  <h3> {{ location.name }} <strong>{{ location.type }}</strong></h3>
                  <p v-if="location.address_road && location.address_land">
                    {{ location.address_road }}
                  </p>
                  <p v-else-if="location.address_road">
                    {{ location.address_road }}
                  </p>
                  <p v-else-if="location.address_land">
                    {{ location.address_land }}
                  </p>
                </li>
              </ul>
            </div>
          </div>

          <div class="slide-up-panel" :class="{ visible: isDetailsVisible }" @click.self="hideDetails">
            <MapLocationDetail v-if="isDetailsVisible" :location="selectedLocation" @close="hideDetails" />
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script>
import axios from "@/axios";
import MapComponent from '@/components/MapComponent.vue'
import MapLocationDetail from '@/components/MapLocationDetail.vue'

export default {
  components: {
    MapComponent,
    MapLocationDetail,
  },
  data() {
    return {
      searchQuery: "", // 검색 입력값
      filteredLocations: [],
      locations: [], // DB에서 위치 데이터를 저장할 배열 - 임시 데이터 넣어둠
      isMapVisible: false, // 지도 표시 여부
      selectedLocation: null, // 선택된 낚시터 데이터
      isDetailsVisible: false, // 상세 정보 슬라이드 표시 여부
      dynamicMaxHeight: window.innerHeight,
      bodyScrollEnabled: true,
    };
  },
  mounted() {
    this.fetchLocations();     // 컴포넌트가 마운트된 후에 DB에서 위치 정보 가져오기
    this.filteredLocations = this.locations; // 초기에는 모든 locations를 표시
    this.updateMaxHeight();     // 페이지 드래그 방지 및 스크롤 숨김 설정
    this.toggleBodyScroll(false);     // 페이지 드래그 방지 및 스크롤 숨김 설정
    window.addEventListener("resize", this.updateMaxHeight); // 화면 크기 변화 감지
  },
  beforeUnmount() {
    // 컴포넌트 제거 시 스크롤 복원
    this.toggleBodyScroll(true);
    window.removeEventListener("resize", this.updateMaxHeight); // 이벤트 제거
  },
  methods: {
    filterLocations() {
      const query = this.searchQuery.trim();
      if (query === "") {
        this.filteredLocations = [...this.locations]; // 모든 데이터 표시
      } else {
        this.filteredLocations = this.locations.filter((location) =>
          String(location.name || "").includes(query)
        );
      }
    },
    updateMaxHeight() {
      const headerHeight = 240;
      const footerHeight = 100;
      const availableHeight = window.innerHeight - headerHeight - footerHeight;
      this.dynamicMaxHeight = Math.max(availableHeight, 300);
    },
    toggleBodyScroll(enable) {
      this.bodyScrollEnabled = enable;
      document.body.style.overflow = enable ? "auto" : "hidden";
    },
    showDetails(location) {
      this.selectedLocation = location;
      this.isDetailsVisible = true;
    },
    hideDetails() {
      this.selectedLocation = null;
      this.isDetailsVisible = false;
    },
    toggleMapComponent() {
      this.isMapVisible = !this.isMapVisible;
    },
    // DB에서 위치 정보 가져오기, 주소 고정값 추후 해결
    async fetchLocations() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/map_fishing_spot');
        if (response.data.location) {
          const locationDict = response.data.location; // 딕셔너리
          this.locations = Object.values(locationDict); // 딕셔너리 값을 배열로 변환
          this.filteredLocations = [...this.locations]; // 초기 필터링 배열 설정
          console.log(this.locations)
        }
      } catch (error) {
        console.error('Error fetching locations:', error);
      }
    },

  }
};
</script>

<style scoped>
.parent-container {
  position: relative;
  /* 부모 컨테이너 기준점 */
  overflow: hidden;
  /* 부모 밖으로 나가는 요소 숨김 */
}

#top-map {
  display: right;
  /* flex-direction: column; 요소들을 세로로 배치 */
  gap: 5px;
  /* 요소 간격 설정 */
  margin-bottom: 0;
  /* 아래 여백 제거 */
}

#searchbar {
  margin-top: 100px;
}

/* 버튼 스타일 */
.show-map-btn {
  margin: 0;
  padding: 8px 16px;
  background-color: #45a049;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  font-size: 12px;
}

.show-map-btn:hover {
  background-color: #3d8e41;
}

/* 지도 컨테이너 */
.map-container {
  position: absolute;
  top: 75px;
  left: 0;
  width: 100%;
  height: 75%;
  background-color: white;
  z-index: 10;
  /* box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); */
  /* border-bottom: 1px solid #ddd; */
}

/* 리스트 스타일 */
.location-item {
  border-bottom: 1px solid #ccc;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

/* 슬라이드 패널 */
.slide-up-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 90%;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  transform: translateY(100%);
  /* 기본 상태 */
  transition: transform 0.3s ease-in-out;
  /* 애니메이션 추가 */
  z-index: 10;
}

.slide-up-panel.visible {
  transform: translateY(0);
  /* 보이는 상태 */
}

.details-content {
  padding: 20px;
  overflow-y: auto;
  max-height: 100%;
}

/* 검색바 */
#searchbar {
  display: flex;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.search-btn {
  padding: 5px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}

.search-btn:hover {
  background-color: #0056b3;
}
</style>