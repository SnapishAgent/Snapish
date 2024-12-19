<!-- Profile.vue 또는 적절한 컴포넌트 -->

<template>
    <!-- 기존 코드 -->
    <button @click="logout">로그아웃</button>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

const router = useRouter();
const store = useStore();

const logout = () => {
    // 토큰 삭제
    localStorage.removeItem('token');

    // 스토어 상태 초기화
    store.dispatch('logout');

    // 로그인 페이지로 이동
    router.push('/login');
};
</script>