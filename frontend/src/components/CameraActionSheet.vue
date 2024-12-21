<template>
    <!-- 액션 시트 모달 -->
    <div v-if="props.isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-end justify-center z-[100]"
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
import { ref } from 'vue';
import axios from '../axios'; // Ensure this is the correct path to your Axios instance
import { useRouter } from 'vue-router';
import store from '../store'; // Vuex store 임포트

// eslint-disable-next-line no-undef
const props = defineProps({
    isOpen: {
        type: Boolean,
        required: true,
    },
});

// eslint-disable-next-line no-undef
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
        try {
            // 전역 로딩 상태 활성화
            store.dispatch('setGlobalLoading', true);
            
            const token = localStorage.getItem('token');
            if (token) {
                const formData = new FormData();
                formData.append('image', file);

                const response = await axios.post('/backend/predict', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        'Authorization': `Bearer ${token}`,
                    },
                    withCredentials: true,
                });
                await handlePredictResponse(response.data);
            } else {
                const reader = new FileReader();
                reader.onload = async () => {
                    const image_base64 = reader.result.split(',')[1];
                    try {
                        const response = await axios.post('/backend/predict', {
                            image_base64,
                        });
                        await handlePredictResponse(response.data);
                    } catch (error) {
                        console.error('Error during Axios POST:', error);
                        alert('이미지 업로드 중 오류가 발생했습니다.');
                    }
                };
                reader.readAsDataURL(file);
            }
        } catch (error) {
            console.error('Error during file upload:', error);
            alert('이미지 업로드 중 오류가 발생했습니다.');
        } finally {
            // 전역 로딩 상태 비활성화
            store.dispatch('setGlobalLoading', false);
        }
    }
};

const handlePredictResponse = async (data) => {
    const detections = data.detections;
    const imageUrl = data.imageUrl || null;
    const imageBase64 = data.image_base64 || null;

    if (detections && detections.length > 0) {
        const currentDate = new Date();
        const currentMonthDay = `${(currentDate.getMonth() + 1).toString().padStart(2, '0')}.${currentDate.getDate().toString().padStart(2, '0')}`;

        console.log('현재 날짜:', currentMonthDay); // 현재 날짜 확인

        const isProhibited = detections.some(detection => {
            const prohibitedDates = detection.prohibited_dates; // 금어기 날짜 가져오기
            console.log('감지된 물고기:', detection.label); // 감지된 물고기 확인
            console.log('금어기 날짜:', prohibitedDates); // 금어기 날짜 확인

            if (!prohibitedDates) return false;

            const [start, end] = prohibitedDates.split('~');
            console.log('시작 날짜:', start, '종료 날짜:', end); // 시작 및 종료 날짜 확인

            // 금어기 날짜 비교 로직 수정
            if (end.startsWith('01.')) {
                // 종료 날짜가 다음 해의 날짜인 경우
                return (currentMonthDay >= start || currentMonthDay <= end);
            } else {
                // 일반적인 경우
                return currentMonthDay >= start && currentMonthDay <= end;
            }
        });

        console.log('금어기 여부:', isProhibited); // 금어기 여부 확인

        const routeName = isProhibited ? 'FishResultWarning' : 'FishResultNormal';

        if (store.state.isAuthenticated) {
            await store.dispatch('fetchCatches');
            router.push({
                name: routeName,
                query: {
                    imageUrl,
                    imageBase64,
                    detections: encodeURIComponent(JSON.stringify(detections)),
                    prohibitedDates: detections[0].prohibited_dates || '알 수 없음',
                    timestamp: Date.now()
                },
            });
        } else {
            router.push({
                name: routeName,
                query: {
                    imageBase64,
                    detections: encodeURIComponent(JSON.stringify(detections)),
                    prohibitedDates: detections[0].prohibited_dates || '알 수 없음',
                    timestamp: Date.now()
                },
            });
        }
    } else {
        alert('알 수 없는 물고기입니다.');
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
    /* Tailwind gray-200 */
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