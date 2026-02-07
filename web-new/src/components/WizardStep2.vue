<script setup lang="ts">
import { useProjectStore } from '@/stores/project'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

const projectStore = useProjectStore()
const { projectData } = storeToRefs(projectStore)
const isLoading = ref(false)

async function handleGenerateScript() {
  if (!projectData.value.analysis) return alert("Please complete analysis first")
  isLoading.value = true
  try {
     await projectStore.generateScript()
  } catch (e) {
     alert('Script generation failed: ' + e)
  } finally {
     isLoading.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col gap-6">
    <div v-if="!projectData.script?.content" class="flex-1 flex flex-col items-center justify-center min-h-[400px]">
        <h3 class="text-2xl font-bold text-slate-300 mb-4">Ready to write the script?</h3>
        <p class="text-slate-500 mb-8 max-w-md text-center">AI will generate a professional script based on your requirements, including scene descriptions and character dialogues.</p>
        <button @click="handleGenerateScript" :disabled="isLoading"
           class="px-8 py-4 rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-bold text-lg shadow-lg shadow-emerald-500/20 transition-all transform hover:scale-105 flex items-center gap-3">
           <span v-if="isLoading" class="animate-spin">◌</span>
           <span>{{ isLoading ? 'Writing Script...' : 'Generate Script' }}</span>
        </button>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
       <!-- Script Content -->
       <div class="lg:col-span-2 space-y-4">
          <div class="flex justify-between items-center">
             <h3 class="text-xl font-semibold text-emerald-400">Screenplay</h3>
             <button @click="handleGenerateScript" class="text-xs bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded text-slate-400 transition-colors">Regenerate</button>
          </div>
          <div class="bg-slate-900 border border-slate-700 rounded-xl p-6 h-[600px] overflow-y-auto font-mono text-sm leading-relaxed text-slate-300 whitespace-pre-wrap shadow-inner">
             {{ projectData.script.content }}
          </div>
       </div>
       
       <!-- Characters List -->
       <div class="space-y-4">
          <h3 class="text-xl font-semibold text-purple-400">Cast & Characters</h3>
          <div class="space-y-4 max-h-[600px] overflow-y-auto pr-2">
             <div v-for="(char, idx) in projectData.characters" :key="idx" 
               class="bg-slate-800/50 border border-slate-700/50 p-4 rounded-xl hover:bg-slate-800 transition-colors group">
                <div class="flex items-center gap-3 mb-2">
                   <div class="w-8 h-8 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs font-bold">{{ char.name.charAt(0) }}</div>
                   <h4 class="font-bold text-white">{{ char.name }}</h4>
                </div>
                <p class="text-xs text-slate-400 line-clamp-3 group-hover:line-clamp-none transition-all">{{ char.description }}</p>
             </div>
             
             <div v-if="(!projectData.characters || projectData.characters.length === 0)" class="text-slate-500 text-sm text-center py-8">
                No characters detected
             </div>
          </div>
       </div>
    </div>
  </div>
</template>
