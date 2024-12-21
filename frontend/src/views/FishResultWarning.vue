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
        <div v-if="loading" class="fixed inset-0 flex justify-center items-center bg-white bg-opacity-75 z-50">
          <div class="flex flex-col items-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
            <span class="text-sm text-gray-500">로딩중...</span>
          </div>
        </div>

        <!-- 추가 로딩 인디케이터 -->
        <div v-if="isLoadingMore" class="flex justify-center items-center py-8">
          <div class="flex flex-col items-center">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mb-2"></div>
            <span class="text-sm text-gray-500">데이터를 불러오는 중...</span>
          </div>
        </div>

        <!-- 에러 메시지 -->
        <div v-if="errorMessage" class="p-4 bg-red-100 text-red-600 rounded-lg">
          {{ errorMessage }}
        </div>

        <!-- 업로드된 물고기 이미지 표시 -->
        <div v-if="!loading && !errorMessage" class="mt-4 bg-gray-200 rounded-lg p-4">
          <div class="image-container" :style="imageContainerStyle">
            <div class="image-wrapper">
              <div class="detection-area">
                <img 
                  ref="fishImage" 
                  :src="imageSource" 
                  alt="물고기 사진" 
                  class="detection-image"
                  @click="handleImageClick" 
                  @load="onImageLoad" 
                />
                <template v-if="imageDimensions.width && imageDimensions.height">
                  <div 
                    v-for="(detection, index) in detections" 
                    :key="index" 
                    class="bounding-box" 
                    :style="getBoundingBoxStyle(detection.bbox)"
                  >
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
        
        <!-- AI 판별 결과 -->
        <div v-if="!loading && fishName" class="mt-6 bg-red-50 rounded-lg p-4 border-2 border-red-500">
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

        <div v-if="!loading && !errorMessage" class="mt-6 bg-gray-50 rounded-lg p-4">
          <h2 class="text-xl font-bold mb-2">{{ fishName }}</h2>
          <p class="text-gray-600">학명: {{ scientificName }}</p>
          <p class="mt-2 text-gray-700">{{ fishDescription }}</p>
        </div>

        <div v-if="!loading && !errorMessage" class="mt-6 bg-yellow-50 rounded-lg p-4">
          <h3 class="font-bold text-yellow-700 mb-2">포획 제한 이유</h3>
          <ul class="list-disc list-inside text-yellow-800">
            <li>ChatGPT로 생성된 포획 제한 이유</li>
          </ul>
        </div>

        <!-- 공유하기 버튼 -->
        <div v-if="!loading && !errorMessage" class="mt-4">
          <button class="w-full bg-green-500 text-white py-3 px-4 rounded-lg flex items-center justify-center"
            @click="shareResult">
            <Share2Icon class="w-5 h-5 mr-2" />
            <span>공유하기</span>
          </button>
        </div>

        <!-- 물고기 정보 수정 버튼 -->
        <div v-if="!loading && !errorMessage && store.state.isAuthenticated" class="mt-4">
          <button 
            class="w-full bg-red-500 text-white py-3 px-4 rounded-lg flex items-center justify-center"
            @click="openEditModal"
          >
            <Edit class="w-5 h-5 mr-2" />
            <span>물고기 정보 수정</span>
          </button>
        </div>

        <!-- 내가 잡은 물고기 페이지로 이동 버튼 -->
        <div v-if="!loading && !errorMessage" class="mt-4">
          <button class="w-full bg-blue-500 text-white py-3 px-4 rounded-lg flex items-center justify-center"
            @click="navigateToCatches">
            <InfoIcon class="w-5 h-5 mr-2" />
            <span>내가 잡은 물고기 리스트 보기</span>
          </button>
        </div>

        <!-- AI 모델 경고 문구 추가 -->
        <div class="mt-6 mb-4 bg-red-50 rounded-lg p-4 border border-red-100 shadow-sm">
          <div class="flex flex-col items-center gap-2">
            <div class="flex items-center justify-center gap-2 text-red-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span class="font-semibold">AI 판별 주의사항</span>
            </div>
            <p class="text-sm text-red-600 text-center leading-relaxed">
              인공지능 모델의 판별 결과는 참고용입니다.<br>
              실제 상황과 법적 규제를 반드시 확인하세요.
            </p>
          </div>
        </div>
      </main>

      <!-- 이미지 팝업 -->
      <div v-if="isImagePopupVisible"
          class="fixed inset-0 bg-black bg-opacity-90 flex justify-center items-center z-50 p-4"
          @click="isImagePopupVisible = false">
          <div class="relative w-full max-w-4xl max-h-[90vh] flex items-center justify-center" @click.stop>
              <div class="relative">
                  <img 
                      :src="popupImageUrl" 
                      alt="Popup Image"
                      class="w-auto h-auto max-w-full max-h-[85vh] rounded-lg shadow-xl object-contain"
                  />
                  <button 
                      @click="isImagePopupVisible = false"
                      class="absolute top-4 right-4 p-2 bg-white rounded-full hover:bg-gray-100 transition-colors shadow-lg"
                  >
                      <X class="w-5 h-5 text-gray-600" />
                  </button>
              </div>
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

      <!-- Add edit fish modal -->
      <EditFishModal
        v-if="showEditModal"
        :isVisible="showEditModal"
        :catchData="selectedCatch"
        @close="showEditModal = false"
        @save="handleFishDataSave"
      />

      <!-- Add consent modal -->
      <ConsentModal 
        v-if="showConsentModal"
        :isVisible="showConsentModal"
        @close="handleConsentClose"
        @consent="handleConsent"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ChevronLeftIcon, AlertTriangleIcon, BellIcon, Settings2Icon, InfoIcon, Share2Icon, Edit, X } from 'lucide-vue-next';
