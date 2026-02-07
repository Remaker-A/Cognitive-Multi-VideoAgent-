<script setup lang="ts">
import { useProjectStore, type Shot } from '@/stores/project'
import { storeToRefs } from 'pinia'
import { ref, computed, watch } from 'vue'

const projectStore = useProjectStore()
const { projectData, generationStatus, shots, allImagesGenerated, imageProgress, videoProgress } = storeToRefs(projectStore)

// 本地状态
const isGeneratingImages = ref(false)
const isGeneratingVideos = ref(false)
const expandedCard = ref<string | null>(null)

// 计算属性：是否可以生成视频
const canGenerateVideos = computed(() => {
  return allImagesGenerated.value && !isGeneratingVideos.value
})

// 生成所有参考图
async function handleGenerateAllImages() {
  if (isGeneratingImages.value) return
  isGeneratingImages.value = true

  try {
    await projectStore.generateAllShotImages()
  } catch (e) {
    console.error('批量生成图像失败:', e)
  } finally {
    isGeneratingImages.value = false
  }
}

// 生成单个参考图
async function handleGenerateSingleImage(shot: Shot) {
  try {
    await projectStore.generateShotImage(shot)
  } catch (e) {
    console.error(`生成分镜 ${shot.shot_id} 图像失败:`, e)
  }
}

// 并发生成所有视频
async function handleGenerateAllVideos() {
  if (!canGenerateVideos.value) return
  isGeneratingVideos.value = true

  try {
    await projectStore.generateAllShotVideos()
  } catch (e) {
    console.error('批量生成视频失败:', e)
  } finally {
    isGeneratingVideos.value = false
  }
}

// 生成单个视频
async function handleGenerateSingleVideo(shot: Shot) {
  try {
    await projectStore.generateShotVideo(shot)
  } catch (e) {
    console.error(`生成分镜 ${shot.shot_id} 视频失败:`, e)
  }
}

// 获取分镜图像状态
function getImageStatus(shotId: string) {
  return generationStatus.value.imageStatus[shotId] || 'pending'
}

// 获取分镜视频状态
function getVideoStatus(shotId: string) {
  return generationStatus.value.videoStatus[shotId] || 'pending'
}

// 切换卡片展开
function toggleCard(shotId: string) {
  expandedCard.value = expandedCard.value === shotId ? null : shotId
}

// 获取状态颜色
function getStatusColor(status: string) {
  switch (status) {
    case 'generating': return 'text-amber-400'
    case 'done': return 'text-emerald-400'
    case 'error': return 'text-red-400'
    default: return 'text-slate-500'
  }
}

// 获取状态文字
function getStatusText(status: string, type: 'image' | 'video') {
  const prefix = type === 'image' ? '图像' : '视频'
  switch (status) {
    case 'generating': return `${prefix}生成中...`
    case 'done': return `${prefix}已完成`
    case 'error': return `${prefix}生成失败`
    default: return `等待${prefix}生成`
  }
}
</script>

