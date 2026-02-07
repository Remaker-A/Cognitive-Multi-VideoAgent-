<script setup lang="ts">
import { useProjectStore } from '@/stores/project'
import { storeToRefs } from 'pinia'
import { ref, computed } from 'vue'

const projectStore = useProjectStore()
const { projectData, shots, allVideosGenerated, videoProgress } = storeToRefs(projectStore)

const isExporting = ref(false)
const exportProgress = ref(0)

// 获取所有已生成的视频
const generatedVideos = computed(() => {
  return shots.value
    .filter(shot => projectData.value.shotVideos?.[shot.shot_id])
    .map(shot => ({
      ...shot,
      videoUrl: projectData.value.shotVideos![shot.shot_id]
    }))
})

// 计算总时长
const totalDuration = computed(() => {
  return generatedVideos.value.reduce((sum, shot) => sum + shot.duration, 0)
})

// 模拟导出功能
async function handleExport() {
  if (generatedVideos.value.length === 0) {
    alert('没有可导出的视频片段')
    return
  }

  isExporting.value = true
  exportProgress.value = 0

  // 模拟导出进度
  const interval = setInterval(() => {
    exportProgress.value += 10
    if (exportProgress.value >= 100) {
      clearInterval(interval)
      isExporting.value = false
      alert('视频导出完成！（演示功能）')
    }
  }, 500)
}

// 下载单个视频
function downloadVideo(url: string, filename: string) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
</script>

<template>
  <div class="h-full flex flex-col gap-6">
    <div class="flex justify-between items-center">
      <div>
        <h3 class="text-xl font-bold text-white mb-1">🎥 视频合成</h3>
        <p class="text-sm text-slate-400">预览和导出最终视频</p>
      </div>
      <button
        @click="handleExport"
        :disabled="isExporting || generatedVideos.length === 0"
        class="px-6 py-2.5 bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-400 hover:to-pink-400 disabled:from-slate-700 disabled:to-slate-700 rounded-lg text-white font-medium transition-all flex items-center gap-2"
      >
        <span v-if="isExporting" class="animate-spin">◌</span>
        <span>{{ isExporting ? `导出中 ${exportProgress}%` : '导出视频' }}</span>
      </button>
    </div>

    <!-- 统计信息 -->
    <div class="grid grid-cols-4 gap-4">
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-center">
        <span class="text-3xl font-bold text-white">{{ shots.length }}</span>
        <span class="text-xs text-slate-500 block mt-1">总分镜数</span>
      </div>
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-center">
        <span class="text-3xl font-bold text-emerald-400">{{ generatedVideos.length }}</span>
        <span class="text-xs text-slate-500 block mt-1">已生成视频</span>
      </div>
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-center">
        <span class="text-3xl font-bold text-indigo-400">{{ totalDuration }}s</span>
        <span class="text-xs text-slate-500 block mt-1">总时长</span>
      </div>
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-center">
        <span class="text-3xl font-bold" :class="allVideosGenerated ? 'text-emerald-400' : 'text-amber-400'">
          {{ videoProgress }}%
        </span>
        <span class="text-xs text-slate-500 block mt-1">完成进度</span>
      </div>
    </div>

    <!-- 视频预览列表 -->
    <div v-if="generatedVideos.length > 0" class="flex-1 overflow-y-auto pr-2 pb-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="(item, idx) in generatedVideos"
          :key="item.shot_id"
          class="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden"
        >
          <!-- 视频播放器 -->
          <div class="aspect-video bg-black">
            <video
              :src="item.videoUrl"
              class="w-full h-full object-contain"
              controls
              preload="metadata"
            ></video>
          </div>

          <!-- 信息栏 -->
          <div class="p-4 flex items-center justify-between">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-mono bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">{{ item.shot_id }}</span>
                <h4 class="font-medium text-white text-sm">{{ item.title }}</h4>
              </div>
              <p class="text-xs text-slate-500">{{ item.duration }}秒 · {{ item.camera }} · {{ item.movement }}</p>
            </div>
            <button
              @click="downloadVideo(item.videoUrl, `${item.shot_id}.mp4`)"
              class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded text-xs text-white transition-colors"
            >
              ⬇️ 下载
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-500 min-h-[300px]">
      <span class="text-6xl mb-4 opacity-50">🎬</span>
      <p class="text-lg mb-2">暂无视频片段</p>
      <p class="text-sm">请先在「图像生成」步骤生成分镜视频</p>
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
