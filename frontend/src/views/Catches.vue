<template>
    <div class="min-h-screen bg-gray-100 flex justify-center">
        <div class="w-full max-w-4xl bg-white shadow-lg">
            <main class="p-4">
                <div class="mb-4 flex items-center">
                    <input type="text" v-model="searchQuery" placeholder="물고기 검색..." class="border p-2 w-full rounded" />
                    <select v-model="sortOption" class="border p-2 ml-2 rounded">
                        <option value="latest">최신순</option>
                        <option value="oldest">오래된순</option>
                    </select>
                </div>
                <div v-if="filteredCatches.length > 0" class="grid grid-cols-2 gap-4">
                    <div v-for="(catchItem) in filteredCatches" :key="catchItem.id"
                        class="bg-gray-50 p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300">
                        <img :src="`${BACKEND_BASE_URL}/uploads/${catchItem.imageUrl}`" alt="Catch Image"
                            class="w-full h-32 object-cover rounded-lg mb-2 cursor-pointer border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-300"
                            @click="openImagePopup(catchItem.imageUrl)" />
                        <p class="text-gray-800 text-sm text-center flex justify-center items-center">
                            {{ catchItem.detections[0].label }}
                            <span v-if="catchItem.detections[0].label" class="ml-2 cursor-pointer"
                                @click="openEditPopup(catchItem)">
                                <Edit class="h-4 w-4 text-blue-500" />
                            </span>
                            <span v-if="catchItem.detections[0].label" class="ml-2 cursor-pointer"
                                @click="confirmDelete(catchItem.id)">
                                <Trash class="h-4 w-4 text-red-500" />
                            </span>
                        </p>
                        <p class="text-gray-600 text-xs text-center">{{ catchItem.catch_date }}</p>
                        <p class="text-gray-600 text-xs text-center">신뢰도: {{
                            (catchItem.detections[0].confidence * 100).toFixed(2) }}%</p>
                    </div>
                </div>
                <div v-else-if="!loading" class="text-gray-500 text-center">아직 잡은 물고기가 없습니다.</div>
                <div v-if="loading" class="text-center text-gray-500 mt-4">Loading...</div>
                <div ref="loadMoreTrigger" class="text-center text-gray-500 mt-4"></div>
                <div v-if="isEditPopupVisible"
                    class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-20">
                    <div class="bg-white p-6 rounded-lg shadow-lg w-80">
                        <h2 class="text-lg mb-4 text-center">데이터 수정</h2>
                        <div class="mb-4">
                            <label class="block text-sm mb-1">라벨(Name)</label>
                            <input v-model="selectedCatch.detections[0].label" class="border p-2 w-full rounded" />
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm mb-1">날짜(YYYY-MM-DD)</label>
                            <input type="date" v-model="selectedCatch.catch_date" class="border p-2 w-full rounded" />
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm mb-1">신뢰도(1~100%)</label>
                            <input type="number" step="0.01" v-model.number="confidenceInput"
                                class="border p-2 w-full rounded" />
                        </div>
                        <div class="flex justify-between">
                            <button @click="saveEdit"
                                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors duration-300">저장</button>
                            <button @click="isEditPopupVisible = false"
                                class="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400 transition-colors duration-300">취소</button>
                        </div>
                    </div>
                </div>
                <div v-if="isImagePopupVisible"
                    class="fixed inset-0 bg-black bg-opacity-75 flex justify-center items-center z-30"
                    @click="isImagePopupVisible = false">
                    <div class="relative flex justify-center items-center max-w-full max-h-full" @click.stop>
                        <img :src="popupImageUrl" alt="Popup Image"
                            class="max-w-full max-h-full object-contain rounded-lg border border-gray-200 shadow-lg" />
                        <button @click="isImagePopupVisible = false"
                            class="absolute top-2 right-2 bg-white text-black rounded-full p-1 hover:bg-gray-200 transition-colors duration-300">
                            &times;
                        </button>
                    </div>
                </div>
            </main>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { Edit, Trash } from 'lucide-vue-next';

const store = useStore();
const catches = computed(() => store.getters.catches);
const loading = ref(true);
const isEditPopupVisible = ref(false);
const selectedCatch = ref(null);
const displayedCatches = ref([]);
const confidenceInput = computed({
    get() {
        return selectedCatch.value ? (parseFloat(selectedCatch.value.detections[0].confidence) * 100).toFixed(2) : '100.00';
    },
    set(value) {
        if (selectedCatch.value) {
            selectedCatch.value.detections[0].confidence = (value / 100).toFixed(2);
        }
    }
});
const itemsToLoad = 8;
const loadMoreTrigger = ref(null);
const isImagePopupVisible = ref(false);
const popupImageUrl = ref('');
const searchQuery = ref('');
const sortOption = ref('latest');

