<template>
  <div :class="['fixed bottom-0 left-0 right-0 max-w-md mx-auto z-10', $attrs.class]">
    <nav class="bg-white border-t px-6 py-2">
      <div class="flex justify-between items-center">
        <!-- 메인 화면 링크 -->
        <router-link to="/" class="flex flex-col items-center p-2" active-class="active-link">
          <HomeIcon class="w-6 h-6" />
          <span class="text-xs mt-1">메인 화면</span>
        </router-link>

        <!-- 사진 찍기 버튼 -->
        <button @click="openCameraActions" class="flex flex-col items-center p-2">
          <CameraIcon class="w-6 h-6" />
          <span class="text-xs mt-1">사진 찍기</span>
        </button>

        <!-- 프로필 링크 -->
        <router-link to="/profile" class="flex flex-col items-center p-2" active-class="active-link">
          <UserIcon class="w-6 h-6" />
          <span class="text-xs mt-1">프로필</span>
        </router-link>
      </div>
    </nav>

    <!-- CameraActionSheet 컴포넌트 -->
    <CameraActionSheet :isOpen="showCameraActions" @close="closeCameraActions" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { HomeIcon, CameraIcon, UserIcon } from 'lucide-vue-next';
import CameraActionSheet from '../CameraActionSheet.vue';
import store from '../../store';

const emit = defineEmits(['toggleCameraActions']);

const showCameraActions = ref(false);

const openCameraActions = () => {
  showCameraActions.value = true;
  emit('toggleCameraActions');

  if (store.state.isAuthenticated) {
    // Additional actions for authenticated users if needed
  } else {
    // Additional actions for unauthenticated users if needed
  }
};

const closeCameraActions = () => {
  showCameraActions.value = false;
};
</script>

<style scoped>
.upload-button {
  /* 버튼 스타일 정의 */
  padding: 12px 24px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.upload-button:hover {
  background-color: #66b1ff;
}

.active-link {
  /* 활성화된 링크 스타일 (필요 시 정의) */
  color: #409eff;
}
</style>