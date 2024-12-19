<!-- filepath: /c:/Users/twoimo/Documents/GitHub/Snapish/frontend/src/views/Signup.vue -->
<template>
    <div class="flex items-center justify-center min-h-screen bg-gray-100" style="min-height: calc(100vh - 112px);">
        <div class=" max-w-md w-full p-8 bg-white rounded-lg shadow-lg">
            <h1 class="text-4xl font-extrabold text-gray-800 mb-6 text-center">회원가입</h1>
            <form @submit.prevent="handleSignup" class="flex flex-col space-y-4">
                <input v-model="username" type="text" placeholder="아이디" required
                    class="p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500" />
                <input v-model="email" type="email" placeholder="이메일" required
                    class="p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500" />
                <input v-model="password" type="password" placeholder="비밀번호" required
                    class="p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500" />
                <input v-model="confirmPassword" type="password" placeholder="비밀번호 확인" required
                    class="p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500" />
                <button type="submit"
                    class="py-3 bg-green-600 text-white rounded hover:bg-green-700 transition duration-200">회원가입</button>
            </form>
            <p class="mt-6 text-gray-600 text-center">
                이미 계정이 있으신가요?
                <router-link to="/login" class="text-green-500 hover:underline">로그인</router-link>
            </p>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const router = useRouter();
const store = useStore();

const handleSignup = async () => {
    if (password.value !== confirmPassword.value) {
        alert('비밀번호가 일치하지 않습니다.');
        return;
    }

    try {
        await store.dispatch('signup', {
            username: username.value,
            email: email.value,
            password: password.value,
        });

        router.push('/login');
    } catch (error) {
        alert('회원가입 실패: 이미 사용 중인 아이디나 이메일입니다.');
        console.error('회원가입 오류:', error);
    }
};
</script>