const filteredCatches = computed(() => {
    const catchesFiltered = displayedCatches.value.filter(catchItem => {
        return catchItem.detections[0].label.toLowerCase().includes(searchQuery.value.toLowerCase());
    });

    if (sortOption.value === 'latest') {
        return catchesFiltered.sort((a, b) => b.id - a.id);
    } else {
        return catchesFiltered.sort((a, b) => a.id - b.id);
    }
});

// Define backend base URL
const BACKEND_BASE_URL = 'http://localhost:5000';

onMounted(() => {
    // 데이터 로드
    if (store.getters.isAuthenticated) {
        store.dispatch('fetchCatches').then(() => {
            const sortedCatches = store.getters.catches.slice().sort((a, b) => b.id - a.id);
            displayedCatches.value = sortedCatches;
            loading.value = false;
        }).catch(() => {
            loading.value = false;
        });
    } else {
        loading.value = false;
    }

    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !loading.value) {
            loadMoreCatches();
        }
    }, {
        root: null,
        rootMargin: '0px',
        threshold: 1.0
    });

    if (loadMoreTrigger.value) {
        observer.observe(loadMoreTrigger.value);
    }
});

function loadMoreCatches() {
    loading.value = true;
    setTimeout(() => {
        const currentLength = displayedCatches.value.length;
        const sortedCatches = catches.value.slice().sort((a, b) => b.id - a.id);
        const moreCatches = sortedCatches.slice(currentLength, currentLength + itemsToLoad);
        displayedCatches.value = [...displayedCatches.value, ...moreCatches];
        loading.value = false;
    }, 1000);
}

function openEditPopup(catchItem) {
    console.log("Opening edit popup for:", catchItem); // Inspect the catch item
    if (!catchItem.id) { // Changed from '_id' to 'id'
        console.error("Cannot open edit popup: 'id' is undefined.");
        alert("수정할 수 없는 항목입니다: 식별자가 없습니다.");
        return;
    }
    selectedCatch.value = { ...catchItem };
    selectedCatch.value.detections[0].confidence = parseFloat(selectedCatch.value.detections[0].confidence); // Ensure it's a number
    isEditPopupVisible.value = true;
}

function saveEdit() {
    const updatedCatch = { ...selectedCatch.value };
    if (!updatedCatch.id) { // Changed from '_id' to 'id'
        console.error("Save failed: 'id' is undefined.");
        alert("데이터 저장에 실패했습니다: 식별자가 없습니다.");
        return;
    }
    // Ensure catch_date is correctly formatted
    if (updatedCatch.catch_date) {
        updatedCatch.catch_date = new Date(updatedCatch.catch_date).toISOString().split('T')[0];
    }
    // Ensure confidence is saved with up to two decimal places
    updatedCatch.detections[0].confidence = parseFloat(updatedCatch.detections[0].confidence).toFixed(2);
    store.dispatch('updateCatch', updatedCatch).then((response) => {
        console.log("Update response:", response); // Log the response from the server
        // Update displayedCatches after successful update
        const index = displayedCatches.value.findIndex(catchItem => catchItem.id === updatedCatch.id); // Changed from '_id' to 'id'
        if (index !== -1) {
            displayedCatches.value[index] = { ...updatedCatch };
        }
        isEditPopupVisible.value = false;
    }).catch((error) => {
        console.error("Update error:", error.response ? error.response.data : error.message); // Detailed error logging
        alert('데이터 업데이트에 실패했습니다.');
    });
}

function openImagePopup(imageUrl) {
    popupImageUrl.value = `${BACKEND_BASE_URL}/uploads/${imageUrl}`; // Updated to include BACKEND_BASE_URL
    isImagePopupVisible.value = true;
}

function confirmDelete(catchId) {
    if (confirm('정말로 이 항목을 삭제하시겠습니까?')) {
        deleteCatch(catchId);
    }
}

function deleteCatch(catchId) {
    store.dispatch('deleteCatch', catchId).then(() => {
        displayedCatches.value = displayedCatches.value.filter(catchItem => catchItem.id !== catchId);
    }).catch((error) => {
        console.error("Delete error:", error.response ? error.response.data : error.message); // Detailed error logging
        alert('데이터 삭제에 실패했습니다.');
    });
}
</script>

<style scoped>
.grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

/* Optional: style the edit icon if needed */
.cursor-pointer:hover svg {
    stroke: #3b82f6;
}

.fixed {
    position: fixed;
}

.absolute {
    position: absolute;
}

/* Ensure pop-up images are displayed correctly */
.object-contain {
    object-fit: contain;
}
</style>
