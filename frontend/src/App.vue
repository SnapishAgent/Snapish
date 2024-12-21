<template>
  <div class="min-h-screen bg-gray-100 flex justify-center">
    <div class="w-full max-w-sm md:max-w-md bg-white shadow-lg relative touch-manipulation">
      <Header v-if="!hideHeader" class="fixed top-0 left-0 right-0 z-10 max-w-sm md:max-w-md mx-auto" />
      <div class="pt-14 pb-14 overflow-y-auto overscroll-contain">
        <router-view></router-view>
      </div>
      <BottomNavigation @toggleCameraActions="handleToggleCameraActions"
        class="fixed bottom-0 left-0 right-0 max-w-sm md:max-w-md mx-auto z-10" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import BottomNavigation from './components/layout/BottomNavigation.vue';
import Header from './components/layout/Header.vue';
import store from './store'; // Import the store

// 현재 라우트 확인
const route = useRoute();

// 특정 경로에서만 헤더 숨기기
const hideHeader = computed(() => /^\/(fish-result)/.test(route.path));

const handleToggleCameraActions = () => {
  // This function can be used to trigger image upload actions based on auth
  // For example, you might open different modals or handle differently
  if (store.state.isAuthenticated) {
    // Handle authenticated user actions
  } else {
    // Handle unauthenticated user actions
  }
};

</script>

<style>
/* 모바일 터치 최적화 */
* {
  -webkit-tap-highlight-color: transparent;
}

/* 모바일 스크롤 최적화 */
.overflow-y-auto {
  -webkit-overflow-scrolling: touch;
}

/* 모바일 폰트 최적화 */
body {
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 반응형 미디어 쿼리 */
@media (min-width: 768px) {
  .md\:max-w-md {
    max-width: 448px;
  }
}

body {
  /* ...existing styles... */
}

.active-link {
  color: #1d4ed8;
  /* ...existing styles... */
}

.pt-16 {
  padding-top: 4rem;
  /* ...existing styles... */
}

.pb-16 {
  padding-bottom: 4rem;
  /* ...existing styles... */
}
</style>