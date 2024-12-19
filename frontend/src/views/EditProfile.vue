<template>
    <div class="min-h-screen bg-gray-100 flex items-center justify-center px-4"
        style="min-height: calc(100vh - 112px);">
        <div class="bg-white w-full max-w-lg p-8 rounded-lg shadow-lg">
            <h1 class="text-3xl font-bold text-center mb-6">프로필 수정</h1>
            <form @submit.prevent="handleEditProfile" class="space-y-6">
                <!-- 기본 정보 섹션 -->
                <div>
                    <label for="username" class="block text-gray-700">아이디</label>
                    <input v-model="username" id="username" type="text" placeholder="아이디" required
                        class="w-full mt-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" />
                </div>
                <div>
                    <label for="email" class="block text-gray-700">이메일</label>
                    <input v-model="email" id="email" type="email" placeholder="이메일" required
                        class="w-full mt-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" />
                </div>
                <!-- 비밀번호 변경 섹션 -->
                <div class="border-t pt-6">
                    <h2 class="text-xl font-semibold mb-4">비밀번호 변경</h2>
                    <div>
                        <label for="currentPassword" class="block text-gray-700">현재 비밀번호</label>
                        <input v-model="currentPassword" id="currentPassword" type="password" placeholder="현재 비밀번호"
                            autocomplete="current-password"
                            class="w-full mt-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" />
                    </div>
                    <div>
                        <label for="newPassword" class="block text-gray-700">새 비밀번호</label>
                        <input v-model="newPassword" id="newPassword" type="password" placeholder="새 비밀번호"
                            autocomplete="new-password"
                            class="w-full mt-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" />
                    </div>
                    <div>
                        <label for="confirmPassword" class="block text-gray-700">비밀번호 확인</label>
                        <input v-model="confirmPassword" id="confirmPassword" type="password" placeholder="비밀번호 확인"
                            autocomplete="new-password"
                            class="w-full mt-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" />
                    </div>
                    <div v-if="passwordError" class="text-red-500 text-sm mt-2">
                        {{ passwordError }}
                    </div>
                </div>
                <!-- 비밀번호 강도 표시 -->
                <div v-if="newPassword" class="mt-4">
                    <div class="flex justify-between mb-1">
                        <span class="text-sm font-medium">비밀번호 강도: {{ passwordStrengthText }}</span>
                        <span class="text-sm font-medium">{{ passwordStrengthPercentage }}</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div :class="passwordStrengthClass" :style="{ width: passwordStrengthPercentage }"
                            class="h-2 rounded-full"></div>
                    </div>
                </div>
                <!-- 저장 버튼 및 에러 메시지 -->
                <button type="submit" :disabled="isLoading"
                    class="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded-md transition duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed">
                    <svg v-if="isLoading" class="animate-spin h-5 w-5 mr-3 text-white"
                        xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                    </svg>
                    <span v-else>저장</span>
                </button>
                <div v-if="errorMessage" class="text-red-500 text-sm text-center mt-2">
                    {{ errorMessage }}
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import axios from '@/axios';

const username = ref('');
const email = ref('');
const currentPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const isLoading = ref(false);
const errorMessage = ref('');
const passwordError = ref('');

const passwordStrength = ref(0);
const passwordStrengthText = ref('');
const passwordStrengthClass = ref('');
const passwordStrengthPercentage = ref('0%');

const router = useRouter();
const store = useStore();

const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    return strength;
};

watch(newPassword, (val) => {
    passwordStrength.value = calculatePasswordStrength(val);
    switch (passwordStrength.value) {
        case 0:
        case 1:
            passwordStrengthText.value = '매우 약함';
            passwordStrengthClass.value = 'bg-red-500';
            passwordStrengthPercentage.value = '20%';
            break;
        case 2:
            passwordStrengthText.value = '약함';
            passwordStrengthClass.value = 'bg-orange-500';
            passwordStrengthPercentage.value = '40%';
            break;
        case 3:
            passwordStrengthText.value = '보통';
            passwordStrengthClass.value = 'bg-yellow-500';
            passwordStrengthPercentage.value = '60%';
            break;
        case 4:
            passwordStrengthText.value = '강함';
            passwordStrengthClass.value = 'bg-blue-500';
            passwordStrengthPercentage.value = '80%';
            break;
        case 5:
            passwordStrengthText.value = '매우 강함';
            passwordStrengthClass.value = 'bg-green-500';
            passwordStrengthPercentage.value = '100%';
            break;
    }
});

const handleEditProfile = async () => {
    if ((newPassword.value || confirmPassword.value) && newPassword.value !== confirmPassword.value) {
        passwordError.value = '새 비밀번호가 일치하지 않습니다.';
        return;
    } else {
        passwordError.value = '';
    }

    isLoading.value = true;
    errorMessage.value = '';

    try {
        const payload = {
            username: username.value,
            email: email.value,
        };

        if (currentPassword.value && newPassword.value) {
            payload.current_password = currentPassword.value;
            payload.new_password = newPassword.value;
        }

        await axios.put('/profile', payload, {  // Changed from '/api/profile' to '/profile'
            headers: {
                Authorization: `Bearer ${store.state.token}`,
            },
        });

        router.push('/profile');
    } catch (error) {
        errorMessage.value = error.response?.data?.message || '프로필 수정에 실패했습니다.';
        console.error('프로필 수정 오류:', error);
    } finally {
        isLoading.value = false;
    }
};
</script>

<style scoped></style>
