# Start of Selection
<template>
  <div class="min-h-screen bg-white flex flex-col">
    <!-- 헤더 -->
    <header
      class="fixed top-0 left-0 right-0 bg-white px-4 py-3 flex items-center justify-between border-b z-10 max-w-md mx-auto">
      <div class="flex items-center">
        <button class="mr-2" @click="goBack" :disabled="isLoading">
          <ChevronLeftIcon class="w-6 h-6" />
        </button>
        <h1 class="text-xl font-bold">물고기 판별 결과</h1>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2" :disabled="isLoading">
          <BellIcon class="w-6 h-6" />
        </button>
        <button class="p-2" :disabled="isLoading">
          <Settings2Icon class="w-6 h-6" />
        </button>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="flex-1 pb-20 px-4 overflow-auto max-w-md mx-auto">
      <!-- 로딩 상태 -->
      <div v-if="loading" class="fixed inset-0 flex justify-center items-center bg-white bg-opacity-75 z-50">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
          <span class="text-sm text-gray-500">로딩중...</span>
        </div>
      </div>

      <!-- 에러 메시지 -->
      <div v-if="errorMessage" class="p-4 bg-red-100 text-red-600 rounded-lg">
        {{ errorMessage }}
      </div>

      <!-- 업로드된 물고기 이미지 표시 -->
      <div v-if="!isLoading && !errorMessage" class="mt-4 bg-gray-200 rounded-lg p-4">
        <div class="image-container" :style="imageContainerStyle">
          <div class="image-wrapper">
            <div class="detection-area">
              <img 
                ref="fishImage" 
                :src="imageSource" 
                alt="물고기 사진" 
                :class="imageClass"
                @click="handleImageClick" 
                @load="onImageLoad" 
              />
              <template v-if="imageDimensions.width && imageDimensions.height">
                <div 
                  v-for="(detection, index) in parsedDetections" 
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
      <div v-if="!isLoading && !errorMessage" class="mt-6 bg-blue-50 rounded-lg p-4">
        <div class="flex items-center mb-2">
          <h2 class="text-lg font-bold text-blue-700">정상: 현재 포획 가능 어종</h2>
        </div>
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
                {{ index < parsedDetections.slice(1).length - 1 ? ', ' : '' }}
              </span>
            </span>
          </p>
        </template>
        <template v-else>
          <p class="text-blue-600">
            예측 결과가 존재하지 않습니다.
          </p>
        </template>
      </div>

      <div v-if="!isLoading && !errorMessage" class="mt-6 bg-gray-50 rounded-lg p-4">
        <h2 class="text-xl font-bold mb-2">{{ fishName }}</h2>
        <p class="text-gray-600">학명: {{ scientificName || '정보 없음' }}</p>
        <p class="mt-2 text-gray-700">{{ fishDescription || '설명 없음' }}</p>
      </div>

      <!-- 공유하기 버튼 -->
      <div v-if="!isLoading && !errorMessage" class="mt-4">
        <button class="w-full bg-green-500 text-white py-3 px-4 rounded-lg flex items-center justify-center"
          @click="shareResult" :disabled="isLoading">
          <Share2Icon class="w-5 h-5 mr-2" />
          <span>공유하기</span>
        </button>
      </div>

      <!-- 물고기 정보 수정 버튼 -->
      <div v-if="!isLoading && !errorMessage && store.state.isAuthenticated" class="mt-4">
        <button 
          class="w-full bg-blue-500 text-white py-3 px-4 rounded-lg flex items-center justify-center"
          @click="openEditModal"
        >
          <Edit class="w-5 h-5 mr-2" />
          <span>물고기 정보 수정</span>
        </button>
      </div>

      <!-- 내가 잡은 물고기 페이지로 이동 버튼 -->
      <div v-if="!isLoading && !errorMessage" class="mt-4">
        <button class="w-full bg-blue-500 text-white py-3 px-4 rounded-lg flex items-center justify-center"
          @click="navigateToCatches" :disabled="isLoading">
          <InfoIcon class="w-5 h-5 mr-2" />
          <span>내가 잡은 물고기 리스트 보기</span>
        </button>
      </div>

      <!-- AI 모델 경고 문구 추가 -->
      <div class="mt-6 mb-4 bg-gray-50 rounded-lg p-4 border border-gray-200 shadow-sm">
        <div class="flex flex-col items-center gap-2">
          <div class="flex items-center justify-center gap-2 text-yellow-500">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span class="font-semibold">AI 판별 주의사항</span>
          </div>
          <p class="text-sm text-gray-600 text-center leading-relaxed">
            인공지능 모델의 판별 결과는 참고용입니다.<br>
            실제 상황과 법적 규제를 반드시 확인하세요.
          </p>
        </div>
      </div>

      <!-- 추가 로딩 인디케이터 -->
      <div v-if="isLoadingMore" class="flex justify-center items-center py-8">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mb-2"></div>
          <span class="text-sm text-gray-500">데이터를 불러오는 중...</span>
        </div>
      </div>
    </main>

    <!-- 포토카드 모달 -->
    <div v-if="showModal && !isLoading" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-[60] max-w-md mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6 w-10/12 max-w-sm">
        <h2 class="text-lg font-bold mb-4 text-center">나만의 포토카드</h2>
        <div ref="photocard" class="bg-gray-100 p-4 rounded-lg overflow-auto">
          <img :src="imageSource" alt="물고기 사진" class="w-full h-64 object-contain rounded-lg" />
          <h3 class="text-md font-semibold mt-4 text-center">{{ parsedDetections[0].label }}</h3>
          <p class="text-center text-sm">신뢰도: {{ (parsedDetections[0].confidence * 100).toFixed(2) }}%</p>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="closeModal" class="px-4 py-2 bg-gray-300 rounded" :disabled="isLoading">닫기</button>
          <button @click="downloadPhotocard" class="px-4 py-2 bg-blue-500 text-white rounded" :disabled="isLoading">저장하기</button>
        </div>
      </div>
    </div>

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

    <!-- Add consent modal -->
    <ConsentModal 
      v-if="showConsentModal"
      :isVisible="showConsentModal"
      @close="handleConsentClose"
      @consent="handleConsent"
    />

    <!-- Add edit fish modal -->
    <EditFishModal
      v-if="showEditModal"
      :isVisible="showEditModal"
      :catchData="selectedCatch"
      @close="showEditModal = false"
      @save="handleFishDataSave"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import html2canvas from 'html2canvas';