<template>
  <div class="h-full flex flex-col gap-6">
    <!-- 顶部操作栏 -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h3 class="text-xl font-bold text-white mb-1">🎬 分镜工作室</h3>
        <p class="text-sm text-slate-400">生成分镜参考图，然后一键生成视频片段</p>
      </div>

      <div class="flex items-center gap-3">
        <!-- 生成所有参考图按钮 -->
        <button
          @click="handleGenerateAllImages"
          :disabled="isGeneratingImages || shots.length === 0"
          class="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:from-slate-700 disabled:to-slate-700 rounded-lg text-white font-medium transition-all flex items-center gap-2 shadow-lg shadow-indigo-500/20 disabled:shadow-none"
        >
          <span v-if="isGeneratingImages" class="animate-spin">◌</span>
          <span v-else>🖼️</span>
          <span>{{ isGeneratingImages ? '生成中...' : '生成参考图' }}</span>
        </button>

        <!-- 生成所有视频按钮 -->
        <button
          @click="handleGenerateAllVideos"
          :disabled="!canGenerateVideos"
          class="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:from-slate-700 disabled:to-slate-700 rounded-lg text-white font-medium transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/20 disabled:shadow-none"
        >
          <span v-if="isGeneratingVideos" class="animate-spin">◌</span>
          <span v-else>🎥</span>
          <span>{{ isGeneratingVideos ? '生成中...' : '生成视频' }}</span>
        </button>
      </div>
    </div>

    <!-- 进度条 -->
    <div v-if="shots.length > 0" class="grid grid-cols-2 gap-4">
      <div class="bg-slate-800/50 rounded-lg p-3">
        <div class="flex justify-between text-xs mb-2">
          <span class="text-slate-400">参考图进度</span>
          <span class="text-indigo-400 font-mono">{{ imageProgress }}%</span>
        </div>
        <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
            :style="{ width: `${imageProgress}%` }"
          ></div>
        </div>
      </div>

      <div class="bg-slate-800/50 rounded-lg p-3">
        <div class="flex justify-between text-xs mb-2">
          <span class="text-slate-400">视频进度</span>
          <span class="text-emerald-400 font-mono">{{ videoProgress }}%</span>
        </div>
        <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-500"
            :style="{ width: `${videoProgress}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 分镜卡片网格 - 漫画多宫格风格 -->
    <div v-if="shots.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 overflow-y-auto pb-20 pr-2">
      <div
        v-for="(shot, idx) in shots"
        :key="shot.shot_id"
        class="bg-slate-900 border-2 border-slate-700 rounded-xl overflow-hidden flex flex-col transition-all duration-300 hover:border-indigo-500/50 hover:shadow-lg hover:shadow-indigo-500/10"
        :class="{ 'ring-2 ring-indigo-500': expandedCard === shot.shot_id }"
      >
        <!-- 卡片头部 -->
        <div class="px-4 py-3 bg-slate-800/80 border-b border-slate-700 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xs font-mono bg-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded">{{ shot.shot_id }}</span>
            <h4 class="font-bold text-white text-sm truncate max-w-[120px]">{{ shot.title }}</h4>
          </div>
          <div class="flex items-center gap-1">
            <span class="text-xs text-slate-500">{{ shot.duration }}s</span>
            <span class="text-xs px-1.5 py-0.5 rounded bg-slate-700 text-slate-400">{{ shot.camera }}</span>
          </div>
        </div>

        <!-- 媒体区域 -->
        <div class="aspect-video bg-slate-950 relative group">
          <!-- 视频播放器（优先显示） -->
          <video
            v-if="projectData.shotVideos?.[shot.shot_id]"
            :src="projectData.shotVideos[shot.shot_id]"
            class="w-full h-full object-cover"
            controls
            loop
            preload="metadata"
          ></video>

          <!-- 参考图 -->
          <img
            v-else-if="projectData.shotImages?.[shot.shot_id]"
            :src="projectData.shotImages[shot.shot_id]"
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            :alt="shot.title"
          />

          <!-- 图像生成中 -->
          <div v-else-if="getImageStatus(shot.shot_id) === 'generating'" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80">
            <div class="relative">
              <div class="w-16 h-16 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-2xl">🖼️</span>
              </div>
            </div>
            <span class="text-xs text-indigo-400 mt-3">生成参考图中...</span>
          </div>

          <!-- 视频生成中（覆盖在图片上） -->
          <div
            v-else-if="getVideoStatus(shot.shot_id) === 'generating' && projectData.shotImages?.[shot.shot_id]"
            class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80"
          >
            <div class="relative">
              <div class="w-16 h-16 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-2xl">🎥</span>
              </div>
            </div>
            <span class="text-xs text-emerald-400 mt-3">生成视频中...</span>
          </div>

          <!-- 等待状态 -->
          <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-slate-600">
            <span class="text-4xl mb-2 opacity-50">🎬</span>
            <span class="text-xs">等待生成</span>
          </div>

          <!-- 悬浮操作按钮 -->
          <div
            v-if="projectData.shotImages?.[shot.shot_id] && !getVideoStatus(shot.shot_id).includes('generating')"
            class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2"
          >
            <button
              @click="handleGenerateSingleImage(shot)"
              class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded text-xs text-white flex items-center gap-1"
              :disabled="getImageStatus(shot.shot_id) === 'generating'"
            >
              🔄 重新生成图
            </button>
            <button
              v-if="!projectData.shotVideos?.[shot.shot_id]"
              @click="handleGenerateSingleVideo(shot)"
              class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 rounded text-xs text-white flex items-center gap-1"
              :disabled="getVideoStatus(shot.shot_id) === 'generating'"
            >
              🎥 生成视频
            </button>
            <button
              v-else
              @click="handleGenerateSingleVideo(shot)"
              class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded text-xs text-white flex items-center gap-1"
              :disabled="getVideoStatus(shot.shot_id) === 'generating'"
            >
              🔄 重新生成视频
            </button>
          </div>
        </div>

        <!-- 状态指示器 -->
        <div class="px-4 py-2 bg-slate-800/50 border-t border-slate-700/50 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <!-- 图像状态 -->
            <div class="flex items-center gap-1">
              <span :class="getStatusColor(getImageStatus(shot.shot_id))">
                <span v-if="getImageStatus(shot.shot_id) === 'generating'" class="animate-pulse">●</span>
                <span v-else-if="getImageStatus(shot.shot_id) === 'done'">✓</span>
                <span v-else-if="getImageStatus(shot.shot_id) === 'error'">✗</span>
                <span v-else>○</span>
              </span>
              <span class="text-xs text-slate-500">图</span>
            </div>

            <!-- 视频状态 -->
            <div class="flex items-center gap-1">
              <span :class="getStatusColor(getVideoStatus(shot.shot_id))">
                <span v-if="getVideoStatus(shot.shot_id) === 'generating'" class="animate-pulse">●</span>
                <span v-else-if="getVideoStatus(shot.shot_id) === 'done'">✓</span>
                <span v-else-if="getVideoStatus(shot.shot_id) === 'error'">✗</span>
                <span v-else>○</span>
              </span>
              <span class="text-xs text-slate-500">视频</span>
            </div>
          </div>

          <!-- 展开详情按钮 -->
          <button
            @click="toggleCard(shot.shot_id)"
            class="text-xs text-slate-400 hover:text-white transition-colors"
          >
            {{ expandedCard === shot.shot_id ? '收起' : '详情' }}
          </button>
        </div>

        <!-- 展开的详情 -->
        <div
          v-if="expandedCard === shot.shot_id"
          class="px-4 py-3 bg-slate-800/30 border-t border-slate-700/50 text-xs space-y-2"
        >
          <div v-if="shot.description">
            <span class="text-slate-500">描述：</span>
            <span class="text-slate-300">{{ shot.description }}</span>
          </div>
          <div v-if="shot.scene">
            <span class="text-slate-500">场景：</span>
            <span class="text-slate-300">{{ shot.scene }}</span>
          </div>
          <div v-if="shot.action">
            <span class="text-slate-500">动作：</span>
            <span class="text-slate-300">{{ shot.action }}</span>
          </div>
          <div v-if="shot.emotion">
            <span class="text-slate-500">情绪：</span>
            <span class="text-slate-300">{{ shot.emotion }}</span>
          </div>
          <div class="flex gap-2 flex-wrap">
            <span class="px-2 py-0.5 bg-slate-700 rounded text-slate-400">{{ shot.camera }}</span>
            <span class="px-2 py-0.5 bg-slate-700 rounded text-slate-400">{{ shot.angle }}</span>
            <span class="px-2 py-0.5 bg-slate-700 rounded text-slate-400">{{ shot.movement }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-500 min-h-[400px]">
      <span class="text-6xl mb-4 opacity-50">🎬</span>
      <p class="text-lg mb-2">暂无分镜数据</p>
      <p class="text-sm">请先在「分镜设计」步骤生成分镜脚本</p>
    </div>
  </div>
</template>

<style scoped>
/* 自定义滚动条 */
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
::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* 视频播放器样式 */
video::-webkit-media-controls-panel {
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
}
</style>
