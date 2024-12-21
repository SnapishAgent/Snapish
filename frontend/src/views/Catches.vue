<template>
    <div class="min-h-screen bg-gray-50">
        <!-- 상단 검색/필터 영역 -->
        <div class="sticky top-0 bg-white shadow-sm z-10 px-4 py-3">
            <div class="max-w-4xl mx-auto">
                <div class="flex flex-col sm:flex-row gap-3">
                    <div class="relative flex-grow">
                        <input 
                            type="text" 
                            v-model="searchQuery" 
                            placeholder="물고기 검색..." 
                            class="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                        />
                        <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    </div>
                    <div class="flex gap-2">
                        <select 
                            v-model="sortOption" 
                            class="px-4 py-2 rounded-lg border border-gray-200 bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors cursor-pointer"
                        >
                        <option value="latest">최신순</option>
                        <option value="oldest">오래된순</option>
                    </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- 메인 콘텐츠 영역 -->
        <main class="max-w-4xl mx-auto px-4 py-6">
            <!-- 초기 로딩 상태 -->
            <div v-if="loading" class="fixed inset-0 flex justify-center items-center bg-white bg-opacity-75 z-50">
                <div class="flex flex-col items-center">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
                    <span class="text-sm text-gray-500">로딩중...</span>
                </div>
            </div>

            <!-- 데이터 없음 상태 -->
            <div v-else-if="!filteredCatches.length" class="flex flex-col items-center justify-center py-12 text-gray-500">
                <Fish class="w-16 h-16 mb-4 text-gray-300" />
                <p class="text-lg">아직 잡은 물고기가 없습니다.</p>
                <p class="text-sm mt-2">물고기를 잡아서 추억을 기록해보세요!</p>
            </div>

            <!-- 물고기 목록 -->
            <div v-else>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div v-for="catchItem in filteredCatches" 
                        :key="catchItem.id"
                        class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden"
                    >
                        <!-- 이미지 섹션 -->
                        <div class="relative aspect-[4/3] overflow-hidden bg-gray-100">
                            <img 
                                :src="`${BACKEND_BASE_URL}/uploads/${catchItem.imageUrl}`" 
                                alt="Catch Image"
                                class="w-full h-full object-cover cursor-pointer hover:scale-105 transition-transform duration-300"
                                @click="openImagePopup(catchItem.imageUrl)"
                            />
                        </div>

                        <!-- 정보 섹션 -->
                        <div class="p-4">
                            <div class="flex items-center justify-between mb-2">
                                <h3 class="text-lg font-semibold text-gray-800">
                                    {{ catchItem.detections[0].label }}
                                </h3>
                                <div class="flex gap-2">
                                    <button 
                                        @click="openEditModal(catchItem)"
                                        class="p-1.5 rounded-full hover:bg-gray-100 transition-colors"
                                    >
                                        <Edit class="w-4 h-4 text-blue-500" />
                                    </button>
                                    <button 
                                        @click="confirmDelete(catchItem.id)"
                                        class="p-1.5 rounded-full hover:bg-gray-100 transition-colors"
                                    >
                                        <Trash class="w-4 h-4 text-red-500" />
                                    </button>
                                </div>
                            </div>

                            <div class="space-y-1.5">
                                <div class="flex items-center text-sm text-gray-600">
                                    <Calendar class="w-4 h-4 mr-2" />
                                    {{ catchItem.catch_date }}
                                </div>
                                <div class="flex items-center text-sm text-gray-600">
                                    <Target class="w-4 h-4 mr-2" />
                                    신뢰도: {{ (catchItem.detections[0].confidence * 100).toFixed(2) }}%
                                </div>
                                <div v-if="catchItem.weight_kg || catchItem.length_cm" class="flex items-center text-sm text-gray-600">
                                    <Scale class="w-4 h-4 mr-2" />
                                    <span v-if="catchItem.weight_kg">{{ catchItem.weight_kg }}kg</span>
                                    <span v-if="catchItem.weight_kg && catchItem.length_cm" class="mx-2">|</span>
                                    <span v-if="catchItem.length_cm">{{ catchItem.length_cm }}cm</span>
                                </div>
                                <div v-if="catchItem.memo" class="flex items-start text-sm text-gray-600">
                                    <FileText class="w-4 h-4 mr-2 mt-0.5" />
                                    <p class="line-clamp-2">{{ catchItem.memo }}</p>
                        </div>
                        </div>
                        </div>
                    </div>
                </div>

                <!-- 추가 로딩 인디케이터 -->
                <div v-if="isLoadingMore" class="fixed inset-0 flex justify-center items-center bg-white bg-opacity-75 z-50">
                    <div class="flex flex-col items-center">
                        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mb-2"></div>
                        <span class="text-sm text-gray-500">물이터를 불러오는 중...</span>
                    </div>
                </div>

                <!-- 더 보기 트리거 -->
                <div v-if="hasMoreItems" 
                    ref="loadMoreTrigger" 
                    class="h-10 mt-6">
                </div>
            </div>
        </main>

        <!-- 모달 컴포넌트들 -->
        <EditFishModal
            v-if="showEditModal"
            :isVisible="showEditModal"
            :catchData="selectedCatch"
            @close="showEditModal = false"
            @save="handleFishDataSave"
        />

        <!-- 이미지 팝업 -->
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
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import { Edit, Trash, Search, Fish, Calendar, Target, Scale, FileText, X } from 'lucide-vue-next';
import EditFishModal from '../components/EditFishModal.vue';

const store = useStore();
const catches = computed(() => store.getters.catches || []);
const loading = ref(true);
const showEditModal = ref(false);
const selectedCatch = ref(null);
const initialLoad = 2;
const itemsToLoad = 2;
const displayCount = ref(initialLoad);
const loadMoreTrigger = ref(null);
const isImagePopupVisible = ref(false);
const popupImageUrl = ref('');
const searchQuery = ref('');
const sortOption = ref('latest');
const isLoadingMore = ref(false);

