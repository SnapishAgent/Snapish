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
                    <router-link 
                        v-for="service in services" 
                        :key="service.id" 
                        :to="service.route"
                        class="flex flex-col items-center hover:bg-gray-50 p-2 rounded-lg transition-colors">
                        <template v-if="service.name.includes('서비스')">
                            <Settings class="w-8 h-8 mb-2" />
                        </template>
                        <template v-else>
                            <component
                                :is="getServiceIcon(service.name)"
                                class="w-8 h-8 mb-2 text-gray-600"
                            />
                        </template>
                        <span class="text-gray-700 text-sm text-center">{{ service.name }}</span>
                    </router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { 
    Edit, 
    LogOut, 
    Settings, 
    Waves, 
    Cloud, 
    BookOpen, 
    Users 
} from 'lucide-vue-next';
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
const services = computed(() => store.getters.services);

const isAuthenticated = computed(() => store.getters.isAuthenticated);

onMounted(async () => {
    if (isAuthenticated.value) {
        await Promise.all([
            store.dispatch('fetchUserProfile'),
            store.dispatch('fetchCatches'),
            store.dispatch('fetchServices'),
        ]);
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
            const response = await axios.post('http://localhost:5000/profile/avatar', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
            });

            if (response.data.avatarUrl) {
                await store.dispatch('fetchUserProfile');
                alert('아바타가 성공적으로 업데이트되었습니다.');
            }
        } catch (error) {
            console.error('Error uploading avatar:', error);
            alert('아바타 업로드에 실패했습니다.');
        }
    }
};

// 서비스 아이콘 매핑 함수
function getServiceIcon(serviceName) {
    const iconMap = {
        '물때 정보': Waves,
        '날씨 정보': Cloud,
        '내 기록': BookOpen,
        '커뮤니티': Users,
    };
    return iconMap[serviceName] || Settings;
}
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