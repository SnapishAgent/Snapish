<template>
  <div class="min-h-screen bg-gray-100 flex flex-col">
    <!-- 헤더 -->
    <header
      class="fixed top-0 left-0 right-0 bg-white px-4 py-3 flex items-center justify-between border-b shadow-md z-50 max-w-md mx-auto">
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
    <main class="flex-1 pb-20 px-4 overflow-auto mt-[60px] max-w-md mx-auto">
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
        <img :src="imageUrl" alt="물고기 사진" class="w-full h-full object-cover" />
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
    </main>

    <!-- 포토카드 모달 -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div class="bg-white rounded-lg shadow-lg p-4 w-10/12 max-w-sm">
        <h2 class="text-lg font-bold mb-2 text-center">나만의 포토카드</h2>
        <div ref="photocard" class="bg-gray-100 p-2 rounded-lg overflow-hidden">
          <img :src="imageUrl" alt="물고기 사진" class="w-full h-48 object-cover rounded-lg" />
          <h3 class="text-md font-semibold mt-2 text-center">{{ parsedDetections[0].label }}</h3>
          <p class="text-center text-sm">신뢰도: {{ (parsedDetections[0].confidence * 100).toFixed(2) }}%</p>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <button @click="closeModal" class="px-3 py-1 bg-gray-300 rounded">닫기</button>
          <button @click="downloadPhotocard" class="px-3 py-1 bg-blue-500 text-white rounded">저장하기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, watch } from 'vue';
import {
  BellIcon,
  Settings2Icon,
  ChevronLeftIcon,
  Share2Icon,
} from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import html2canvas from 'html2canvas';

// props 정의
const props = defineProps({
  detections: {
    type: String, // JSON 문자열로 전달됨
    required: true,
  },
  imageUrl: {
    type: String,
    required: true,
  },
});

// 라우터 인스턴스
const router = useRouter();

// 로딩 상태
const isLoading = ref(true);

// 에러 메시지
const errorMessage = ref('');

// parsedDetections을 ref로 선언
const parsedDetections = ref([]);

// 포토카드 모달 제어
const showModal = ref(false);

// 포토카드 엘리먼트 참조
const photocard = ref(null);

// watch를 통해 props.detections을 파싱하고 에러 처리
watch(
  () => props.detections,
  (newVal) => {
    console.log('Received detections:', newVal); // 추가된 로그
    try {
      // detections을 디코딩하여 파싱
      const decodedVal = decodeURIComponent(newVal);
      console.log('Decoded detections:', decodedVal); // 디코딩된 값 확인
      const detections = JSON.parse(decodedVal);
      console.log('Parsed detections:', detections); // 파싱된 값 확인
      parsedDetections.value = detections;
      errorMessage.value = '';
    } catch (e) {
      console.error('Failed to parse detections:', e);
      errorMessage.value = '예측 결과를 불러오는 데 실패했습니다.';
      parsedDetections.value = [];
    } finally {
      isLoading.value = false;
    }
  },
  { immediate: true }
);

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
    html2canvas(photocard.value).then((canvas) => {
      const link = document.createElement('a');
      link.download = 'photocard.png';
      link.href = canvas.toDataURL();
      link.click();
    });
  }
};

// 뒤로 가기 기능 구현
const goBack = () => {
  router.back();
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
</style>
