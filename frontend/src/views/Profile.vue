<template>
    <div class="min-h-screen bg-white flex flex-col items-center">
        <div class="bg-white w-full max-w-4xl rounded-lg mt-6">
            <!-- 프로필 헤더 -->
            <div v-if="user" class="p-6 flex flex-col items-center">
                <!-- Avatar 및 사용자 정보 -->
                <div @click="triggerFileInput" class="flex flex-col items-center space-y-4 cursor-pointer">
                    <!-- 아바타 -->
                    <div class="w-32 h-32 rounded-full bg-gray-200 flex-shrink-0" :style="{
                        backgroundImage: `url(${user.avatar ? `http://localhost:5000${user.avatar}` : '/default-avatar.webp'})`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                    }"></div>

                    <!-- 사용자 정보 -->
                    <div class="text-center">
                        <h1 class="text-2xl font-semibold text-gray-800">
                            {{ user.full_name || user.username }}
                        </h1>
                        <p class="text-gray-600 mt-1">{{ user.tier || '낚시 초보자' }}</p>
                    </div>
                </div>

                <!-- Hidden file input -->
                <input type="file" ref="avatarInput" accept="image/*" @change="uploadAvatar" class="hidden" />

                <!-- 액션 버튼 -->
                <div class="flex items-center space-x-6 mt-4">
                    <!-- 프로필 수정 -->
                    <button @click="editProfile" class="text-blue-500 hover:text-blue-600 flex items-center space-x-1"
                        aria-label="Edit Profile">
                        <Edit class="h-6 w-6" />
                        <span class="text-sm font-medium">프로필 수정</span>
                    </button>

                    <!-- 로그아웃 -->
                    <button @click="logout" class="text-red-500 hover:text-red-600 flex items-center space-x-1"
                        aria-label="Logout">
                        <LogOut class="h-6 w-6" />
                        <span class="text-sm font-medium">로그아웃</span>
                    </button>
                </div>
            </div>

            <!-- 낚시 잡기, 팔로워, 팔로잉 -->
            <div v-if="stats" class="flex justify-around py-6 border-t border-gray-200">
                <div class="text-center cursor-pointer" @click="goToCatches">
                    <div class="text-2xl font-bold text-gray-800">{{ stats.catches || 0 }}</div>
                    <div class="text-gray-500 text-sm">Catches</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-gray-800">{{ stats.followers || 0 }}</div>
                    <div class="text-gray-500 text-sm">Followers</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-gray-800">{{ stats.following || 0 }}</div>
                    <div class="text-gray-500 text-sm">Following</div>
                </div>
            </div>

            <!-- 4x4 Grid of Icons and Names -->
            <div class="p-6">
                <h2 class="text-xl font-semibold text-gray-800 mb-6">전체 서비스</h2>
                <div class="grid grid-cols-4 gap-4">
                    <div v-for="service in services" :key="service.id" class="flex flex-col items-center">
                        <!-- Changed from service._id -->
                        <template v-if="service.name.includes('서비스')">
                            <Settings class="w-8 h-8 mb-2" />
                        </template>
                        <template v-else>
                            <img :src="service.icon" alt="Service Icon" class="w-16 h-16 mb-2" />
                        </template>
                        <span class="text-gray-700">{{ service.name }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { Edit, LogOut, Settings } from 'lucide-vue-next';
import axios from 'axios';

const store = useStore();
const router = useRouter();
const avatarInput = ref(null);

const user = computed(() => store.getters.user);
const stats = computed(() => {
    const originalStats = store.getters.stats;
    return {
        catches: store.getters.catches.length || 0, // Fetch catches from the store
        followers: originalStats?.followers || 0,
        following: originalStats?.following || 0,
    };
});
const services = computed(() => {
    if (!store.state.services) {
        store.dispatch('fetchServices');
    }
    return store.state.services || [
        { id: 1, icon: '/', name: '서비스 1' },
        { id: 2, icon: '/', name: '서비스 2' },
        { id: 3, icon: '/', name: '서비스 3' },
        { id: 4, icon: '/', name: '서비스 4' },
        { id: 5, icon: '/', name: '서비스 5' },
        { id: 6, icon: '/', name: '서비스 6' },
        { id: 7, icon: '/', name: '서비스 7' },
        { id: 8, icon: '/', name: '서비스 8' },
        { id: 9, icon: '/', name: '서비스 9' },
        { id: 10, icon: '/', name: '서비스 10' },
        { id: 11, icon: '/', name: '서비스 11' },
        { id: 12, icon: '/', name: '서비스 12' },
        { id: 13, icon: '/', name: '서비스 13' },
        { id: 14, icon: '/', name: '서비스 14' },
        { id: 15, icon: '/', name: '서비스 15' },
        { id: 16, icon: '/', name: '서비스 16' },
    ];
});

const isAuthenticated = computed(() => store.getters.isAuthenticated);

onMounted(() => {
    if (!store.state.catches) {
        store.dispatch("fetchCatches"); // Fetch catches when the component is mounted
    }
    if (isAuthenticated.value) {
        store.dispatch('fetchCatches');
    }
    const savedAvatar = localStorage.getItem('avatar');
    if (savedAvatar) {
        store.dispatch('updateAvatar', savedAvatar); // Load avatar URL from local storage
    }
});

const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('avatar');
    store.dispatch('logout');
    router.push('/login');
};

const editProfile = () => {
    router.push('/edit-profile');
};

const goToCatches = () => {
    router.push('/catches');
};

const triggerFileInput = () => {
    avatarInput.value.click();
};

const uploadAvatar = async (event) => {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('avatar', file);
        try {
            const response = await axios.post('http://localhost:5000/profile/avatar', formData, { // Ensure this URL is correct
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
            });

            // Check if response is JSON
            if (response.headers['content-type'].includes('application/json')) {
                const avatarUrl = response.data.avatarUrl;
                store.dispatch('updateAvatar', avatarUrl);
                localStorage.setItem('avatar', avatarUrl); // Save avatar URL to local storage
                alert('아바타가 성공적으로 업데이트되었습니다.');
            } else {
                console.error('Invalid response format:', response);
                alert('서버 응답이 올바르지 않습니다.');
            }
        } catch (error) {
            if (error.response) {
                console.error('Error response:', error.response);
                alert(`Error: ${error.response.status} - ${error.response.statusText}`);
            } else {
                console.error('Error uploading avatar:', error);
                alert('아바타 업로드에 실패했습니다.');
            }
        }
    }
};
</script>

<style scoped>
/* 미세 조정 */
@media (min-width: 768px) {
    .md\:flex-row {
        flex-direction: row;
    }

    .md\:items-center {
        align-items: center;
    }

    .md\:justify-between {
        justify-content: space-between;
    }
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

.cursor-pointer {
    cursor: pointer;
}
</style>