<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'
import ModelConfigCard from '@/components/settings/ModelConfigCard.vue'

const settingsStore = useSettingsStore()
const { textModel, imageModel, videoModel, language, user, isSaving } = storeToRefs(settingsStore)

// 显示/隐藏 API Key
const showApiKey = ref({
  text: false,
  image: false,
  video: false
})

// 保存提示
const saveMessage = ref('')
const saveStatus = ref<'success' | 'error' | ''>('')

// 语言选项
const languageOptions = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'en-US', label: 'English' }
]

onMounted(() => {
  settingsStore.fetchUserInfo()
})

// 保存设置
async function handleSave() {
  const success = await settingsStore.saveSettings()
  if (success) {
    saveMessage.value = '设置已保存'
    saveStatus.value = 'success'
  } else {
    saveMessage.value = '保存失败，请重试'
    saveStatus.value = 'error'
  }
  setTimeout(() => {
    saveMessage.value = ''
    saveStatus.value = ''
  }, 3000)
}

// 重置设置
function handleReset() {
  if (confirm('确定要重置所有设置吗？')) {
    settingsStore.resetSettings()
    saveMessage.value = '设置已重置'
    saveStatus.value = 'success'
    setTimeout(() => {
      saveMessage.value = ''
      saveStatus.value = ''
    }, 3000)
  }
}

// 登出
async function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    await settingsStore.logout()
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-white font-sans">
    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold">V</div>
            <span class="font-bold text-lg tracking-tight">VideoGen <span class="text-xs font-normal text-slate-400 ml-1">Studio</span></span>
          </router-link>
        </div>
        <div class="flex items-center gap-2">
          <router-link to="/" class="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors">
            ← 返回
          </router-link>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Title -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold mb-2">设置</h1>
        <p class="text-slate-400">配置 AI 模型和应用偏好</p>
      </div>

      <!-- Save Message Toast -->
      <Transition name="fade">
        <div v-if="saveMessage"
          class="fixed top-20 right-4 px-4 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2"
          :class="saveStatus === 'success' ? 'bg-emerald-500/90' : 'bg-red-500/90'">
          <svg v-if="saveStatus === 'success'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
          {{ saveMessage }}
        </div>
      </Transition>

      <!-- Model Configurations -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
          </svg>
          AI 模型配置
        </h2>

        <div class="space-y-4">
          <!-- Text Model -->
          <ModelConfigCard
            title="Text Model"
            subtitle="文本生成模型 (GPT/Claude/Gemini)"
            icon="text"
            :config="textModel"
            :show-api-key="showApiKey.text"
            @update:config="settingsStore.updateTextModel($event)"
            @toggle-api-key="showApiKey.text = !showApiKey.text"
          />

          <!-- Image Model -->
          <ModelConfigCard
            title="Image Model"
            subtitle="图像生成模型 (DALL-E/Midjourney/SD)"
            icon="image"
            :config="imageModel"
            :show-api-key="showApiKey.image"
            @update:config="settingsStore.updateImageModel($event)"
            @toggle-api-key="showApiKey.image = !showApiKey.image"
          />

          <!-- Video Model -->
          <ModelConfigCard
            title="Video Model"
            subtitle="视频生成模型 (Runway/Pika/Sora)"
            icon="video"
            :config="videoModel"
            :show-api-key="showApiKey.video"
            @update:config="settingsStore.updateVideoModel($event)"
            @toggle-api-key="showApiKey.video = !showApiKey.video"
          />
        </div>
      </section>

      <!-- Language Settings -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"></path>
          </svg>
          语言设置
        </h2>

        <div class="bg-slate-800/50 rounded-xl border border-slate-700/50 p-5">
          <label class="block text-sm text-slate-400 mb-2">界面语言</label>
          <div class="flex gap-3">
            <button
              v-for="option in languageOptions"
              :key="option.value"
              @click="settingsStore.setLanguage(option.value as 'zh-CN' | 'en-US')"
              class="px-4 py-2 rounded-lg border transition-all"
              :class="language === option.value
                ? 'bg-indigo-500/20 border-indigo-500 text-indigo-400'
                : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
      </section>

      <!-- Account Settings -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
          账户管理
        </h2>

        <div class="bg-slate-800/50 rounded-xl border border-slate-700/50 p-5">
          <div v-if="user" class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-lg font-bold">
                {{ user.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
              <div>
                <div class="font-medium">{{ user.username }}</div>
                <div class="text-sm text-slate-400">{{ user.email }}</div>
              </div>
            </div>
            <button
              @click="handleLogout"
              class="px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 transition-colors"
            >
              退出登录
            </button>
          </div>
          <div v-else class="text-center py-4">
            <p class="text-slate-400 mb-4">尚未登录</p>
            <button class="px-6 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600 text-white transition-colors">
              登录 / 注册
            </button>
          </div>
        </div>
      </section>

      <!-- Action Buttons -->
      <div class="flex justify-between items-center pt-4 border-t border-slate-800">
        <button
          @click="handleReset"
          class="px-4 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          重置设置
        </button>
        <button
          @click="handleSave"
          :disabled="isSaving"
          class="px-8 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium shadow-lg shadow-indigo-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isSaving" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            保存中...
          </span>
          <span v-else>保存设置</span>
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
