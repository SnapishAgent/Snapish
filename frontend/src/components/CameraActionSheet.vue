<!-- filepath: /c:/Users/twoimo/Documents/GitHub/Snapish/frontend/src/components/CameraActionSheet.vue -->
<template>
    <!-- 액션 시트 모달 -->
    <div v-if="props.isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-end justify-center z-20"
        @click="closeActionSheet">
        <!-- 모달 콘텐츠 -->
        <div class="bg-white w-full max-w-sm rounded-t-xl" @click.stop>
            <div class="p-4">
                <!-- 제목 -->
                <h2 class="text-lg font-semibold text-center mb-4">사진 업로드</h2>
                <div class="space-y-2">
                    <!-- 옵션 버튼들 -->
                    <button v-for="(option, index) in options" :key="index"
                        class="w-full py-3 px-4 text-center text-blue-500 bg-white hover:bg-gray-50 border-b last:border-b-0"
                        @click="handleOption(option.action)">
                        {{ option.text }}
                    </button>
                </div>
                <!-- 취소 버튼 -->
                <button class="w-full py-3 px-4 text-center text-red-500 font-medium mt-2" @click="closeActionSheet">
                    취소
                </button>
            </div>
        </div>
    </div>

    <!-- 숨겨진 파일 입력 요소들 -->
    <input ref="cameraInput" type="file" accept="image/*" capture="environment" style="display: none;"
        @change="onFileChange" />
    <input ref="galleryInput" type="file" accept="image/*" style="display: none;" @change="onFileChange" />
    <input ref="fileInput" type="file" accept="*/*" style="display: none;" @change="onFileChange" />
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

// Props 정의
const props = defineProps({
    isOpen: {
        type: Boolean,
        required: true,
    },
});

// Emits 정의
const emit = defineEmits(['close']);

// Router 인스턴스
const router = useRouter();

// 파일 입력 요소에 대한 참조 정의
const cameraInput = ref(null);
const galleryInput = ref(null);
const fileInput = ref(null);

// 옵션 목록
const options = [
    { text: '사진 촬영', action: 'camera' },
    { text: '갤러리에서 선택', action: 'gallery' },
    { text: '파일 선택', action: 'file' },
];

// 액션 시트를 닫기 위한 함수
const closeActionSheet = () => {
    emit('close');
};

// 옵션 클릭 시 실행되는 함수
const handleOption = (action) => {
    console.log('Option selected:', action); // 로그 추가
    closeActionSheet();

    if (action === 'camera') {
        if (cameraInput.value) {
            cameraInput.value.click();
        } else {
            console.error('cameraInput is not available');
        }
    } else if (action === 'gallery') {
        if (galleryInput.value) {
            galleryInput.value.click();
        } else {
            console.error('galleryInput is not available');
        }
    } else if (action === 'file') {
        if (fileInput.value) {
            fileInput.value.click();
        } else {
            console.error('fileInput is not available');
        }
    }
};

// 파일 선택 시 실행되는 함수
const onFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
        const imageUrl = URL.createObjectURL(file);
        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await axios.post('http://localhost:5000/backend/predict', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            const detections = response.data.detections;

            // detections을 JSON 문자열로 변환 후 URL 인코딩
            router.push({
                name: 'FishResultNormal',
                query: {
                    detections: JSON.stringify(detections),
                    imageUrl,
                },
            });
        } catch (error) {
            console.error('Error during Axios POST:', error);
            alert('이미지 업로드 중 오류가 발생했습니다.');
        }
    }
};
</script>

<style scoped>
.fixed.inset-0 {
    /* 모달 배경 스타일 */
    display: flex;
    align-items: flex-end;
    justify-content: center;
}

.bg-black.bg-opacity-50 {
    /* 반투명 검은색 배경 */
    background-color: rgba(0, 0, 0, 0.5);
}

.bg-white {
    /* 흰색 배경 */
    background-color: white;
}

.rounded-t-xl {
    /* 모서리 라운딩 */
    border-top-left-radius: 1rem;
    border-top-right-radius: 1rem;
}

.border-b {
    /* 하단 경계선 */
    border-bottom: 1px solid #e5e7eb;
    /* Tailwind의 gray-200 */
}

.last\:border-b-0 {
    /* 마지막 요소의 하단 경계선 제거 */
    border-bottom: none;
}

.text-blue-500:hover {
    /* 텍스트 및 배경 호버 스타일 */
    color: #3b82f6;
    /* Tailwind의 blue-500 */
    background-color: #f3f4f6;
    /* Tailwind의 gray-100 */
}

.text-red-500 {
    /* 취소 버튼 색상 */
    color: #ef4444;
    /* Tailwind의 red-500 */
}

.space-y-2>*+* {
    /* 버튼 간 간격 */
    margin-top: 0.5rem;
}
</style>