<template>
  <div class="min-h-screen bg-gray-100 flex justify-center">
    <div class="w-full max-w-md bg-white shadow-lg relative">
      <!-- 상단 헤더 -->
      <Header v-if="!hideHeader" class="fixed top-0 left-0 right-0 z-10 max-w-md mx-auto" />
      <div class="pt-14 pb-14">
        <router-view></router-view>
      </div>
      <!-- 하단 네비게이션 -->
      <BottomNavigation @toggleCameraActions="handleToggleCameraActions"
        class="fixed bottom-0 left-0 right-0 max-w-md mx-auto z-10" />
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