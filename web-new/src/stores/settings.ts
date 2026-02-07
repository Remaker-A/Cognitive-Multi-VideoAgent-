import { defineStore } from 'pinia'
import apiClient from '@/api/client'

// 模型配置接口
export interface ModelConfig {
    baseUrl: string
    apiKey: string
    modelName: string
}

// 用户信息接口
export interface UserInfo {
    id: string
    username: string
    email: string
    avatar?: string
}

// 设置状态接口
export interface SettingsState {
    // 模型配置
    textModel: ModelConfig
    imageModel: ModelConfig
    videoModel: ModelConfig
    // 语言设置
    language: 'zh-CN' | 'en-US'
    // 用户信息
    user: UserInfo | null
    // 状态
    isLoading: boolean
    isSaving: boolean
    error: string | null
}

const DEFAULT_MODEL_CONFIG: ModelConfig = {
    baseUrl: '',
    apiKey: '',
    modelName: ''
}

// 从 localStorage 加载设置
function loadFromStorage(): Partial<SettingsState> {
    try {
        const saved = localStorage.getItem('videogen-settings')
        if (saved) {
            return JSON.parse(saved)
        }
    } catch (e) {
        console.error('Failed to load settings from storage:', e)
    }
    return {}
}

// 保存到 localStorage
function saveToStorage(state: Partial<SettingsState>) {
    try {
        // 不保存敏感信息到 localStorage（API Key 只保存掩码）
        const toSave = {
            textModel: { ...state.textModel, apiKey: state.textModel?.apiKey ? '***' : '' },
            imageModel: { ...state.imageModel, apiKey: state.imageModel?.apiKey ? '***' : '' },
            videoModel: { ...state.videoModel, apiKey: state.videoModel?.apiKey ? '***' : '' },
            language: state.language
        }
        localStorage.setItem('videogen-settings', JSON.stringify(toSave))
    } catch (e) {
        console.error('Failed to save settings to storage:', e)
    }
}

export const useSettingsStore = defineStore('settings', {
    state: (): SettingsState => {
        const saved = loadFromStorage()
        return {
            textModel: saved.textModel?.baseUrl ? saved.textModel : { ...DEFAULT_MODEL_CONFIG },
            imageModel: saved.imageModel?.baseUrl ? saved.imageModel : { ...DEFAULT_MODEL_CONFIG },
            videoModel: saved.videoModel?.baseUrl ? saved.videoModel : { ...DEFAULT_MODEL_CONFIG },
            language: saved.language || 'zh-CN',
            user: null,
            isLoading: false,
            isSaving: false,
            error: null
        }
    },

    getters: {
        // 检查模型是否已配置
        isTextModelConfigured: (state) => !!state.textModel.baseUrl && !!state.textModel.apiKey,
        isImageModelConfigured: (state) => !!state.imageModel.baseUrl && !!state.imageModel.apiKey,
        isVideoModelConfigured: (state) => !!state.videoModel.baseUrl && !!state.videoModel.apiKey,

        // 获取当前语言显示名称
        languageDisplayName: (state) => {
            return state.language === 'zh-CN' ? '简体中文' : 'English'
        }
    },

    actions: {
        // 更新文本模型配置
        updateTextModel(config: Partial<ModelConfig>) {
            this.textModel = { ...this.textModel, ...config }
            saveToStorage(this.$state)
        },

        // 更新图像模型配置
        updateImageModel(config: Partial<ModelConfig>) {
            this.imageModel = { ...this.imageModel, ...config }
            saveToStorage(this.$state)
        },

        // 更新视频模型配置
        updateVideoModel(config: Partial<ModelConfig>) {
            this.videoModel = { ...this.videoModel, ...config }
            saveToStorage(this.$state)
        },

        // 切换语言
        setLanguage(lang: 'zh-CN' | 'en-US') {
            this.language = lang
            saveToStorage(this.$state)
        },

        // 保存所有设置到服务器
        async saveSettings() {
            this.isSaving = true
            this.error = null
            try {
                await apiClient.post('/settings', {
                    textModel: this.textModel,
                    imageModel: this.imageModel,
                    videoModel: this.videoModel,
                    language: this.language
                })
                return true
            } catch (err: any) {
                console.error('Failed to save settings:', err)
                this.error = err.message || 'Failed to save settings'
                return false
            } finally {
                this.isSaving = false
            }
        },

        // 从服务器加载设置
        async fetchSettings() {
            this.isLoading = true
            this.error = null
            try {
                const response = await apiClient.get('/settings')
                if (response.data) {
                    if (response.data.textModel) this.textModel = response.data.textModel
                    if (response.data.imageModel) this.imageModel = response.data.imageModel
                    if (response.data.videoModel) this.videoModel = response.data.videoModel
                    if (response.data.language) this.language = response.data.language
                }
            } catch (err: any) {
                console.error('Failed to fetch settings:', err)
                this.error = err.message || 'Failed to fetch settings'
            } finally {
                this.isLoading = false
            }
        },

        // 获取用户信息
        async fetchUserInfo() {
            try {
                const response = await apiClient.get('/user/info')
                this.user = response.data
            } catch (err: any) {
                console.error('Failed to fetch user info:', err)
            }
        },

        // 登出
        async logout() {
            try {
                await apiClient.post('/auth/logout')
                this.user = null
                // 清除本地存储
                localStorage.removeItem('videogen-settings')
                localStorage.removeItem('videogen-token')
            } catch (err: any) {
                console.error('Failed to logout:', err)
            }
        },

        // 重置所有设置
        resetSettings() {
            this.textModel = { ...DEFAULT_MODEL_CONFIG }
            this.imageModel = { ...DEFAULT_MODEL_CONFIG }
            this.videoModel = { ...DEFAULT_MODEL_CONFIG }
            this.language = 'zh-CN'
            localStorage.removeItem('videogen-settings')
        }
    }
})
