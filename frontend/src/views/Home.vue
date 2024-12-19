<template>
    <!-- 전체 페이지 컨테이너 - 최소 화면 높이 설정 및 중앙 정렬 -->
    <div class="min-h-screen bg-gray-100 flex justify-center">
        <!-- 메인 콘텐츠 영역 - 최대 너비 제한 및 그림자 효과 적용 -->
        <div class="w-full max-w-md bg-white shadow-lg">
            <!-- 메인 콘텐츠 영역 - 하단 네비게이션바 공간 확보를 위한 패딩 설정 -->
            <main class="pb-20 px-4">
                <!-- 물때/날씨 섹션 -->
                <section class="mb-6 pt-4">
                    <div class="flex justify-between items-center mb-3">
                        <router-link to="/weather-specific" class="flex flex-col items-center p-2">
                            <h2 class="text-lg font-medium">오늘의 물때</h2> 
                        </router-link>
                        <ChevronRightIcon class="w-5 h-5 text-gray-400" />
                    </div>
                    <!-- 물때 표시 카드 -->
                    <div class="relative bg-gray-50 rounded-lg p-6 shadow-sm fixed-size-card" style="height: 125px; overflow: hidden; position: relative;">
                        <!-- 새로고침 버튼 -->
                        <button 
                            class="absolute top-2 right-2 bg-gray-200 text-gray-600 rounded-full p-1 shadow hover:bg-gray-300"
                            @click="refreshCard"
                            title="새로고침"
                        >새로고침
                        </button>
                        <MulddaeWidget></MulddaeWidget>
                    </div>
                </section>

                <!-- 물고기 캐치 기록 섹션 -->
                <section class="mb-6">
                    <div class="flex justify-between items-center mb-3">
                        <h2 class="text-lg font-medium">내가 잡은 물고기</h2>
                        <ChevronRightIcon class="w-5 h-5 text-gray-400" />
                    </div>
                    <!-- 물고기 그리드 레이아웃 - 3열 구성 -->
                    <div class="grid grid-cols-3 gap-3">
                        <div v-for="i in 3" :key="i" class="bg-gray-50 rounded-lg p-3 shadow-sm">
                            <div class="flex items-center justify-center h-24 bg-gray-200 rounded mb-2">
                                <FishIcon class="w-8 h-8 text-gray-400" />
                            </div>
                            <p class="text-sm text-gray-600">물고기</p>
                            <p class="text-sm">종류</p>
                        </div>
                    </div>
                </section>

                <!-- 커뮤니티 게시물 섹션 -->
                <section>
                    <div class="flex justify-between items-center mb-3">
                        <h2 class="text-lg font-medium">
                            <router-link to="/community" class="flex flex-col items-center p-2">
                                커뮤니티
                            </router-link>
                        </h2>
                        <ChevronRightIcon class="w-5 h-5 text-gray-400" />
                    </div>
                    <!-- 게시물 목록 -->
                    <div class="space-y-3">
                        <!-- 각 게시물 카드 -->
                        <article v-for="i in 4" :key="i" class="bg-gray-50 rounded-lg p-4 shadow-sm">
                            <div class="flex gap-3">
                                <!-- 게시물 썸네일 이미지 -->
                                <div
                                    class="w-16 h-16 bg-gray-200 rounded flex items-center justify-center flex-shrink-0">
                                    <ImageIcon class="w-8 h-8 text-gray-400" />
                                </div>
                                <!-- 게시물 내용 -->
                                <div class="flex-1">
                                    <h3 class="font-medium mb-1">게시물 제목</h3>
                                    <p class="text-sm text-gray-600 mb-2">게시물 내용 미리보기입니다. 여기에 간단한 설명이 들어갑니다.</p>
                                    <!-- 게시 시간 정보 -->
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
</template>

<script setup>
// Lucide 아이콘 컴포넌트 임포트
/* eslint-disable */
import {
    ChevronRightIcon,// 오른쪽 화살표 아이콘
    // CloudIcon,       // 구름 아이콘
    FishIcon,        // 물고기 아이콘
    ImageIcon,       // 이미지 아이콘
    ClockIcon,       // 시계 아이콘
} from 'lucide-vue-next'
import { onMounted } from "vue";
import { useStore } from "vuex";
import MulddaeWidget from '../components/MulddaeWidget.vue';
// import WeatherService from "../components/WeatherService.vue";

const store = useStore();

onMounted(() => {
    store.dispatch("fetchMulddae");
    
    if (!store.state.currentlocation) {
        store.dispatch("fetchLocation");
    }
});

</script>