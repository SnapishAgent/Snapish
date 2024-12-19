<template>
  <header class="bg-white shadow">
    <!-- 네비게이션 바 -->
    <nav class="container mx-auto px-4 py-3 flex justify-between items-center">
      <!-- 사이트 제목 -->
      <h1 class="text-xl font-bold">SNAPish</h1>
      <div class="flex items-center gap-4">
        <!-- 알림 버튼 -->
        <button class="p-2">
          <BellIcon class="w-6 h-6" />
        </button>
        <!-- 설정 버튼 -->
        <button class="p-2">
          <Settings2Icon class="w-6 h-6" />
        </button>
      </div>
    </nav>
  </header>
</template>

<script>
import { BellIcon, Settings2Icon } from 'lucide-vue-next'

export default {
  name: 'AppHeader',
  components: {
    BellIcon,
    Settings2Icon
  }
}
</script>
