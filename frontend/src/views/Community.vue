<template>
    <div class="min-h-screen bg-gray-100 flex justify-center">
        <div class="w-full max-w-md bg-white shadow-lg">
            <!-- 메인 콘텐츠 섹션 -->
            <main class="p-4">
                <div class="space-y-4" ref="postsContainer">
                    <!-- 게시물 반복 렌더링 -->
                    <article v-for="(post, index) in displayedPosts" :key="index" class="bg-white rounded-lg shadow-sm">
                        <div class="p-4">
                            <div class="flex items-center mb-4">
                                <!-- 작성자 프로필 이미지 -->
                                <div class="w-10 h-10 rounded-full bg-gray-200 overflow-hidden">
                                    <img 
                                        :src="post.authorAvatar || DEFAULT_AVATAR" 
                                        alt="Profile" 
                                        class="w-full h-full object-cover"
                                        @error="$event.target.src = DEFAULT_AVATAR"
                                    />
                                </div>
                                <div class="ml-3">
                                    <!-- 작성자 이름 -->
                                    <h3 class="font-bold">{{ post.author }}</h3>
                                    <!-- 작성 날짜 -->
                                    <p class="text-sm text-gray-500">{{ post.date }}</p>
                                </div>
                            </div>
                            <!-- 게시물 이미지 -->
                            <img 
                                :src="post.image" 
                                :alt="post.title" 
                                class="w-full h-64 object-cover rounded-lg mb-4" 
                                @error="handleImageError"
                            />
                            <!-- 게시물 내용 -->
                            <p class="text-gray-800">{{ post.content }}</p>
                            <div class="flex items-center mt-4 space-x-4 text-gray-500">
                                <!-- 좋아요 버튼 -->
                                <button class="flex items-center">
                                    <HeartIcon class="w-5 h-5 mr-1" />
                                    {{ post.likes }}
                                </button>
                                <!-- 댓글 버튼 -->
                                <button class="flex items-center">
                                    <MessageCircleIcon class="w-5 h-5 mr-1" />
                                    {{ post.comments }}
                                </button>
                            </div>
                        </div>
                    </article>
                    <!-- 로딩 인디케이터 -->
                    <div v-if="isLoading" class="flex justify-center py-4">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                </div>
            </main>
        </div>
    </div>
</template>

<script setup>
import {
    HeartIcon,
    MessageCircleIcon
} from 'lucide-vue-next'
import { ref, onMounted, onUnmounted } from 'vue';

// 기본 이미지 base64 문자열 (회색 배경의 간단한 이미지)
const DEFAULT_IMAGE = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgZmlsbD0iI2YzZjRmNiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjAiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7snbTrr7jsp4Ag7JeG7J2EPC90ZXh0Pjwvc3ZnPg==';

// 기본 아바타 이미지
const DEFAULT_AVATAR = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiNlNWU3ZWIiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOWNhM2FmIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+VTwvdGV4dD48L3N2Zz4=';

const basePosts = [
    {
        author: '낚시왕',
        date: '1시간 전',
        content: '오늘의 조과입니다! 날씨가 정말 좋네요.',
        image: 'https://picsum.photos/800/600?random=1',
        likes: 24,
        comments: 8,
        authorAvatar: DEFAULT_AVATAR,
        title: '오늘의 조과'
    },
    {
        author: '바다사랑',
        date: '3시간 전',
        content: '초보자도 잡을 수 있는 포인트를 공유합니다.',
        image: 'https://picsum.photos/800/600?random=2',
        likes: 45,
        comments: 12,
        authorAvatar: DEFAULT_AVATAR,
        title: '낚시 포인트'
    },
    {
        author: '물때지킴이',
        date: '5시간 전',
        content: '오늘 물때 정보와 함께 잡은 감성돔입니다. 조과가 좋네요!',
        image: 'https://picsum.photos/800/600?random=3',
        likes: 67,
        comments: 15,
        authorAvatar: DEFAULT_AVATAR,
        title: '감성돔 조과'
    }
];

// 상태 관리
const displayedPosts = ref([]);
const isLoading = ref(false);
const page = ref(1);
const postsContainer = ref(null);

// 게시물 생성 함수
function generatePosts(pageNum) {
    return basePosts.map((post, index) => ({
        ...post,
        id: `${pageNum}-${Math.random()}`,
        date: `${Math.floor(Math.random() * 12) + 1}시간 전`,
        likes: Math.floor(Math.random() * 100),
        comments: Math.floor(Math.random() * 50),
        image: `https://picsum.photos/800/600?random=${pageNum * 3 + index}`
    }));
}

// 초기 게시물 로드
onMounted(() => {
    displayedPosts.value = generatePosts(page.value);
    window.addEventListener('scroll', handleScroll);
});

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
});

// 스크롤 핸들러
async function handleScroll() {
    if (isLoading.value) return;

    const container = postsContainer.value;
    if (!container) return;

    const bottomOfWindow = Math.ceil(window.innerHeight + window.scrollY) >= document.documentElement.scrollHeight - 100;

    if (bottomOfWindow) {
        isLoading.value = true;
        
        // 새로운 게시물 로드 시뮬레이션
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        page.value++;
        const newPosts = generatePosts(page.value);
        displayedPosts.value = [...displayedPosts.value, ...newPosts];
        
        isLoading.value = false;
    }
}

// 이미지 로드 실패 시 대체 이미지 사용
function handleImageError(e) {
    if (e.target.src !== DEFAULT_IMAGE) {
        e.target.src = DEFAULT_IMAGE;
    }
}
</script>

<style scoped>
/* 이미지 로딩 및 전환 효과 */
img {
    transition: opacity 0.3s ease;
}

img[src=''] {
    opacity: 0;
}

/* 버튼 호버 효과 */
button {
    transition: color 0.2s ease;
}

button:hover {
    color: #4B5563;
}

/* 스크롤 최적화 */
.space-y-4 {
    will-change: contents;
}

/* 로딩 애니메이션 */
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.animate-spin {
    animation: spin 1s linear infinite;
}
</style>