import { useStore } from 'vuex';
import ConsentModal from '../components/ConsentModal.vue';
import EditFishModal from '../components/EditFishModal.vue';
import axios from 'axios';

const store = useStore();
const route = useRoute();
const router = useRouter();

const showEditModal = ref(false);
const selectedCatch = ref(null);
const showConsentModal = ref(false);
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
const loading = ref(true);
const isLoadingMore = ref(false);
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

// 이미지 팝업 관련 상태
const isImagePopupVisible = ref(false);
const popupImageUrl = ref('');

// 이미지 팝업 열기
function openImagePopup(imageSrc) {
    popupImageUrl.value = imageSrc.startsWith('http') ? imageSrc : `${BACKEND_BASE_URL}/uploads/${imageSrc}`;
    isImagePopupVisible.value = true;
}

// 내가 잡은 물고기 페이지로 이동
function navigateToCatches() {
  router.push('/catches');
}

// 컴포넌트 마운트 시 초기화
onMounted(async () => {
  console.log('포넌트가 마운트되었습니다.');
  
  imageUrl.value = route.query.imageUrl || '';
  imageBase64.value = route.query.imageBase64 ? decodeURIComponent(route.query.imageBase64) : '';

  // 실제 이미지 로딩 완료 시에만 isLoading을 false로 설정
  const img = new Image();
  img.src = imageSource.value;
  img.onload = () => {
    loading.value = false;
  };
  img.onerror = () => {
    loading.value = false;
    if (imageSource.value === '/placeholder.svg') {
      errorMessage.value = '이미지를 불러오는 데 실패했습니다.';
    }
  };

  if (store.state.isAuthenticated) {
    try {
      const consentStatus = await store.dispatch('checkConsent');
      if (!consentStatus.hasConsent) {
        showConsentModal.value = true;
      }
    } catch (error) {
      console.error('Error checking consent:', error);
    }
  }
});

const fishImage = ref(null);
const imageDimensions = ref({ width: 0, height: 0 });

const onImageLoad = () => {
  const imageElement = fishImage.value;
  if (imageElement) {
    imageDimensions.value = {
      width: imageElement.naturalWidth,
      height: imageElement.naturalHeight
    };
    
    // resize 이벤트 리스너 추가
    window.addEventListener('resize', updateBoundingBoxes);
    // 초기 bbox 업데이트를 위해 약간의 지연 추가
    setTimeout(updateBoundingBoxes, 100);
  }
};

