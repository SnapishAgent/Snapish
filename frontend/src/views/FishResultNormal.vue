<template>
  <div class="min-h-screen bg-white flex flex-col">
    <!-- 헤더 -->
    <header
      class="fixed top-0 left-0 right-0 bg-white px-4 py-3 flex items-center justify-between border-b z-15 max-w-md mx-auto">
      <div class="flex items-center">
        <button class="mr-2" @click="goBack">
          <ChevronLeftIcon class="w-6 h-6" />
        </button>
        <h1 class="text-xl font-bold">물고기 판별 결과</h1>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2">
          <BellIcon class="w-6 h-6" />
        </button>
        <button class="p-2">
          <Settings2Icon class="w-6 h-6" />
        </button>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="flex-1 pb-20 px-4 overflow-auto max-w-md mx-auto">
      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <span class="text-gray-500">로딩 중...</span>
      </div>

      <!-- 에러 메시지 -->
      <div v-if="errorMessage" class="p-4 bg-red-100 text-red-600 rounded-lg">
        {{ errorMessage }}
      </div>

      <!-- 업로드된 물고기 이미지 표시 -->
      <div v-if="!isLoading && !errorMessage" class="mt-4 bg-gray-200 rounded-lg p-4 flex justify-center">
        <img :src="imageSource" alt="물고기 사진" class="w-full h-full object-cover cursor-pointer"
          @click="openImagePopup(imageSource)" />
      </div>

      <!-- AI 판별 결과 -->
      <div v-if="!isLoading && !errorMessage" class="mt-6 bg-blue-50 rounded-lg p-4">
        <h2 class="text-lg font-bold text-blue-700 mb-2">AI 판별 결과</h2>
        <template v-if="parsedDetections.length > 0">
          <p class="text-blue-600" v-if="parsedDetections[0].label !== '알 수 없음'">
            이 물고기는 <strong>{{ parsedDetections[0].label }}</strong>입니다.
            <span :class="[
              'text-sm',
              getConfidenceColor(parsedDetections[0].confidence)
            ]">
              신뢰도: {{ (parsedDetections[0].confidence * 100).toFixed(2) }}%
            </span>
          </p>
          <p class="text-blue-600" v-else>
            이 물고기는 <strong>알 수 없음</strong>으로 판별되었습니다.
          </p>

          <p class="text-sm text-blue-600 mt-2"
            v-if="parsedDetections.length > 1 && parsedDetections[0].label !== '알 수 없음'">
            다른 후보:
            <span class="text-blue-500">
              <span v-for="(detection, index) in parsedDetections.slice(1)" :key="index">
                {{ detection.label }}
                <span :class="[
                  'text-sm',
                  getConfidenceColor(detection.confidence)
                ]">
                  (신뢰도: {{ (detection.confidence * 100).toFixed(2) }}%)
                </span>
                {{ index < parsedDetections.slice(1).length - 1 ? ', ' : '' }} </span>
              </span>
          </p>
        </template>
        <template v-else>
          <p class="text-blue-600">
            예측 결과가 존재하지 않습니다.
          </p>
        </template>
      </div>

      <!-- 공유하기 버튼 -->
      <div v-if="!isLoading && !errorMessage" class="mt-6">
        <button class="w-full bg-green-500 text-white py-3 px-4 rounded-lg flex items-center justify-center"
          @click="shareResult">
          <Share2Icon class="w-5 h-5 mr-2" />
          <span>공유하기</span>
        </button>
      </div>

      <!-- 내가 잡은 물고기 페이지로 이동 버튼 -->
      <div v-if="!isLoading && !errorMessage" class="mt-4">
        <button class="w-full bg-blue-500 text-white py-3 px-4 rounded-lg flex items-center justify-center"
          @click="navigateToCatches">
          <span>내가 잡은 물고기 리스트 보기</span>
        </button>
      </div>
    </main>

    <!-- 포토카드 모달 -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 w-10/12 max-w-sm">
        <h2 class="text-lg font-bold mb-4 text-center">나만의 포토카드</h2>
        <div ref="photocard" class="bg-gray-100 p-4 rounded-lg overflow-auto">
          <img :src="imageUrl" alt="물고기 사진" class="w-full h-64 object-contain rounded-lg" />
          <h3 class="text-md font-semibold mt-4 text-center">{{ parsedDetections[0].label }}</h3>
          <p class="text-center text-sm">신뢰도: {{ (parsedDetections[0].confidence * 100).toFixed(2) }}%</p>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="closeModal" class="px-4 py-2 bg-gray-300 rounded">닫기</button>
          <button @click="downloadPhotocard" class="px-4 py-2 bg-blue-500 text-white rounded">저장하기</button>
        </div>
      </div>
    </div>

    <!-- 이미지 팝업 -->
    <div v-if="isImagePopupVisible" class="fixed inset-0 bg-black bg-opacity-75 flex justify-center items-center z-30"
      @click="isImagePopupVisible = false">
      <div class="relative max-w-full max-h-full" @click.stop>
        <img :src="popupImageUrl" alt="Popup Image"
          class="w-full h-full object-contain rounded-lg border border-gray-200 shadow-lg" />
        <button @click="isImagePopupVisible = false"
          class="absolute top-2 right-2 bg-white text-black rounded-full p-1 hover:bg-gray-200 transition-colors duration-300">
          &times;
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from '../axios';
import html2canvas from 'html2canvas';
import { ChevronLeftIcon, BellIcon, Settings2Icon, Share2Icon } from 'lucide-vue-next';
import store from '../store';

