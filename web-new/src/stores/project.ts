import { defineStore } from 'pinia'
import apiClient from '@/api/client'

// 分镜数据接口
export interface Shot {
  shot_id: string
  title: string
  description: string
  scene: string
  characters: string
  action: string
  visual_elements: string
  dialogue?: string
  narration?: string
  duration: number
  camera: string
  angle: string
  movement: string
  transition: string
  emotion: string
  notes?: string
}

// 项目数据接口
export interface ProjectData {
  requirement?: {
    description: string
    duration: number
    quality_tier: string
    style: string
  }
  analysis?: {
    theme: string
    style: string
    shots: number
    duration: number
    key_elements: string[]
  }
  script?: {
    content: string
    metadata?: any
  }
  characters?: Array<{
    name: string
    description: string
  }>
  storyboard?: {
    shots: Shot[]
    total_shots: number
  }
  characterDesigns?: Record<string, string>
  // 分镜参考图 (shot_id -> image_url)
  shotImages?: Record<string, string>
  // 分镜视频 (shot_id -> video_url)
  shotVideos?: Record<string, string>
}

// 生成状态
export interface GenerationStatus {
  // 图像生成状态 (shot_id -> 'pending' | 'generating' | 'done' | 'error')
  imageStatus: Record<string, 'pending' | 'generating' | 'done' | 'error'>
  // 视频生成状态 (shot_id -> 'pending' | 'generating' | 'done' | 'error')
  videoStatus: Record<string, 'pending' | 'generating' | 'done' | 'error'>
  // 错误信息
  errors: Record<string, string>
}

