<template>
  <div class="min-h-screen bg-gray-100 flex justify-center">
    <div class="w-full max-w-md bg-white shadow-lg">
      <header class="fixed top-0 left-0 right-0 bg-white px-4 py-3 flex items-center justify-between border-b z-10 max-w-md mx-auto">
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

      <main class="pb-20 px-4">
        <!-- 로딩 상태 -->
        <div v-if="isLoading" class="flex justify-center items-center h-64">
          <span class="text-gray-500">Loading...</span>
        </div>

        <!-- 에러 메시지 -->
        <div v-if="errorMessage" class="p-4 bg-red-100 text-red-600 rounded-lg">
          {{ errorMessage }}
        </div>

        <!-- 업로드된 물고기 이미지 표시 -->
        <div v-if="!isLoading && !errorMessage" class="mt-4 bg-gray-200 rounded-lg p-4">
          <div class="relative w-full aspect-[4/3] bg-gray-100">
            <img 
              ref="fishImage" 
              :src="imageSource" 
              alt="물고기 사진" 
              class="absolute inset-0 w-full h-full object-contain cursor-pointer"
              @click="handleImageClick" 
              @load="onImageLoad" 
            />
            <template v-if="imageDimensions.width && imageDimensions.height">
              <div 
                v-for="(detection, index) in detections" 
                :key="index" 
                class="absolute" 
                :style="getBoundingBoxStyle(detection.bbox)"
              >
              </div>
            </template>
          </div>
        </div>
        
        <!-- AI 판별 결과 -->
        <div v-if="!isLoading && fishName" class="mt-6 bg-red-50 rounded-lg p-4 border-2 border-red-500">
          <div class="flex items-center mb-2">
            <AlertTriangleIcon class="w-6 h-6 text-red-500 mr-2" />
            <h2 class="text-lg font-bold text-red-700">경고: 현재 포획 금지 어종</h2>
          </div>
          <p class="text-red-600" v-if="detections[0].label !== '알 수 없음'">
            이 물고기는 <strong>{{ detections[0].label }}</strong>입니다.
            <span :class="[
              'text-sm',
              getConfidenceColor(detections[0].confidence)
            ]">
              신뢰도: {{ (detections[0].confidence * 100).toFixed(2) }}%
            </span>
          </p>
          <p class="text-red-600" v-else>
            이 물고기는 <strong>알 수 없음</strong>으로 판별되었습니다.
          </p>

          <!-- 다른 후보 추가 -->
          <p class="text-sm text-red-600 mt-2"
            v-if="detections.length > 1 && detections[0].label !== '알 수 없음'">
            다른 후보:
            <span class="text-red-500">
              <span v-for="(detection, index) in detections.slice(1)" :key="index">
                {{ detection.label }}
                <span :class="[
                  'text-sm',
                  getConfidenceColor(detection.confidence)
                ]">
                  (신뢰도: {{ (detection.confidence * 100).toFixed(2) }}%)
                </span>
                {{ index < detections.slice(1).length - 1 ? ', ' : '' }}
              </span>
            </span>
          </p>
          <p class="text-red-600 mt-2">금어기 기간: {{ prohibitedDates }}</p>
        </div>

        <div v-if="!isLoading && !errorMessage" class="mt-6 bg-gray-50 rounded-lg p-4">
          <h2 class="text-xl font-bold mb-2">{{ fishName }}</h2>
          <p class="text-gray-600">학명: {{ scientificName }}</p>
          <p class="mt-2 text-gray-700">{{ fishDescription }}</p>
        </div>

        <div v-if="!isLoading && !errorMessage" class="mt-6 bg-yellow-50 rounded-lg p-4">
          <h3 class="font-bold text-yellow-700 mb-2">포획 제한 이유</h3>
          <ul class="list-disc list-inside text-yellow-800">
            <li>ChatGPT로 생성된 포획 제한 이유</li>
          </ul>
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
            <InfoIcon class="w-5 h-5 mr-2" />
            <span>내가 잡은 물고기 리스트 보기</span>
          </button>
        </div>
      </main>

      <!-- 이미지 팝업 모달 -->
      <div
        v-if="isImagePopupVisible"
        class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-30"
        @click="closeImagePopup"
      >
        <div class="bg-white p-4 rounded-lg relative" @click.stop>
          <button class="absolute top-2 right-2" @click="closeImagePopup">
            &times;
          </button>
          <img :src="popupImageUrl" alt="확대된 이미지" class="max-w-full max-h-full" />
        </div>
      </div>

      <!-- 공유 모달 -->
      <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
        <div class="bg-white p-6 rounded-lg relative">
          <button class="absolute top-2 right-2" @click="showModal = false">
            &times;
          </button>
          <h2 class="text-xl font-bold mb-4">공유하기</h2>
          <!-- 공유 옵션들 -->
          <button class="w-full bg-blue-500 text-white py-2 px-4 rounded-lg mb-2">Facebook으로 공유</button>
          <button class="w-full bg-blue-700 text-white py-2 px-4 rounded-lg mb-2">Twitter로 공유</button>
          <button class="w-full bg-green-500 text-white py-2 px-4 rounded-lg">링크 복사</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ChevronLeftIcon, AlertTriangleIcon, BellIcon, Settings2Icon, InfoIcon, Share2Icon } from 'lucide-vue-next';
