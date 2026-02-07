<script setup lang="ts">
import { useProjectStore, type Shot } from '@/stores/project'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

const projectStore = useProjectStore()
const { projectData, shots } = storeToRefs(projectStore)
const isLoading = ref(false)
const editingShot = ref<string | null>(null)

async function handleGenerateStoryboard() {
  if (!projectData.value.script?.content) {
    alert('请先生成剧本')
    return
  }

  isLoading.value = true
  try {
    await projectStore.generateStoryboard()
  } catch (e) {
    alert('分镜生成失败: ' + e)
  } finally {
    isLoading.value = false
  }
}

function getCameraIcon(camera: string) {
  const icons: Record<string, string> = {
    '特写': '🔍',
    '近景': '👤',
    '中景': '🧍',
    '远景': '🏞️',
    '全景': '🌄',
    '鸟瞰': '🦅'
  }
  return icons[camera] || '📷'
}
</script>

<template>
  <div class="h-full flex flex-col gap-6">
    <div class="flex justify-between items-center">
      <div>
        <h3 class="text-xl font-bold text-white mb-1">🎬 分镜设计</h3>
        <p class="text-sm text-slate-400">将剧本转换为详细的分镜脚本</p>
      </div>
      <button
        @click="handleGenerateStoryboard"
        :disabled="isLoading || !projectData.script?.content"
        class="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 disabled:from-slate-700 disabled:to-slate-700 rounded-lg text-white font-medium transition-all flex items-center gap-2"
      >
        <span v-if="isLoading" class="animate-spin">◌</span>
        <span>{{ isLoading ? '生成中...' : shots.length ? '重新生成' : '生成分镜' }}</span>
      </button>
    </div>

    <!-- 分镜时间线 -->
    <div v-if="shots.length > 0" class="flex-1 overflow-y-auto pr-2 pb-4">
      <div class="relative">
        <!-- 时间线 -->
        <div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-amber-500 via-orange-500 to-red-500"></div>

        <!-- 分镜卡片 -->
        <div class="space-y-4">
          <div
            v-for="(shot, idx) in shots"
            :key="shot.shot_id"
            class="relative pl-16"
          >
            <!-- 时间线节点 -->
            <div class="absolute left-4 w-5 h-5 rounded-full bg-slate-900 border-2 border-amber-500 flex items-center justify-center">
              <span class="text-[10px] text-amber-400">{{ idx + 1 }}</span>
            </div>

            <!-- 卡片内容 -->
            <div class="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden hover:border-amber-500/50 transition-colors">
              <div class="p-4">
                <div class="flex items-start justify-between mb-3">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-mono bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded">{{ shot.shot_id }}</span>
                    <h4 class="font-bold text-white">{{ shot.title }}</h4>
                  </div>
                  <div class="flex items-center gap-2 text-xs">
                    <span class="px-2 py-0.5 bg-slate-700 rounded text-slate-400">{{ shot.duration }}s</span>
                    <span class="text-lg" :title="shot.camera">{{ getCameraIcon(shot.camera) }}</span>
                  </div>
                </div>

                <p class="text-sm text-slate-400 mb-3 line-clamp-2">{{ shot.description }}</p>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                  <div class="bg-slate-900/50 rounded px-2 py-1.5">
                    <span class="text-slate-500 block">机位</span>
                    <span class="text-slate-300">{{ shot.camera }}</span>
                  </div>
                  <div class="bg-slate-900/50 rounded px-2 py-1.5">
                    <span class="text-slate-500 block">角度</span>
                    <span class="text-slate-300">{{ shot.angle }}</span>
                  </div>
                  <div class="bg-slate-900/50 rounded px-2 py-1.5">
                    <span class="text-slate-500 block">运动</span>
                    <span class="text-slate-300">{{ shot.movement }}</span>
                  </div>
                  <div class="bg-slate-900/50 rounded px-2 py-1.5">
                    <span class="text-slate-500 block">转场</span>
                    <span class="text-slate-300">{{ shot.transition }}</span>
                  </div>
                </div>

                <div v-if="shot.action" class="mt-3 text-xs">
                  <span class="text-slate-500">动作：</span>
                  <span class="text-slate-400">{{ shot.action }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-500 min-h-[400px]">
      <span class="text-6xl mb-4 opacity-50">🎬</span>
      <p class="text-lg mb-2">准备生成分镜脚本</p>
      <p class="text-sm">AI 将根据剧本自动生成专业的分镜设计</p>
    </div>
  </div>
</template>

<style scoped>
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 3px;
}
</style>