import { ChevronLeftIcon, BellIcon, Settings2Icon, Share2Icon, InfoIcon, Edit, X } from 'lucide-vue-next';
import { useStore } from 'vuex';
import ConsentModal from '../components/ConsentModal.vue';
import EditFishModal from '../components/EditFishModal.vue';

const store = useStore();
const route = useRoute();
const router = useRouter();

const isLoading = ref(true);
const errorMessage = ref('');
const parsedDetections = ref([]);
const imageUrl = ref('');
const imageBase64 = ref('');
const showModal = ref(false);
const photocard = ref(null);
const popupImageUrl = ref('');
const isImagePopupVisible = ref(false);
const fishImage = ref(null);
const imageDimensions = ref({ width: 0, height: 0 });
const showConsentModal = ref(false);
const showEditModal = ref(false);
const selectedCatch = ref(null);
const loading = ref(true);

// Define backend base URL
const BACKEND_BASE_URL = 'http://localhost:5000';

// Change fishName to a computed property
const fishName = computed(() => {
  if (parsedDetections.value.length > 0 && parsedDetections.value[0].label !== '알 수 없음') {
    return parsedDetections.value[0].label;
  }
  return '알 수 없는 물고기';
});

const scientificName = ref('ChatGPT로 생성된 학명'); // 필요에 따라 학명 정보를 추가하세요.
const fishDescription = ref('ChatGPT로 생성된 물고기 설명'); // 필요에 따라 물고기 설명을 추가하세요.

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

