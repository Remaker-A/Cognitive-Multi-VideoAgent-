<script setup lang="ts">
import { useProjectStore } from '@/stores/project'
import { storeToRefs } from 'pinia'
import { ref, reactive } from 'vue'

const projectStore = useProjectStore()
const { projectData } = storeToRefs(projectStore)
const isLoading = ref(false)

const form = reactive({
  description: '',
  duration: 30,
  quality_tier: 'standard',
  style: '现代'
})

const styles = ['现代', '复古', '科幻', '自然', '商务', '艺术', '动漫', '纪录片']
const durations = [15, 30, 60, 90, 120]

async function handleAnalyze() {
  if (!form.description.trim()) {
    alert('请输入视频描述')
    return
  }

  isLoading.value = true
  try {
    await projectStore.analyzeRequirement({
      description: form.description,
      duration: form.duration,
      quality_tier: form.quality_tier,
      style: form.style
    })
  } catch (e) {
    alert('需求分析失败: ' + e)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col gap-6">
    <div class="flex justify-between items-center">
      <div>
        <h3 class="text-xl font-bold text-white mb-1">💡 需求理解</h3>
        <p class="text-sm text-slate-400">描述你的视频创意，AI 将分析并提取核心要素</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- 输入表单 -->
      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-slate-300 mb-2">视频描述 *</label>
          <textarea
            v-model="form.description"
            rows="6"
            class="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors resize-none"
            placeholder="描述你想要创作的视频内容，例如：一个关于科技创新的宣传片，展示未来城市的智能生活场景..."
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">视频时长</label>
            <select
              v-model="form.duration"
              class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option v-for="d in durations" :key="d" :value="d">{{ d }} 秒</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">视觉风格</label>
            <select
              v-model="form.style"
              class="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option v-for="s in styles" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
        </div>

        <button
          @click="handleAnalyze"
          :disabled="isLoading || !form.description.trim()"
          class="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:from-slate-700 disabled:to-slate-700 text-white font-medium transition-all flex items-center justify-center gap-2"
        >
          <span v-if="isLoading" class="animate-spin">◌</span>
          <span>{{ isLoading ? '分析中...' : '开始分析' }}</span>
        </button>
      </div>

      <!-- 分析结果 -->
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
        <h4 class="text-lg font-semibold text-white mb-4">📊 分析结果</h4>

        <div v-if="projectData.analysis" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-slate-900/50 rounded-lg p-4">
              <span class="text-xs text-slate-500 block mb-1">核心主题</span>
              <span class="text-white font-medium">{{ projectData.analysis.theme }}</span>
            </div>
            <div class="bg-slate-900/50 rounded-lg p-4">
              <span class="text-xs text-slate-500 block mb-1">视觉风格</span>
              <span class="text-white font-medium">{{ projectData.analysis.style }}</span>
            </div>
            <div class="bg-slate-900/50 rounded-lg p-4">
              <span class="text-xs text-slate-500 block mb-1">建议镜头数</span>
              <span class="text-white font-medium">{{ projectData.analysis.shots }} 个</span>
            </div>
            <div class="bg-slate-900/50 rounded-lg p-4">
              <span class="text-xs text-slate-500 block mb-1">总时长</span>
              <span class="text-white font-medium">{{ projectData.analysis.duration }} 秒</span>
            </div>
          </div>

          <div v-if="projectData.analysis.key_elements?.length" class="bg-slate-900/50 rounded-lg p-4">
            <span class="text-xs text-slate-500 block mb-2">关键元素</span>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(el, idx) in projectData.analysis.key_elements"
                :key="idx"
                class="px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-full text-sm"
              >{{ el }}</span>
            </div>
          </div>
        </div>

        <div v-else class="flex flex-col items-center justify-center h-48 text-slate-500">
          <span class="text-4xl mb-2 opacity-50">📋</span>
          <span class="text-sm">填写需求后点击分析</span>
        </div>
      </div>
    </div>
  </div>
</template>
