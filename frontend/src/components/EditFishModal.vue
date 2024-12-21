<template>
  <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-6 rounded-lg shadow-xl max-w-lg w-full mx-4">
      <h2 class="text-xl font-bold mb-4">물고기 정보 수정</h2>
      
      <div v-if="errorMessage" class="mb-4 p-3 bg-red-100 text-red-700 rounded">
        {{ errorMessage }}
      </div>
      
      <form @submit.prevent="saveFishData" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">물고기 이름</label>
          <input 
            v-model="fishData.name" 
            type="text" 
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">무게 (kg)</label>
            <input 
              v-model="fishData.weight_kg" 
              type="number" 
              step="0.001"
              min="0"
              max="999.999"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">길이 (cm)</label>
            <input 
              v-model="fishData.length_cm" 
              type="number" 
              step="0.01"
              min="0"
              max="999.99"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">위도</label>
            <input 
              v-model="fishData.latitude" 
              type="number" 
              step="0.000001"
              min="-90"
              max="90"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">경도</label>
            <input 
              v-model="fishData.longitude" 
              type="number" 
              step="0.000001"
              min="-180"
              max="180"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">메모</label>
          <textarea 
            v-model="fishData.memo" 
            rows="3"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          ></textarea>
        </div>

        <div class="flex justify-end gap-4 mt-6">
          <button 
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            취소
          </button>
          <button 
            type="submit"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            저장
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useStore } from 'vuex';

const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true
  },
  catchData: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'save']);
const store = useStore();
const errorMessage = ref('');

const fishData = ref({
  name: '',
  weight_kg: null,
  length_cm: null,
  latitude: null,
  longitude: null,
  memo: ''
});

onMounted(() => {
  if (props.catchData) {
    fishData.value = {
      name: props.catchData.detections[0].label,
      weight_kg: props.catchData.weight_kg,
      length_cm: props.catchData.length_cm,
      latitude: props.catchData.latitude,
      longitude: props.catchData.longitude,
      memo: props.catchData.memo
    };
  }
});

const saveFishData = async () => {
  try {
    errorMessage.value = '';

    if (!props.catchData || !props.catchData.id) {
      console.error('Invalid catch data:', props.catchData);
      errorMessage.value = '물고기 정보가 올바르지 않습니다.';
      return;
    }

    if (fishData.value.weight_kg && (fishData.value.weight_kg < 0 || fishData.value.weight_kg > 999.999)) {
      errorMessage.value = '무게는 0에서 999.999kg 사이여야 합니다.';
      return;
    }
    if (fishData.value.length_cm && (fishData.value.length_cm < 0 || fishData.value.length_cm > 999.99)) {
      errorMessage.value = '길이는 0에서 999.99cm 사이여야 합니다.';
      return;
    }
    if (fishData.value.latitude && (fishData.value.latitude < -90 || fishData.value.latitude > 90)) {
      errorMessage.value = '위도는 -90에서 90도 사이여야 합니다.';
      return;
    }
    if (fishData.value.longitude && (fishData.value.longitude < -180 || fishData.value.longitude > 180)) {
      errorMessage.value = '경도는 -180에서 180도 사이여야 합니다.';
      return;
    }

    const catch_date = props.catchData.catch_date || new Date().toISOString().split('T')[0];

    const updatedData = {
      id: props.catchData.id,
      ...props.catchData,
      detections: [{
        ...props.catchData.detections[0],
        label: fishData.value.name
      }],
      catch_date,
      weight_kg: fishData.value.weight_kg,
      length_cm: fishData.value.length_cm,
      latitude: fishData.value.latitude,
      longitude: fishData.value.longitude,
      memo: fishData.value.memo
    };

    const response = await store.dispatch('updateCatch', updatedData);
    emit('save', response);
    emit('close');
  } catch (error) {
    console.error('Error saving fish data:', error);
    errorMessage.value = error.response?.data?.error || '물고기 정보 저장에 실패했습니다.';
  }
};
</script> 