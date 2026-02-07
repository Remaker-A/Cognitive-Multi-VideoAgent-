<script setup lang="ts">
import { useProjectStore } from '@/stores/project'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

const projectStore = useProjectStore()
const { projectData } = storeToRefs(projectStore)
const generating = ref<Record<string, boolean>>({})

async function handleGenerate(char: any, index: number) {
  if (generating.value[char.name]) return
  generating.value[char.name] = true
  
  try {
     await projectStore.generateCharacterDesign(char.name, char.description)
  } catch (e) {
     alert(`Failed to generate design for ${char.name}: ${e}`)
  } finally {
     generating.value[char.name] = false
  }
}

async function generateAll() {
  if (!projectData.value.characters) return
  for (let i = 0; i < projectData.value.characters.length; i++) {
     const char = projectData.value.characters[i]
     if (!projectData.value.characterDesigns?.[char.name]) {
        handleGenerate(char, i)
     }
  }
}
</script>

<template>
  <div class="h-full flex flex-col gap-6">
     <div class="flex justify-between items-center">
        <div>
           <h3 class="text-xl font-bold text-white mb-1">Character Studio</h3>
           <p class="text-sm text-slate-400">Generate standardized character sheets for consistency.</p>
        </div>
        <button @click="generateAll" class="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-medium transition-colors">
           Generate All
        </button>
     </div>

     <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 overflow-y-auto pr-2 pb-4">
        <div v-for="(char, idx) in projectData.characters" :key="idx" 
           class="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden flex flex-col">
           <!-- Header -->
           <div class="p-4 bg-slate-800/50 border-b border-slate-700">
              <h4 class="font-bold text-white">{{ char.name }}</h4>
              <p class="text-xs text-slate-400 mt-1 line-clamp-2">{{ char.description }}</p>
           </div>
           
           <!-- Image Area -->
           <div class="aspect-[3/2] bg-slate-950 relative flex items-center justify-center group text-center">
              <img v-if="projectData.characterDesigns?.[char.name]" 
                 :src="projectData.characterDesigns[char.name]" 
                 class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" 
                 alt="Character Design" />
              
              <div v-else-if="generating[char.name]" class="flex flex-col items-center">
                 <div class="animate-spin text-indigo-500 text-3xl mb-2">◌</div>
                 <span class="text-xs text-indigo-400">Animator Agent Working...</span>
              </div>
              
              <div v-else class="text-slate-600 text-sm">
                 Waiting for generation
              </div>

              <!-- Overlay Actions -->
              <div v-if="projectData.characterDesigns?.[char.name]" 
                 class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                 <button @click="handleGenerate(char, Number(idx))" class="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-xs text-white">Regenerate</button>
                 <button class="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 rounded text-xs text-white">Download</button>
              </div>
           </div>
           
           <!-- Footer Action (if empty) -->
           <div v-if="!projectData.characterDesigns?.[char.name] && !generating[char.name]" class="p-3 border-t border-slate-800 bg-slate-900">
              <button @click="handleGenerate(char, Number(idx))" class="w-full py-2 rounded border border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white text-sm transition-colors">
                 Generate Design
              </button>
           </div>
        </div>
     </div>
     
     <div v-if="(!projectData.characters || projectData.characters.length === 0)" class="flex-1 flex items-center justify-center text-slate-500">
         Please generate script first to identify characters.
     </div>
  </div>
</template>