const getBoundingBoxStyle = (bbox) => {
  if (!Array.isArray(bbox)) {
    console.warn('Invalid bbox format:', bbox);
    return {};
  }

  const [x1, y1, x2, y2] = bbox;
  const imageElement = fishImage.value;

  if (!imageElement || !imageDimensions.value.width || !imageDimensions.value.height) {
    return {};
  }

  // 이미지의 실제 렌더링된 크기 계산
  const renderedWidth = imageElement.clientWidth;
  const renderedHeight = imageElement.clientHeight;

  // 스케일 계산
  const scaleX = renderedWidth / imageDimensions.value.width;
  const scaleY = renderedHeight / imageDimensions.value.height;

  return {
    left: `${x1 * scaleX}px`,
    top: `${y1 * scaleY}px`,
    width: `${(x2 - x1) * scaleX}px`,
    height: `${(y2 - y1) * scaleY}px`
  };
};

const imageContainerStyle = computed(() => {
  if (!imageDimensions.value.width || !imageDimensions.value.height) {
    return { 
      minHeight: 'fit-content',
      padding: '1rem'
    };
  }

  const aspectRatio = imageDimensions.value.width / imageDimensions.value.height;
  const style = {
    minHeight: 'fit-content',
    padding: '1rem'
  };

  // 세로로 긴 이미지일 경우 패딩 조정
  if (aspectRatio < 1) {
    style.padding = '2rem 1rem';
  }
  // 가로로 긴 이미지일 경우 작은 이미지일 경우 패딩 조정
  else if (aspectRatio > 1.5 || imageDimensions.value.height < 500) {
    style.padding = '0.5rem';
  }

  return style;
});

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onUnmounted(() => {
  window.removeEventListener('resize', updateBoundingBoxes);
});

// bbox 업데이트 함수
const updateBoundingBoxes = () => {
  // 강제 Vue가 bbox를 다 계산하도록 함
  imageDimensions.value = { ...imageDimensions.value };
};

// 신뢰도에 따른 색상 클래스 반환
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return 'text-red-600';
  if (confidence >= 0.5) return 'text-red-400';
  return 'text-red-300';
};

const openEditModal = () => {
  // 새로운 catch 생성을 위한 POST 요청
  const createNewCatch = async () => {
    try {
      const response = await axios.post('/catches', {
        detections: detections,
        imageUrl: imageUrl.value,
        catch_date: new Date().toISOString().split('T')[0]
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      console.log('Created new catch:', response.data);
      if (!response.data.id) {
        throw new Error('Invalid response from server: missing catch ID');
      }
      return response.data;
    } catch (error) {
      console.error('Error creating new catch:', error);
      alert('새로운 캐치 생성에 실패했습니다.');
      throw error;
    }
  };

  // 새로운 catch 생성 후 수정 모달 열기
  const initEditModal = async () => {
    try {
      const newCatch = await createNewCatch();
      if (!newCatch.id) {
        throw new Error('No catch ID received from server');
      }
      selectedCatch.value = {
        id: newCatch.id,
        detections: detections,
        imageUrl: imageUrl.value,
        catch_date: new Date().toISOString().split('T')[0],
        weight_kg: null,
        length_cm: null,
        latitude: null,
        longitude: null,
        memo: ''
      };
      console.log('Opening edit modal with catch:', selectedCatch.value);  // 디버깅용 로그
      showEditModal.value = true;
    } catch (error) {
      console.error('Error initializing edit modal:', error);
      alert('물고기 정보 수정을 초기화하는데 실패했습니다.');
    }
  };

  initEditModal();
};

const handleFishDataSave = async (updatedData) => {
  try {
    await store.dispatch('updateCatch', updatedData);
    showEditModal.value = false;
    router.push('/catches');
  } catch (error) {
    console.error('Error saving fish data:', error);
  }
};

const handleConsentClose = () => {
  showConsentModal.value = false;
};

const handleConsent = async (consented) => {
  if (!consented) {
    router.push('/');
    return;
  }
};

// 이미지 클릭 핸들러 추가
const handleImageClick = () => {
  if (imageSource.value === '/placeholder.svg') {
    alert('이미지를 불러올 수 없습니다.');
    return;
  }
  openImagePopup(imageSource.value);
};
</script>

<style scoped>
.image-container {
  position: relative;
  width: 100%;
  background-color: #f3f4f6;
  min-height: fit-content;
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.detection-area {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.detection-image {
  display: block;
  max-width: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  cursor: pointer;
}

.bounding-box {
  position: absolute;
  border: 2px solid red;
  pointer-events: none;
  background-color: rgba(255, 0, 0, 0.1);
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

.bg-opacity-50 {
  background-opacity: 0.5;
}

.modal {
  background: white;
}
</style>