const isLoading = ref(true);
const errorMessage = ref('');
const parsedDetections = ref([]);
const imageUrl = ref('');
const imageBase64 = ref('');
const route = useRoute();
const router = useRouter();

// Define the missing variables
const showModal = ref(false);
const photocard = ref(null);
const popupImageUrl = ref('');
const isImagePopupVisible = ref(false);

const fetchDetections = async () => {
  isLoading.value = true;
  try {
    const token = localStorage.getItem('token');
    if (token && route.query.imageUrl) {
      const response = await axios.get('/backend/get-detections', {
        params: {
          imageUrl: route.query.imageUrl,
        },
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      parsedDetections.value = response.data.detections;
      imageUrl.value = response.data.imageUrl;
    } else {
      parsedDetections.value = JSON.parse(decodeURIComponent(route.query.detections));
      imageBase64.value = route.query.imageBase64;
    }
    errorMessage.value = '';
  } catch (e) {
    console.error('Failed to fetch detections:', e);
    errorMessage.value = '예측 결과를 불러오는 데 실패했습니다.';
    parsedDetections.value = [];
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchDetections();
});

watch(route, () => {
  fetchDetections();
});

// 신뢰도에 따른 색상 클래스 반환
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.5) return 'text-yellow-600';
  return 'text-red-600';
};

// 공유하기 기능 구현
const shareResult = () => {
  showModal.value = true;
};

// 포토카드 모달 닫기
const closeModal = () => {
  showModal.value = false;
};

// 포토카드 다운로드
const downloadPhotocard = () => {
  if (photocard.value) {
    html2canvas(photocard.value, { useCORS: true, scale: 2 }).then((canvas) => {
      const link = document.createElement('a');
      link.download = 'photocard.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
    });
  }
};

// 이미지 팝업 열기
function openImagePopup(imageUrl) {
  popupImageUrl.value = `${BACKEND_BASE_URL}/uploads/${imageUrl}`; // Updated to include BACKEND_BASE_URL
  isImagePopupVisible.value = true;
}

// 내가 잡은 물고기 페이지로 이동
function navigateToCatches() {
  router.push('/catches');
}

// Define backend base URL
const BACKEND_BASE_URL = 'http://localhost:5000';

// 뒤로 가기 기능 구현
const goBack = () => {
  router.back();
};

const imageSource = computed(() => {
  if (imageUrl.value && store.state.isAuthenticated) {
    return `${BACKEND_BASE_URL}/uploads/${imageUrl.value}`; // Updated to backend URL
  } else if (imageBase64.value) {
    return `data:image/jpeg;base64,${imageBase64.value}`;
  }
  return '/placeholder.svg';
});
</script>

<style scoped>
.uploaded-image img {
  max-width: 100%;
  height: auto;

  object-fit: cover;
}

.fixed {
  position: fixed;
}

.absolute {
  position: absolute;
}

/* Ensure pop-up images are displayed correctly */
.object-contain {
  object-fit: contain;
}
</style>
