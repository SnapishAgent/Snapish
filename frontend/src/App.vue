<template>
  <div class="min-h-screen bg-gray-100 flex justify-center">
    <div class="w-full max-w-md bg-white shadow-lg relative">
      <!-- 상단 헤더 -->
      <Header v-if="!hideHeader" class="fixed top-0 left-0 right-0 z-10 max-w-md mx-auto" />
      <div class="pt-16 pb-16">
        <router-view></router-view>
      </div>
      <!-- 하단 네비게이션 -->
      <BottomNavigation @toggleCameraActions="showCameraActions = true"
        class="fixed bottom-0 left-0 right-0 max-w-md mx-auto z-10" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import BottomNavigation from './components/layout/BottomNavigation.vue';
import Header from './components/layout/Header.vue';

// 현재 라우트 확인
const route = useRoute();

// 특정 경로에서만 헤더 숨기기
const hideHeader = computed(() => /^\/(fish-result)/.test(route.path));
</script>

<style>
body {
  /* eslint-disable-next-line */
  @apply antialiased text-gray-900 bg-gray-100;
}

.active-link {
  color: #1d4ed8;
  /* 선호하는 활성화 색상으로 변경 */
}

.pt-16 {
  padding-top: 4rem;
  /* Adjust according to the height of your header */
}

.pb-16 {
  padding-bottom: 4rem;
  /* Adjust according to the height of your bottom navigation */
}
</style>
