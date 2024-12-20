<template>
    <div class="min-h-screen bg-gray-100 flex justify-center">
        <div class="w-full max-w-4xl bg-white shadow-lg overflow-hidden rounded-lg">
            <main class="pb-20 px-4">
                <!-- 오늘의 물때 섹션 -->
                <section class="mb-6 pt-4">
                    <div class="flex justify-between items-center mb-3">
                        <router-link to="/map-location-service"
                            class="flex justify-between items-center p-2 w-full hover:bg-gray-50 rounded-lg transition">
                            <h2 class="text-lg font-medium mr-2">오늘의 물때</h2>
                            <ChevronRightIcon class="w-5 h-5 text-gray-400" />
                        </router-link>
                    </div>
                    <MulddaeWidget></MulddaeWidget>
                </section>

                <!-- 내가 잡은 물고기 섹션 -->
                <section v-if="isAuthenticated" class="mb-6 pt-4">
                    <div class="flex justify-between items-center mb-3">
                        <router-link to="/catches"
                            class="flex justify-between items-center p-2 w-full hover:bg-gray-50 rounded-lg transition">
                            <h2 class="text-lg font-medium mr-2">내가 잡은 물고기</h2>
                            <ChevronRightIcon class="w-5 h-5 text-gray-400" />
                        </router-link>
                    </div>
                    <div v-if="isLoadingCatches" class="text-center text-gray-500">
                        Loading...
                    </div>
                    <div v-else-if="displayedCatches.length > 0" 
                        ref="scrollContainer"
                        class="overflow-x-auto touch-pan-x relative group"
                        @mouseenter="stopAutoSlide"
                        @mouseleave="startAutoSlide">
                        <div class="flex space-x-4 transition-all duration-700 ease-in-out transform">
                            <div v-for="catchItem in displayedCatches" :key="catchItem.id"
                                class="bg-gray-50 p-4 rounded-lg shadow-sm flex-shrink-0 w-80 h-64">
                                <img :src="`${BACKEND_BASE_URL}/uploads/${catchItem.imageUrl}`" alt="Catch Image"
                                    class="w-full h-48 object-cover rounded-lg mb-2 cursor-pointer"
                                    @click="openImagePopup(catchItem.imageUrl)" />
                                <p class="text-gray-800 text-sm text-center">{{ catchItem.detections[0].label }}
                                </p>
                                <p class="text-gray-600 text-xs text-center mb-2">신뢰도: {{
                                    (catchItem.detections[0].confidence * 100).toFixed(2)
                                    }}%</p>
                            </div>
                        </div>
                        
                        <!-- 네비게이션 버튼 추가 -->
                        <button @click="scrollLeft"
                            class="absolute left-0 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-r hidden group-hover:block transition-opacity duration-300">
                            ←
                        </button>
                        <button @click="scrollRight"
                            class="absolute right-0 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-l hidden group-hover:block transition-opacity duration-300">
                            →
                        </button>
                    </div>
                    <div v-else class="text-gray-500 flex flex-col items-center p-2">아직 잡은 물고기가 없습니다.</div>
                </section>

                <!-- 오늘의 핫이슈 섹션 -->
                <section>
                    <div class="flex justify-between items-center mb-3">
                        <router-link to="/community"
                            class="flex justify-between items-center p-2 w-full hover:bg-gray-50 rounded-lg transition">
                            <h2 class="text-lg font-medium">오늘의 핫이슈</h2>
                            <ChevronRightIcon class="w-5 h-5 text-gray-400" />
                        </router-link>
                    </div>
                    <div class="space-y-3">
                        <article v-for="i in 5" :key="i"
                            class="bg-gray-50 rounded-lg p-4 shadow-sm hover:bg-gray-100 transition">
                            <div class="flex gap-3">
                                <div
                                    class="w-16 h-16 bg-gray-200 rounded flex items-center justify-center flex-shrink-0">
                                    <ImageIcon class="w-8 h-8 text-gray-400" />
                                </div>
                                <div class="flex-1">
                                    <h3 class="font-medium mb-1">게시물 제목</h3>
                                    <p class="text-sm text-gray-600 mb-2">게시 내용 미리보기입니다. 여기에 간단한 설명이 들어갑니다.</p>
                                    <div class="flex items-center text-sm text-gray-500">
                                        <ClockIcon class="w-4 h-4 mr-1" />
                                        <span>오늘 • 23분 전</span>
                                    </div>
                                </div>
                                <ChevronRightIcon class="w-5 h-5 text-gray-400" />
                            </div>
                        </article>
                    </div>
                </section>
            </main>
        </div>
    </div>
    <div v-if="isImagePopupVisible" class="fixed inset-0 bg-black bg-opacity-75 flex justify-center items-center z-30"
        @click="isImagePopupVisible = false">
        <div class="relative flex justify-center items-center" @click.stop>
            <img :src="popupImageUrl" alt="Popup Image"
                class="max-w-full max-h-full object-contain rounded-lg border border-gray-200 shadow-lg" />
            <button @click="isImagePopupVisible = false"
                class="absolute top-2 right-2 bg-white text-black rounded-full p-1 hover:bg-gray-200 transition-colors duration-300">
                &times;
            </button>
        </div>
    </div>