import { useStore } from 'vuex';

const store = useStore();
const route = useRoute();
const router = useRouter();

const detections = JSON.parse(decodeURIComponent(route.query.detections || '[]'));
const fishName = computed(() => {
  if (detections.length > 0 && detections[0].label !== '알 수 없음') {
    return detections[0].label;
  }
  return '알 수 없는 물고기';
});
const prohibitedDates = route.query.prohibitedDates || '알 수 없음';
const scientificName = ref('ChatGPT로 생성된 학명');
const fishDescription = ref('ChatGPT로 생성된 물고기 설명');
const isLoading = ref(true);
const errorMessage = ref('');
const imageUrl = ref('');
const imageBase64 = ref('');
const showModal = ref(false);

// Define backend base URL
const BACKEND_BASE_URL = 'http://localhost:5000';

const goBack = () => {
  window.history.back();
};

// 공유하기 기능 구현
const shareResult = () => {
  showModal.value = true;
};

// 이미지 소스 계산
const imageSource = computed(() => {
  if (imageBase64.value) {
    return `data:image/jpeg;base64,${imageBase64.value}`;
  } else if (imageUrl.value && store.state.isAuthenticated) {
    return `${BACKEND_BASE_URL}/uploads/${imageUrl.value}`;
  }
  return '/placeholder.svg';
});

// 이미지 팝업 상태
const popupImageUrl = ref('');
const isImagePopupVisible = ref(false);

// 이미지 클릭 핸들러
const handleImageClick = () => {
  if (imageSource.value === '/placeholder.svg') {
    alert('이미지를 불러올 수 없습니다.');
    return;
  }
  openImagePopup(imageSource.value);
};

// 이미지 팝업 열기
function openImagePopup(imageSrc) {
  if (
    imageSrc.startsWith('data:image/') ||
    imageSrc.startsWith('http://') ||
    imageSrc.startsWith('https://')
  ) {
    popupImageUrl.value = imageSrc;
  } else {
    popupImageUrl.value = `${BACKEND_BASE_URL}/uploads/${imageSrc}`;
  }
  isImagePopupVisible.value = true;
}

// 이미지 팝업 닫기
function closeImagePopup() {
  isImagePopupVisible.value = false;
}

// 내가 잡은 물고기 페이지로 이동
function navigateToCatches() {
  router.push('/catches');
}

// 컴포넌트 마운트 시 초기화
onMounted(() => {
  console.log('컴포넌트가 마운트되었습니다.');
  
  imageUrl.value = route.query.imageUrl || '';
  imageBase64.value = route.query.imageBase64 ? decodeURIComponent(route.query.imageBase64) : '';

  // 실제 이미지 로딩 완료 시에만 isLoading을 false로 설정
  const img = new Image();
  img.src = imageSource.value;
  img.onload = () => {
    isLoading.value = false;
  };
  img.onerror = () => {
    isLoading.value = false;
    if (imageSource.value === '/placeholder.svg') {
      errorMessage.value = '이미지를 불러오는 데 실패했습니다.';
    }
  };
});

const fishImage = ref(null);
const imageDimensions = ref({ width: 0, height: 0 });

const onImageLoad = () => {
  const imageElement = fishImage.value;
  if (imageElement) {
    imageDimensions.value.width = imageElement.naturalWidth;
    imageDimensions.value.height = imageElement.naturalHeight;
    console.log('Image loaded:', fishImage.value);
  }
};

const getBoundingBoxStyle = (bbox) => {
  // Handle case where bbox is not an array
  if (!Array.isArray(bbox)) {
    console.warn('Invalid bbox format:', bbox);
    return {};
  }

  const [x1, y1, x2, y2] = bbox;
  const imageElement = fishImage.value;

  if (!imageElement || !imageDimensions.value.width || !imageDimensions.value.height) {
    return {};
  }

  // 이미지의 실제 표시 크기와 원본 크기의 비율 계산
  const displayWidth = imageElement.clientWidth;
  const displayHeight = imageElement.clientHeight;
  const scaleX = displayWidth / imageDimensions.value.width;
  const scaleY = displayHeight / imageDimensions.value.height;

  // 바운딩 박스 위치와 크기 계산
  return {
    left: `${x1 * scaleX}px`,
    top: `${y1 * scaleY}px`,
    width: `${(x2 - x1) * scaleX}px`,
    height: `${(y2 - y1) * scaleY}px`,
    position: 'absolute',
    border: '2px solid red',
    pointerEvents: 'none',
    backgroundColor: 'rgba(255, 0, 0, 0.1)'
  };
};

// 신뢰도에 따른 색상 클래스 반환
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return 'text-red-600';
  if (confidence >= 0.5) return 'text-red-400';
  return 'text-red-300';
};
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

.object-contain {
  object-fit: contain;
  width: 100%;
  height: 100%;
}

.relative {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f3f4f6;
  min-height: 300px;
}

.absolute.inset-0 {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.aspect-\[4\/3\] {
  aspect-ratio: 4/3;
}

header {
  position: fixed;
  top: 0;
  z-index: 10;
}

.bg-opacity-50 {
  background-opacity: 0.5;
}

.modal {
  background: white;
}
</style>
