<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useProjectStore } from '@/stores/project'
import { storeToRefs } from 'pinia'

// Components
import WizardStep1 from '@/components/WizardStep1.vue'
import WizardStep2 from '@/components/WizardStep2.vue'
import WizardStep3 from '@/components/WizardStep3.vue'
import WizardStep4 from '@/components/WizardStep4.vue'
import WizardStep5 from '@/components/WizardStep5.vue'
import WizardStep6 from '@/components/WizardStep6.vue'

// Steps map
const steps = [
  { id: 1, title: '需求理解', desc: 'Describe your vision' },
  { id: 2, title: '剧本创作', desc: 'AI Scriptwriting' },
  { id: 3, title: '角色设计', desc: 'Character Studio' },
  { id: 4, title: '分镜设计', desc: 'Visual Storyboard' },
  { id: 5, title: '图像生成', desc: 'Scene Rendering' },
  { id: 6, title: '视频合成', desc: 'Final Production' }
]

const currentStep = ref(1)
const projectStore = useProjectStore()
const { projectId } = storeToRefs(projectStore)

onMounted(() => {
  projectStore.initializeProject()
  projectStore.restoreState()
})

const progress = computed(() => {
  return (currentStep.value / steps.length) * 100
})
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-white font-sans selection:bg-indigo-500 selection:text-white">
    <!-- Top Navigation -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold">V</div>
          <span class="font-bold text-lg tracking-tight">VideoGen <span class="text-xs font-normal text-slate-400 ml-1">Studio</span></span>
        </div>
        
        <div class="flex items-center gap-4">
           <router-link to="/settings" class="flex items-center justify-center w-8 h-8 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer" title="Settings">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 pointer-events-none" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.532 1.532 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.532 1.532 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
              </svg>
            </router-link>
            <div class="text-xs font-mono text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full">
              ID: {{ projectId }}
            </div>
        </div>
      </div>
      
      <!-- Progress Bar -->
      <div class="h-1 bg-slate-800 w-full">
         <div class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500 ease-out" :style="{ width: `${progress}%` }"></div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Stepper -->
      <nav aria-label="Progress" class="mb-12">
        <ol role="list" class="overflow-hidden rounded-md lg:flex lg:border-l lg:border-r lg:border-slate-800 lg:rounded-none">
          <li v-for="(step, stepIdx) in steps" :key="step.id" class="relative overflow-hidden lg:flex-1">
            <div :class="[
              stepIdx === 0 ? 'border-b-0 rounded-t-md border-t-0' : '', 
              stepIdx === steps.length - 1 ? 'border-t-0 rounded-b-md border-b-0' : '', 
              'border border-slate-800 overflow-hidden lg:border-0'
            ]">
              <button @click="currentStep = step.id" class="group w-full text-left">
                <div class="absolute top-0 left-0 w-1 h-full bg-transparent group-hover:bg-indigo-500/30 transition-colors" :class="{ '!bg-indigo-500': currentStep === step.id }"></div>
                <div class="flex items-start px-6 py-5 text-sm font-medium">
                  <span class="flex-shrink-0">
                    <span class="flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all"
                      :class="[
                        currentStep === step.id ? 'border-indigo-500 text-indigo-400' : 
                        currentStep > step.id ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10' : 'border-slate-700 text-slate-500'
                      ]">
                      <span v-if="currentStep > step.id">✓</span>
                      <span v-else>{{ step.id }}</span>
                    </span>
                  </span>
                  <div class="ml-4 mt-0.5 min-w-0 flex flex-col items-start">
                    <span class="text-sm font-medium" :class="currentStep === step.id ? 'text-indigo-400' : 'text-slate-300'">{{ step.title }}</span>
                    <span class="text-xs text-slate-500 mt-1">{{ step.desc }}</span>
                  </div>
                </div>
              </button>
            </div>
          </li>
        </ol>
      </nav>

      <!-- Content Area -->
      <div class="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6 min-h-[500px] shadow-xl backdrop-blur-sm">
         <div v-if="currentStep === 1">
           <WizardStep1 />
         </div>
         <div v-else-if="currentStep === 2">
           <WizardStep2 />
         </div>
         <div v-else-if="currentStep === 3">
           <WizardStep3 />
         </div>
         <div v-else-if="currentStep === 4">
           <WizardStep4 />
         </div>
         <div v-else-if="currentStep === 5">
           <WizardStep5 />
         </div>
         <div v-else-if="currentStep === 6">
           <WizardStep6 />
         </div>
         <div v-else>
           <h2 class="text-2xl font-bold mb-6">Step {{ currentStep }}</h2>
           <p class="text-slate-400">Component coming soon...</p>
         </div>
      </div>
      
      <!-- Action Bar (Sticky Bottom) -->
      <div class="fixed bottom-0 left-0 w-full bg-slate-900/90 border-t border-slate-800 p-4 backdrop-blur z-40" v-if="true">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <button class="px-6 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                @click="currentStep--" :disabled="currentStep === 1" :class="{ 'opacity-50 cursor-not-allowed': currentStep === 1 }">
                Back
            </button>
            
            <button class="px-8 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium shadow-lg shadow-indigo-500/20 transition-all transform hover:scale-105"
                @click="currentStep++">
                Continue
            </button>
        </div>
      </div>

    </main>
  </div>
</template>

<style scoped>
/* Add any view-specific styles here if Tailwind isn't enough */
</style>