onMounted(async () => {
  try {
    loading.value = true;
    await store.dispatch('fetchInitialData');
    if (store.state.isAuthenticated) {
      console.log('Checking consent status...');
      try {
        const consentStatus = await store.dispatch('checkConsent');
        console.log('Consent status:', consentStatus);
        if (!consentStatus.hasConsent) {
          console.log('Showing consent modal...');
          showConsentModal.value = true;
        }
      } catch (error) {
        console.error('Error checking consent:', error);
      }
    }
    fetchDetections();
  } catch (error) {
    console.error('Error:', error);
  } finally {
    loading.value = false;
  }
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

// 이미지 소스 계산
const imageSource = computed(() => {
  if (imageUrl.value && store.state.isAuthenticated) {
    return `${BACKEND_BASE_URL}/uploads/${imageUrl.value}`; // Authenticated users get the image from backend
  } else if (imageBase64.value) {
    return `data:image/jpeg;base64,${imageBase64.value}`; // Unauthenticated users get base64 image
  }
  return '/placeholder.svg'; // Fallback placeholder
});

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
  // Directly assign imageSrc without adding '/uploads/' again
  popupImageUrl.value = imageSrc;
  isImagePopupVisible.value = true;
}

// 내가 잡은 물고기 페이지로 이동
function navigateToCatches() {
  router.push('/catches');
}

// 뒤로 가기 기능 구현
const goBack = () => {
  router.back();
};

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

  const renderedWidth = imageElement.clientWidth;
  const renderedHeight = imageElement.clientHeight;

  const scaleX = renderedWidth / imageDimensions.value.width;
  const scaleY = renderedHeight / imageDimensions.value.height;

  return {
    left: `${x1 * scaleX}px`,
    top: `${y1 * scaleY}px`,
    width: `${(x2 - x1) * scaleX}px`,
    height: `${(y2 - y1) * scaleY}px`
  };
};

// 이미지 크기에 따른 클래스 계산
const imageClass = computed(() => {
  if (!imageDimensions.value.width || !imageDimensions.value.height) {
    return 'detection-image';
  }
  
  // 작은 이미지 기준 (예: 800px)
  return imageDimensions.value.width < 800 
    ? 'detection-image small-image' 
    : 'detection-image';
});

const imageContainerStyle = computed(() => {
  if (!imageDimensions.value.width || !imageDimensions.value.height) {
    return { 
      minHeight: 'fit-content',
      padding: '0.5rem'
    };
  }

  const style = {
    minHeight: 'fit-content',
    padding: '0.5rem'
  };

  // 작은 이미지일 경우 패딩 제거
  if (imageDimensions.value.width < 800) {
    style.padding = '0';
  }

  return style;
});

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onUnmounted(() => {
  window.removeEventListener('resize', updateBoundingBoxes);
});

// bbox 업데이트 함수
const updateBoundingBoxes = () => {
  // 강제로 Vue가 bbox를 다시 계산하도록 함
  imageDimensions.value = { ...imageDimensions.value };
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

const handleFishDataSave = async (updatedData) => {
  try {
    await store.dispatch('updateCatch', updatedData);
    showEditModal.value = false;
    router.push('/catches');
  } catch (error) {
    console.error('Error saving fish data:', error);
  }
};

const openEditModal = () => {
  // 새로운 catch 생성을 위한 POST 요청
  const createNewCatch = async () => {
    try {
      const response = await axios.post('/catches', {
        detections: parsedDetections.value,
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
        detections: parsedDetections.value,
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
</script>

<style scoped>
.image-container {
  position: relative;
  width: 100%;
  background-color: #f3f4f6;
  min-height: fit-content;
  padding: 0.5rem;
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
  max-width: 100vw;  /* 화면 너비 최대로 설정 */
}

.detection-image {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  object-fit: contain;
  cursor: pointer;
}

/* 작은 이미지 처리를 위한 스타일 */
.small-image {
  width: 100vw;
  max-width: none;
  margin: -0.5rem;  /* 컨테이너 패딩 상쇄 */
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

.aspect-\[4\/3\] {
  aspect-ratio: 4/3;
}
</style>
# End of Selection
```