</template>

<script setup>
import {
    ChevronRightIcon,
    ImageIcon,
    ClockIcon,
} from 'lucide-vue-next'
import { onMounted, computed, ref, watch, onUnmounted } from "vue";
import { useStore } from "vuex";
import MulddaeWidget from '../components/MulddaeWidget.vue';

// Vuex 스토어 사용
const store = useStore();

// Define backend base URL
const BACKEND_BASE_URL = 'http://localhost:5000';

const isLoadingCatches = ref(false); // Add loading state

const isAuthenticated = computed(() => store.getters.isAuthenticated); // Use computed property for authentication status

// 컴포넌트가 마운트될 때 데이터 가져오기
onMounted(async () => {
    await store.dispatch('fetchInitialData');
    // 인증된 사용자의 경우 catches 데이터 업데이트
    if (isAuthenticated.value && catches.value.length > 0) {
        updateDisplayedCatches();
        startAutoSlide(); // 자동 슬라이드 시작
    }
});

// Vuex 스토어에서 잡은 물고기 데이터 가져오기
const catches = computed(() => store.getters.catches);

// 이미지 팝업 관련 상태
const isImagePopupVisible = ref(false);
const popupImageUrl = ref('');

// 잡은 물고기 섹션 관련 상태
const displayedCatches = ref([]);

function openImagePopup(imageUrl) {
    popupImageUrl.value = `${BACKEND_BASE_URL}/uploads/${imageUrl}`; // Updated to include BACKEND_BASE_URL
    isImagePopupVisible.value = true;
}

function updateDisplayedCatches() {
    const sortedCatches = catches.value.slice().reverse();
    displayedCatches.value = sortedCatches;
}

// catches 데이터가 변경될 때마다 displayed catches 업데이트
watch(() => catches.value, () => {
    if (catches.value.length > 0) {
        updateDisplayedCatches();
    }
}, { immediate: true });

// script 부분에 새로운 ref와 함수 추가
const autoSlideInterval = ref(null);
const scrollContainer = ref(null);

// 자동 슬라이드 시작 함수
function startAutoSlide() {
    if (!autoSlideInterval.value) {
        autoSlideInterval.value = setInterval(() => {
            if (scrollContainer.value) {
                const container = scrollContainer.value;
                const scrollAmount = 335; // 카드 너비 + 간격
                
                if (container.scrollLeft + container.clientWidth >= container.scrollWidth) {
                    // 끝에 도달하면 부드럽게 처음으로 돌아가기
                    container.scrollTo({
                        left: 0,
                        behavior: 'smooth'
                    });
                } else {
                    // 부드럽게 다음 슬라이드로 이동
                    container.scrollTo({
                        left: container.scrollLeft + scrollAmount,
                        behavior: 'smooth'
                    });
                }
            }
        }, 1700); // 시간 간격 늘림
    }
}

// 자동 슬라이드 정지 함수
function stopAutoSlide() {
    if (autoSlideInterval.value) {
        clearInterval(autoSlideInterval.value);
        autoSlideInterval.value = null;
    }
}

// 컴포넌트 언마운트 시 자동 슬라이드 정지
onUnmounted(() => {
    stopAutoSlide();
});

// 네비게이션 버튼 클릭 핸들러도 수정
function scrollLeft() {
    if (scrollContainer.value) {
        scrollContainer.value.scrollTo({
            left: scrollContainer.value.scrollLeft - 320,
            behavior: 'smooth'
        });
    }
}

function scrollRight() {
    if (scrollContainer.value) {
        scrollContainer.value.scrollTo({
            left: scrollContainer.value.scrollLeft + 320,
            behavior: 'smooth'
        });
    }
}

</script>

<style lang="css" scoped>
* {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

*::-webkit-scrollbar {
    display: none;
}

.touch-pan-x {
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
}

.scroll-smooth {
    scroll-behavior: smooth;
}

.hover\:bg-gray-50:hover {
    background-color: #f9fafb;
}

.hover\:bg-gray-100:hover {
    background-color: #f3f4f6;
}

.transition {
    transition: background-color 0.3s ease;
}

.transition-all {
    transition: all 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

.group:hover .group-hover\:block {
    display: block;
}

.transform {
    will-change: transform;
}
</style>
