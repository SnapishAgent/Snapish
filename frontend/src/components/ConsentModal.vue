<template>
  <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-6 rounded-lg shadow-xl max-w-lg w-full mx-4">
      <h2 class="text-xl font-bold mb-4">데이터 수집 동의</h2>
      
      <div class="mb-6 text-gray-700">
        <p class="mb-4">본 서비스는 다음과 같은 데이터를 수집하고 활용합니다:</p>
        <ul class="list-disc list-inside mb-4">
          <li>물고기 이미지 및 관련 메타데이터</li>
          <li>위치 정보 (위도/경도)</li>
          <li>물고기 크기 및 무게 정보</li>
          <li>사용자 입력 메모</li>
        </ul>
        <p class="mb-4">수집된 데이터는 다음 목적으로 활용됩니다:</p>
        <ul class="list-disc list-inside mb-4">
          <li>서비스 품질 개선</li>
          <li>AI 모델 학습 및 개선</li>
          <li>어족 자원 보호 및 연구</li>
        </ul>
        <p class="text-sm text-gray-500 mb-4">
          * 수집된 개인정보는 관련 법령에 따라 안전하게 보호되며, 
          동의하지 않으실 경우 서비스 이용이 제한될 수 있습니다.
        </p>
      </div>

      <div class="flex justify-end gap-4">
        <button 
          @click="decline" 
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
        >
          거부
        </button>
        <button 
          @click="accept" 
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          동의
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

defineProps({
  isVisible: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close', 'consent']);
const store = useStore();
const router = useRouter();

const accept = async () => {
  try {
    await store.dispatch('updateConsent', true);
    emit('consent', true);
    emit('close');
  } catch (error) {
    console.error('Error updating consent:', error);
  }
};

const decline = () => {
  emit('consent', false);
  emit('close');
  router.push('/'); // 메인 페이지로 이동
};
</script> 