<template>
    <div class="min-h-screen bg-gray-100 flex justify-center">
        <div class="w-full max-w-4xl bg-white shadow-lg overflow-hidden rounded-lg">
            <main class="pb-20 px-4">
                <!-- 로딩 상태 -->
                <div v-if="loading" class="fixed inset-0 flex justify-center items-center bg-white bg-opacity-75 z-50">
                    <div class="flex flex-col items-center">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
                        <span class="text-sm text-gray-500">로딩중...</span>
                    </div>
                </div>

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
                                <img :src="`${BACKEND_BASE_URL}/uploads/${catchItem.imageUrl}`" 
                                    alt="Catch Image"
                                    class="w-full h-48 object-cover rounded-lg mb-2 cursor-pointer"
                                    @click="openImagePopup(catchItem.imageUrl)" />
                                <p class="text-gray-800 text-sm text-center">
                                    {{ catchItem.detections[0].label }}
                                </p>
                                <p class="text-gray-600 text-xs text-center mb-2">
                                    신뢰도: {{ (catchItem.detections[0].confidence * 100).toFixed(2) }}%
                                </p>
                            </div>
                        </div>
                        
                        <!-- 네비게이션 버튼 수정 -->
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
                        <article v-for="issue in hotIssues" :key="issue.id"
                            class="bg-gray-50 rounded-lg p-4 shadow-sm hover:bg-gray-100 transition cursor-pointer">
                            <div class="flex gap-3">
                                <div
                                    class="w-20 h-20 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                                    <img 
                                        :src="issue.imageUrl" 
                                        :alt="issue.title"
                                        class="w-full h-full object-cover"
                                        @error="$event.target.src = DEFAULT_IMAGE"
                                    />
                                </div>
                                <div class="flex-1">
                                    <h3 class="font-medium mb-1 text-blue-900">{{ issue.title }}</h3>
                                    <p class="text-sm text-gray-600 mb-2">{{ issue.content }}</p>
                                    <div class="flex items-center justify-between text-sm text-gray-500">
                                        <span class="font-medium text-gray-600">{{ issue.author }}</span>
                                        <div class="flex items-center">
                                            <ClockIcon class="w-4 h-4 mr-1" />
                                            <span>{{ formatTimestamp(issue.timestamp) }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </article>
                    </div>
                </section>
            </main>
        </div>
    </div>
    <div v-if="isImagePopupVisible"
        class="fixed inset-0 bg-black bg-opacity-90 flex justify-center items-center z-50 p-4"
        @click="isImagePopupVisible = false">
        <div class="relative w-full max-w-4xl max-h-[90vh] flex items-center justify-center" @click.stop>
            <div class="relative">
                <img 
                    :src="popupImageUrl" 
                    alt="Popup Image"
                    class="w-auto h-auto max-w-full max-h-[85vh] rounded-lg shadow-xl object-contain"
                />
                <button 
                    @click="isImagePopupVisible = false"
                    class="absolute top-4 right-4 p-2 bg-white rounded-full hover:bg-gray-100 transition-colors shadow-lg"
                >
                    <X class="w-5 h-5 text-gray-600" />
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import {
    ChevronRightIcon,
    ClockIcon,
    X,
} from 'lucide-vue-next'
import { onMounted, computed, ref, watch, onUnmounted } from "vue";
import { useStore } from "vuex";
import MulddaeWidget from '../components/MulddaeWidget.vue';

// Vuex 스토어 사용
const store = useStore();

// Define backend base URL
const BACKEND_BASE_URL = 'http://localhost:5000';

const loading = ref(true);
const isLoadingCatches = ref(false);
const isAuthenticated = computed(() => store.getters.isAuthenticated);

// 컴포넌트가 마운트될 때 데이터 가져오기
onMounted(async () => {
    try {
        loading.value = true;
        await store.dispatch('fetchInitialData');
        if (isAuthenticated.value && catches.value.length > 0) {
            updateDisplayedCatches();
            startAutoSlide();
        }
    } catch (error) {
        console.error('Error:', error);
    } finally {
        loading.value = false;
    }
});

// 컴포넌트 언마운트 시 자동 슬라이드 정지
onUnmounted(() => {
    stopAutoSlide();
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
    // 모든 catches를 표시하도록 수정
    const sortedCatches = catches.value.slice().reverse();
    displayedCatches.value = sortedCatches;
}

// catches 데이터가 변경될 때마다 displayed catches 업데이트
watch(() => catches.value, () => {
    if (catches.value.length > 0) {
        updateDisplayedCatches();
    }
}, { immediate: true });

// 자동 슬라이드 관련 상태
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
        }, 1900); // 시간 간격 늘림
    }
}

// 자동 슬라이드 정지 함수
function stopAutoSlide() {
    if (autoSlideInterval.value) {
        clearInterval(autoSlideInterval.value);
        autoSlideInterval.value = null;
    }
}

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

// Vuex store에서 핫이슈 데이터 가져오기
const hotIssues = computed(() => store.getters.hotIssues);

// 타임스탬프 포맷팅 함수
function formatTimestamp(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 60) {
        return `${diffInMinutes}분 전`;
    } else if (diffInMinutes < 1440) {
        return `${Math.floor(diffInMinutes / 60)}시간 전`;
    } else {
        return date.toLocaleDateString();
    }
}

// 기본 이미지 (Community.vue와 동일한 DEFAULT_IMAGE 사용)
const DEFAULT_IMAGE = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgZmlsbD0iI2YzZjRmNiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjAiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7snbTrr7jsp4Ag7JeG7J2EPC90ZXh0Pjwvc3ZnPg==';

</script>

<style lang="css" scoped>
/* 기존 스타일은 유지하고 transition 관련 스타일 수정 */
.transition-all {
    transition: all 0.7s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 슬라이드 컨테이너에 스무스 스크롤 추가 */
.touch-pan-x {
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
}

/* 추가적인 애니메이션 부드러움을 위한 스타일 */
.transform {
    will-change: transform;
}
</style>