export const useProjectStore = defineStore('project', {
  state: () => ({
    projectId: '',
    projectData: {} as ProjectData,
    generationStatus: {
      imageStatus: {},
      videoStatus: {},
      errors: {}
    } as GenerationStatus,
    isLoading: false
  }),

  getters: {
    // 获取所有分镜
    shots: (state): Shot[] => state.projectData.storyboard?.shots || [],

    // 获取分镜总数
    totalShots: (state): number => state.projectData.storyboard?.total_shots || 0,

    // 检查所有图像是否生成完成
    allImagesGenerated: (state): boolean => {
      const shots = state.projectData.storyboard?.shots || []
      return shots.every(shot => state.projectData.shotImages?.[shot.shot_id])
    },

    // 检查所有视频是否生成完成
    allVideosGenerated: (state): boolean => {
      const shots = state.projectData.storyboard?.shots || []
      return shots.every(shot => state.projectData.shotVideos?.[shot.shot_id])
    },

    // 获取图像生成进度
    imageProgress: (state): number => {
      const shots = state.projectData.storyboard?.shots || []
      if (shots.length === 0) return 0
      const generated = shots.filter(shot => state.projectData.shotImages?.[shot.shot_id]).length
      return Math.round((generated / shots.length) * 100)
    },

    // 获取视频生成进度
    videoProgress: (state): number => {
      const shots = state.projectData.storyboard?.shots || []
      if (shots.length === 0) return 0
      const generated = shots.filter(shot => state.projectData.shotVideos?.[shot.shot_id]).length
      return Math.round((generated / shots.length) * 100)
    }
  },

  actions: {
    // 初始化项目
    initializeProject() {
      if (!this.projectId) {
        this.projectId = `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      }
    },

    // 从 localStorage 恢复状态
    restoreState() {
      try {
        const saved = localStorage.getItem(`videogen-project-${this.projectId}`)
        if (saved) {
          const data = JSON.parse(saved)
          this.projectData = data.projectData || {}
          this.generationStatus = data.generationStatus || { imageStatus: {}, videoStatus: {}, errors: {} }
        }
      } catch (e) {
        console.error('Failed to restore project state:', e)
      }
    },

    // 保存状态到 localStorage
    saveState() {
      try {
        localStorage.setItem(`videogen-project-${this.projectId}`, JSON.stringify({
          projectData: this.projectData,
          generationStatus: this.generationStatus
        }))
      } catch (e) {
        console.error('Failed to save project state:', e)
      }
    },

    // 分析需求
    async analyzeRequirement(requirement: ProjectData['requirement']) {
      this.projectData.requirement = requirement
      const response = await apiClient.post('/api/analyze-requirement', {
        project_id: this.projectId,
        requirement
      })
      this.projectData.analysis = response.data
      this.saveState()
      return response.data
    },

    // 生成剧本
    async generateScript() {
      const response = await apiClient.post('/api/generate-script', {
        project_id: this.projectId,
        analysis: this.projectData.analysis
      })
      this.projectData.script = {
        content: response.data.content,
        metadata: response.data.metadata
      }
      // 提取角色
      this.extractCharacters(response.data.content)
      this.saveState()
      return response.data
    },

    // 从剧本提取角色
    extractCharacters(scriptContent: string) {
      // 简单的角色提取逻辑
      const characters: Array<{ name: string; description: string }> = []
      const lines = scriptContent.split('\n')

      for (const line of lines) {
        if (line.includes('【角色】') || line.includes('角色：')) {
          const match = line.match(/[：:]\s*(.+)/)
          if (match) {
            const desc = match[1].trim()
            // 尝试提取角色名
            const nameMatch = desc.match(/^([^，,、]+)/)
            if (nameMatch) {
              characters.push({
                name: nameMatch[1].trim(),
                description: desc
              })
            }
          }
        }
      }

      // 如果没有提取到，添加默认角色
      if (characters.length === 0) {
        characters.push({ name: '主角', description: '故事的主要人物' })
      }

      this.projectData.characters = characters
    },

    // 生成角色设计图
    async generateCharacterDesign(name: string, description: string) {
      const response = await apiClient.post('/api/generate-image', {
        project_id: this.projectId,
        shot: 0,
        shot_info: {
          scene: '角色设计图',
          characters: `${name}: ${description}`,
          action: '角色立绘，多角度展示',
          visual_elements: '白色背景，角色设计稿，多视角',
          camera: '全身',
          angle: '正面',
          emotion: '中性'
        }
      })

      if (!this.projectData.characterDesigns) {
        this.projectData.characterDesigns = {}
      }
      this.projectData.characterDesigns[name] = response.data.image_url
      this.saveState()
      return response.data
    },

    // 生成分镜脚本
    async generateStoryboard() {
      const response = await apiClient.post('/api/generate-storyboard', {
        project_id: this.projectId,
        script: this.projectData.script
      })
      this.projectData.storyboard = {
        shots: response.data.shots,
        total_shots: response.data.total_shots
      }

      // 初始化生成状态
      for (const shot of response.data.shots) {
        this.generationStatus.imageStatus[shot.shot_id] = 'pending'
        this.generationStatus.videoStatus[shot.shot_id] = 'pending'
      }

      this.saveState()
      return response.data
    },

    // 生成单个分镜的参考图
    async generateShotImage(shot: Shot) {
      const shotId = shot.shot_id
      this.generationStatus.imageStatus[shotId] = 'generating'

      try {
        const response = await apiClient.post('/api/generate-image', {
          project_id: this.projectId,
          shot: parseInt(shotId.replace('S', '')) || 1,
          shot_info: shot
        })

        if (!this.projectData.shotImages) {
          this.projectData.shotImages = {}
        }
        this.projectData.shotImages[shotId] = response.data.image_url
        this.generationStatus.imageStatus[shotId] = 'done'
        this.saveState()
        return response.data
      } catch (e: any) {
        this.generationStatus.imageStatus[shotId] = 'error'
        this.generationStatus.errors[shotId] = e.message || '图像生成失败'
        throw e
      }
    },

    // 批量生成所有分镜参考图
    async generateAllShotImages() {
      const shots = this.projectData.storyboard?.shots || []
      const promises = shots.map(shot => this.generateShotImage(shot))
      return Promise.allSettled(promises)
    },

    // 生成单个分镜的视频
    async generateShotVideo(shot: Shot) {
      const shotId = shot.shot_id
      const imageUrl = this.projectData.shotImages?.[shotId]

      if (!imageUrl) {
        throw new Error(`分镜 ${shotId} 的参考图尚未生成`)
      }

      this.generationStatus.videoStatus[shotId] = 'generating'

      try {
        const response = await apiClient.post('/api/generate-video', {
          project_id: this.projectId,
          shot: parseInt(shotId.replace('S', '')) || 1,
          image_url: imageUrl,
          shot_info: shot
        })

        if (!this.projectData.shotVideos) {
          this.projectData.shotVideos = {}
        }
        this.projectData.shotVideos[shotId] = response.data.video_url
        this.generationStatus.videoStatus[shotId] = 'done'
        this.saveState()
        return response.data
      } catch (e: any) {
        this.generationStatus.videoStatus[shotId] = 'error'
        this.generationStatus.errors[`video_${shotId}`] = e.message || '视频生成失败'
        throw e
      }
    },

    // 并发生成所有分镜视频
    async generateAllShotVideos() {
      const shots = this.projectData.storyboard?.shots || []
      // 只生成已有参考图的分镜视频
      const shotsWithImages = shots.filter(shot => this.projectData.shotImages?.[shot.shot_id])
      const promises = shotsWithImages.map(shot => this.generateShotVideo(shot))
      return Promise.allSettled(promises)
    },

    // 重置项目
    resetProject() {
      this.projectId = ''
      this.projectData = {}
      this.generationStatus = { imageStatus: {}, videoStatus: {}, errors: {} }
      this.initializeProject()
    }
  }
})
