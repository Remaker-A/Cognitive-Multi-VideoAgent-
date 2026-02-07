<script setup lang="ts">
import { computed } from 'vue'
import type { ModelConfig } from '@/stores/settings'

interface Props {
  title: string
  subtitle: string
  icon: 'text' | 'image' | 'video'
  config: ModelConfig
  showApiKey: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:config': [config: Partial<ModelConfig>]
  'toggle-api-key': []
}>()

// 图标映射
const iconPath = computed(() => {
  switch (props.icon) {
    case 'text':
      return 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
    case 'image':
      return 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z'
    case 'video':
      return 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z'
    default:
      return ''
  }
})

// 图标颜色
const iconColor = computed(() => {
  switch (props.icon) {
    case 'text':
      return 'from-blue-500 to-cyan-500'
    case 'image':
      return 'from-pink-500 to-rose-500'
    case 'video':
      return 'from-purple-500 to-violet-500'
    default:
      return 'from-indigo-500 to-purple-500'
  }
})

// 配置状态
const isConfigured = computed(() => {
  return !!props.config.baseUrl && !!props.config.apiKey
})

function updateField(field: keyof ModelConfig, value: string) {
  emit('update:config', { [field]: value })
}
</script>

<template>
  <div class="bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-hidden transition-all hover:border-slate-600/50">
    <!-- Card Header -->
    <div class="px-5 py-4 border-b border-slate-700/50 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center" :class="iconColor">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPath"></path>
          </svg>
        </div>
        <div>
          <h3 class="font-medium">{{ title }}</h3>
          <p class="text-xs text-slate-400">{{ subtitle }}</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="isConfigured" class="px-2 py-1 text-xs rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          已配置
        </span>
        <span v-else class="px-2 py-1 text-xs rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
          未配置
        </span>
      </div>
    </div>

    <!-- Card Body -->
    <div class="p-5 space-y-4">
      <!-- Base URL -->
      <div>
        <label class="block text-sm text-slate-400 mb-1.5">Base URL</label>
        <input
          type="text"
          :value="config.baseUrl"
          @input="updateField('baseUrl', ($event.target as HTMLInputElement).value)"
          placeholder="https://api.openai.com/v1"
          class="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
        />
      </div>

      <!-- API Key -->
      <div>
        <label class="block text-sm text-slate-400 mb-1.5">API Key</label>
        <div class="relative">
          <input
            :type="showApiKey ? 'text' : 'password'"
            :value="config.apiKey"
            @input="updateField('apiKey', ($event.target as HTMLInputElement).value)"
            placeholder="sk-xxxxxxxxxxxxxxxx"
            class="w-full px-4 py-2.5 pr-12 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
          />
          <button
            type="button"
            @click="emit('toggle-api-key')"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
          >
            <svg v-if="showApiKey" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Model Name -->
      <div>
        <label class="block text-sm text-slate-400 mb-1.5">Model Name</label>
        <input
          type="text"
          :value="config.modelName"
          @input="updateField('modelName', ($event.target as HTMLInputElement).value)"
          :placeholder="icon === 'text' ? 'gpt-4o / claude-3-opus' : icon === 'image' ? 'dall-e-3 / stable-diffusion-xl' : 'runway-gen3 / pika-1.0'"
          class="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
        />
      </div>
    </div>
  </div>
</template>
