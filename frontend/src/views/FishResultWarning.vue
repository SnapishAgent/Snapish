<template>
  <!-- 전체 페이지 컨테이너 -->
  <div class="min-h-screen bg-gray-100 flex justify-center">
    <!-- 메인 카드 컨테이너 -->
    <div class="w-full max-w-md bg-white shadow-lg">
      <!-- 상단 헤더 영역 -->
      <header class="sticky top-0 bg-white px-4 py-3 flex items-center justify-between border-b">
        <!-- 좌측 헤더: 뒤로가기 버튼과 제목 -->
        <div class="flex items-center">
          <button class="mr-2">
            <ChevronLeftIcon class="w-6 h-6" />
          </button>
          <h1 class="text-xl font-bold">물고기 판별 결과</h1>
        </div>
        <!-- 우측 헤더: 알림과 설정 버튼 -->
        <div class="flex items-center gap-4">
          <button class="p-2">
            <BellIcon class="w-6 h-6" />
          </button>
          <button class="p-2">
            <Settings2Icon class="w-6 h-6" />
          </button>
        </div>
      </header>

      <!-- 메인 컨텐츠 영역 -->
      <main class="pb-20 px-4">
        <!-- 물고기 이미지 섹션 -->
        <div class="mt-4 bg-gray-200 rounded-lg p-4 flex justify-center">
          <img src="@/../public/sample-img-1.jpg" alt="물고기 사진" class="w-full h-full object-cover" />
        </div>

        <!-- 경고 메시지 섹션 -->
        <div class="mt-6 bg-red-50 rounded-lg p-4 border-2 border-red-500">
          <div class="flex items-center mb-2">
            <AlertTriangleIcon class="w-6 h-6 text-red-500 mr-2" />
            <h2 class="text-lg font-bold text-red-700">주의: 현재 포획 금지 어종</h2>
          </div>
          <p class="text-red-600 mt-2">이 물고기는 <strong>참돔</strong>입니다.
            <span class="text-sm text-red-500">(신뢰도: {{ confidence }}%)</span>
          </p>
          <p class="text-red-600 mt-2">현재 포획 금지되어 있습니다.</p>
        </div>

        <!-- 물고기 상세 정보 섹션 -->
        <div class="mt-6 bg-gray-50 rounded-lg p-4">
          <h2 class="text-xl font-bold mb-2">참돔</h2>
          <p class="text-gray-600">학명: Pagrus major</p>
          <p class="mt-2 text-gray-700">참돔은 한국 연안에서 흔히 볼 수 있는 어종이지만, 현재 자원 보호를 위해 포획이 제한되어 있습니다.</p>
        </div>

        <!-- 포획 제한 이유 섹션 -->
        <div class="mt-6 bg-yellow-50 rounded-lg p-4">
          <h3 class="font-bold text-yellow-700 mb-2">포획 제한 이유</h3>
          <ul class="list-disc list-inside text-yellow-800">
            <li>산란기 보호 (5월 1일 ~ 6월 30일)</li>
            <li>어족 자원 회복을 위한 조치</li>
            <li>생태계 균형 유지</li>
          </ul>
        </div>

        <!-- 권장 행동 안내 섹션 -->
        <div class="mt-6 bg-green-50 rounded-lg p-4">
          <h3 class="font-bold text-green-700 mb-2">권장 행동</h3>
          <ul class="list-disc list-inside text-green-800">
            <li>즉시 물고기를 놓아주세요.</li>
            <li>가능한 한 물고기에 상처를 주지 않도록 주의하세요.</li>
            <li>다른 낚시꾼들에게 현재 상황을 알려주세요.</li>
          </ul>
        </div>

        <!-- 하단 액션 버튼 영역 -->
        <div class="mt-6 space-y-3">
          <button class="w-full bg-blue-500 text-white py-3 px-4 rounded-lg flex items-center justify-center">
            <InfoIcon class="w-5 h-5 mr-2" />
            <span>더 자세한 정보 보기</span>
          </button>
          <button class="w-full bg-green-500 text-white py-3 px-4 rounded-lg flex items-center justify-center">
            <Share2Icon class="w-5 h-5 mr-2" />
            <span>이 정보 공유하기</span>
          </button>
        </div>
      </main>
    </div>
  </div>

  <div>
    <h1>경고</h1>
    <img :src="imageSource" alt="Warning" />
    <p>{{ warningMessage }}</p>
  </div>
</template>

<script setup>

// Lucide 아이콘 컴포넌트 불러오기
import {
  BellIcon,         // 알림 아이콘
  Settings2Icon,    // 설정 아이콘
  ChevronLeftIcon,  // 뒤로가기 아이콘
  AlertTriangleIcon,// 경고 아이콘
  InfoIcon,         // 정보 아이콘
  Share2Icon,       // 공유 아이콘
} from 'lucide-vue-next'

import { computed } from 'vue';
import { useRoute } from 'vue-router';
import store from '../store';

const route = useRoute();

const imageUrl = route.query.imageUrl;
const imageBase64 = route.query.imageBase64;
const detections = computed(() => JSON.parse(decodeURIComponent(route.query.detections || '[]')));

const imageSource = computed(() => {
  if (imageUrl && store.state.isAuthenticated) {
    return `data:image/jpeg;base64,${imageUrl}`;
  } else if (imageBase64) {
    return `data:image/jpeg;base64,${imageBase64}`;
  }
  return '/placeholder.svg';
});

const warningMessage = computed(() => {
  const prohibited = detections.value.filter(d => d.label === 'ProhibitedFishLabel'); // Replace with actual label
  if (prohibited.length > 0) {
    return '금지된 어종이 검출되었습니다.';
  }
  return '경고 사항이 없습니다.';
});
</script>

<style scoped>
/* 컴포넌트별 스타일 정의 영역 */
</style>