// Define backend base URL
const BACKEND_BASE_URL = 'http://localhost:5000';

let observer = null;

const totalFilteredItems = computed(() => {
    if (!catches.value) return 0;
    const filtered = catches.value.filter(catchItem => 
        catchItem.detections[0].label.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
    return filtered.length;
});

const hasMoreItems = computed(() => {
    return displayCount.value < totalFilteredItems.value;
});

const filteredCatches = computed(() => {
    if (!catches.value) return [];
    const allFilteredCatches = catches.value.filter(catchItem => {
        return catchItem.detections[0].label.toLowerCase().includes(searchQuery.value.toLowerCase());
    });

    const sortedCatches = sortOption.value === 'latest'
        ? allFilteredCatches.sort((a, b) => new Date(b.catch_date) - new Date(a.catch_date))
        : allFilteredCatches.sort((a, b) => new Date(a.catch_date) - new Date(b.catch_date));
    
    return sortedCatches.slice(0, displayCount.value);
});

onMounted(async () => {
    if (store.getters.isAuthenticated) {
        try {
            loading.value = true;
            await store.dispatch('fetchCatches');
            displayCount.value = initialLoad;
            nextTick(() => {
                setupIntersectionObserver();
            });
        } catch (error) {
            console.error('Error fetching catches:', error);
        } finally {
            loading.value = false;
        }
    } else {
        loading.value = false;
    }
});

function setupIntersectionObserver() {
    if (observer) {
        observer.disconnect();
    }

    observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !isLoadingMore.value && hasMoreItems.value) {
            console.log('Loading more items...', {
                currentCount: displayCount.value,
                totalItems: totalFilteredItems.value
            });
            loadMoreCatches();
        }
    }, {
        root: null,
        rootMargin: '50px',
        threshold: 0
    });

    nextTick(() => {
        if (loadMoreTrigger.value) {
            observer.observe(loadMoreTrigger.value);
        }
    });
}

function preloadImage(url) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(url);
        img.onerror = () => reject(url);
        img.src = url;
    });
}

function loadMoreCatches() {
    if (isLoadingMore.value) return;
    isLoadingMore.value = true;

    const loadNextBatch = async () => {
        if (!catches.value || !catches.value.length) {
            isLoadingMore.value = false;
            return;
        }

        const allFilteredCatches = catches.value.filter(catchItem => 
            catchItem.detections[0].label.toLowerCase().includes(searchQuery.value.toLowerCase())
        );

        const sortedCatches = sortOption.value === 'latest'
            ? allFilteredCatches.sort((a, b) => new Date(b.catch_date) - new Date(a.catch_date))
            : allFilteredCatches.sort((a, b) => new Date(a.catch_date) - new Date(b.catch_date));

        const nextItems = sortedCatches.slice(
            displayCount.value,
            displayCount.value + itemsToLoad
        );

        if (nextItems.length === 0) {
            isLoadingMore.value = false;
            return;
        }

        try {
            const imagePromises = nextItems.map(item => 
                preloadImage(`${BACKEND_BASE_URL}/uploads/${item.imageUrl}`)
            );

            await Promise.allSettled(imagePromises);

            console.log('Adding more items:', {
                before: displayCount.value,
                adding: itemsToLoad,
                after: displayCount.value + itemsToLoad,
                nextItemsCount: nextItems.length
            });
            displayCount.value += itemsToLoad;

            nextTick(() => {
                setupIntersectionObserver();
            });
        } catch (error) {
            console.error('Error loading images:', error);
        } finally {
            isLoadingMore.value = false;
        }
    };

    loadNextBatch();
}

function openEditModal(catchItem) {
    console.log("Opening edit modal for:", catchItem);
    if (!catchItem.id) {
        console.error("Cannot open edit popup: 'id' is undefined.");
        alert("수정할 수 없는 항목입니다: 식별자가 없습니다.");
        return;
    }
    selectedCatch.value = { ...catchItem };
    selectedCatch.value.detections[0].confidence = parseFloat(selectedCatch.value.detections[0].confidence);
    showEditModal.value = true;
}

const handleFishDataSave = async (updatedData) => {
    try {
        await store.dispatch('updateCatch', updatedData);
        showEditModal.value = false;
    } catch (error) {
        console.error('Error saving fish data:', error);
        alert('물고기 정보 저장에 실패했습니다.');
    }
};

function openImagePopup(imageUrl) {
    popupImageUrl.value = `${BACKEND_BASE_URL}/uploads/${imageUrl}`;
    isImagePopupVisible.value = true;
}

function confirmDelete(catchId) {
    if (confirm('정말로 항목을 삭제하시겠습니까?')) {
        deleteCatch(catchId);
    }
}

function deleteCatch(catchId) {
    store.dispatch('deleteCatch', catchId).then(() => {
        const currentTotal = totalFilteredItems.value;
        displayCount.value = Math.min(displayCount.value, currentTotal);
    }).catch((error) => {
        console.error("Delete error:", error.response ? error.response.data : error.message);
        alert('데이터 삭제에 실패했습니다.');
    });
}

watch([searchQuery, sortOption], () => {
    displayCount.value = initialLoad;
    nextTick(() => {
        setupIntersectionObserver();
    });
});

watch(() => catches.value, () => {
    nextTick(() => {
        setupIntersectionObserver();
    });
}, { deep: true });

onUnmounted(() => {
    if (observer) {
        observer.disconnect();
    }
});
</script>

<style scoped>
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.grid > div {
    opacity: 0;
    animation: fadeIn 0.5s ease forwards;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
