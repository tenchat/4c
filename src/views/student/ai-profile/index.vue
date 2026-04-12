<!-- AI 就业画像页面 -->
<template>
  <div class="page-ai-profile">
    <el-row :gutter="20">
      <!-- 左侧表单区域 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="7">
        <el-card class="art-card-xs">
          <template #header>
            <div class="card-header">
              <span class="title">基本信息</span>
            </div>
          </template>

          <el-form :model="formData" label-width="80px" class="ai-form">
            <el-form-item label="专业">
              <el-input v-model="formData.major" placeholder="请输入专业名称" clearable />
            </el-form-item>

            <el-form-item label="GPA">
              <el-input-number
                v-model="formData.gpa"
                :min="0"
                :max="4"
                :step="0.1"
                :precision="1"
                placeholder="请输入GPA"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="技能标签">
              <el-select
                v-model="formData.skills"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="请选择或输入技能标签"
                style="width: 100%"
              >
                <el-option
                  v-for="skill in SKILL_OPTIONS"
                  :key="skill"
                  :label="skill"
                  :value="skill"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="目标城市">
              <el-input v-model="formData.targetCity" placeholder="请输入目标城市" clearable />
            </el-form-item>

            <el-form-item label="实习经历">
              <el-input
                v-model="formData.internship"
                type="textarea"
                :rows="3"
                placeholder="请描述您的实习经历"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                @click="handleAnalyze"
                class="analyze-btn"
              >
                <el-icon v-if="!loading"><Cpu /></el-icon>
                开始分析
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 历史记录 -->
          <div v-if="historyList.length > 0" class="history-section">
            <div class="section-title">
              <el-icon><Clock /></el-icon>
              历史记录
            </div>
            <div class="history-list">
              <div v-for="(item, index) in historyList" :key="index" class="history-item-wrapper">
                <div class="history-item" @click="loadHistory(item)">
                  <div class="history-info">
                    <span class="history-date">{{ item.date }}</span>
                    <span class="history-score">{{ item.score }}分</span>
                  </div>
                </div>
                <el-icon class="history-delete" @click.stop="deleteHistory(index)">
                  <Delete />
                </el-icon>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧结果区域 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="17">
        <!-- 空白状态 -->
        <div v-if="!showResult && !loading" class="empty-result">
          <div class="empty-illustration">
            <svg width="180" height="140" viewBox="0 0 180 140" fill="none">
              <!-- 背景卡片 -->
              <rect
                x="20"
                y="20"
                width="140"
                height="100"
                rx="12"
                fill="#f0f7ff"
                stroke="#d9ecff"
                stroke-width="1.5"
              />
              <!-- 顶部装饰线 -->
              <rect x="35" y="40" width="60" height="8" rx="4" fill="#c0d9ff" />
              <rect x="35" y="55" width="90" height="6" rx="3" fill="#d9ecff" />
              <rect x="35" y="68" width="75" height="6" rx="3" fill="#d9ecff" />
              <!-- 图表占位 -->
              <circle cx="130" cy="75" r="20" fill="#e6f0ff" stroke="#b3d8ff" stroke-width="1" />
              <path
                d="M125 80 L130 70 L135 75 L140 65"
                stroke="#409EFF"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <!-- 闪光装饰 -->
              <circle cx="150" cy="30" r="4" fill="#409EFF" opacity="0.6" />
              <circle cx="25" cy="110" r="3" fill="#67C23A" opacity="0.5" />
            </svg>
          </div>
          <h3 class="empty-title">就业竞争力分析</h3>
          <p class="empty-desc">填写左侧基本信息，AI 将为您生成多维度就业竞争力分析报告</p>
          <div class="empty-features">
            <span class="feature-tag"
              ><el-icon><User /></el-icon> 智能画像</span
            >
            <span class="feature-tag"
              ><el-icon><DataAnalysis /></el-icon> 多维分析</span
            >
            <span class="feature-tag"
              ><el-icon><TrendCharts /></el-icon> 趋势预测</span
            >
          </div>
        </div>

        <!-- 加载分析状态 -->
        <div v-else-if="loading" class="loading-result">
          <div class="loading-animation">
            <div class="loading-ring">
              <div class="ring ring-1"></div>
              <div class="ring ring-2"></div>
              <div class="ring ring-3"></div>
              <div class="loading-icon">
                <el-icon :size="32"><Cpu /></el-icon>
              </div>
            </div>
            <div class="loading-text">
              <span class="loading-title">AI 正在分析中...</span>
              <span class="loading-steps">
                <span class="step" :class="{ active: true }">✓ 解析信息</span>
                <span class="step-arrow">→</span>
                <span class="step" :class="{ active: true }">✓ 检索数据</span>
                <span class="step-arrow">→</span>
                <span class="step" :class="{ active: true }">生成报告</span>
              </span>
            </div>
          </div>
          <div class="loading-cards">
            <div class="skeleton-card">
              <div class="skeleton-header"></div>
              <div class="skeleton-body"></div>
            </div>
            <div class="skeleton-card">
              <div class="skeleton-header"></div>
              <div class="skeleton-body"></div>
            </div>
          </div>
        </div>

        <!-- 分析结果 -->
        <div v-else class="result-content">
          <!-- 第一行：仪表盘 + 雷达图 -->
          <el-row :gutter="20" class="result-row">
            <el-col :span="10">
              <el-card class="art-card-xs result-card">
                <template #header>
                  <span class="card-title">综合评分</span>
                </template>
                <ArtGaugeChart
                  :value="resultData.overallScore"
                  name="就业竞争力"
                  :height="'260px'"
                />
                <div class="percentile-info">
                  <el-icon><Top /></el-icon>
                  超过了 {{ resultData.overallScore }}% 的求职者
                </div>
              </el-card>
            </el-col>
            <el-col :span="14">
              <el-card class="art-card-xs result-card">
                <template #header>
                  <span class="card-title">五维能力分析</span>
                </template>
                <ArtRadarChart
                  :indicator="radarIndicator"
                  :data="radarData"
                  :height="'260px'"
                  :colors="['#409EFF', '#67C23A', '#E6A23C']"
                />
              </el-card>
            </el-col>
          </el-row>

          <!-- 第二行：能力进度条 -->
          <el-card class="art-card-xs result-card mt-4">
            <template #header>
              <span class="card-title">能力详情</span>
            </template>
            <div class="progress-list">
              <div
                v-for="(item, index) in progressList"
                :key="index"
                class="progress-item"
                :style="{ animationDelay: `${index * 100}ms` }"
              >
                <div class="progress-header">
                  <span class="progress-label">{{ item.label }}</span>
                  <span class="progress-value">{{ Math.round(item.value * 100) }}%</span>
                </div>
                <el-progress
                  :percentage="Math.round(item.value * 100)"
                  :stroke-width="12"
                  :color="item.color"
                  :show-text="false"
                />
              </div>
            </div>
          </el-card>

          <!-- 第三行：技能气泡图 + 优劣势 -->
          <el-row :gutter="20" class="result-row mt-4">
            <el-col :span="12">
              <el-card class="art-card-xs result-card">
                <template #header>
                  <span class="card-title">技能分布</span>
                </template>
                <ArtBubbleChart :data="skillBubbleData" :height="'280px'" />
                <div class="skill-legend">
                  <span class="legend-item"><span class="dot green"></span>已掌握</span>
                  <span class="legend-item"><span class="dot yellow"></span>学习中</span>
                  <span class="legend-item"><span class="dot red"></span>需提升</span>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="art-card-xs result-card">
                <template #header>
                  <span class="card-title">优劣势分析</span>
                </template>
                <div class="analysis-section">
                  <div class="strengths">
                    <h4>
                      <el-icon><SuccessFilled /></el-icon>
                      优势
                    </h4>
                    <ul>
                      <li v-for="(item, index) in resultData.strengths" :key="index">
                        <el-icon><Check /></el-icon>
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                  <div class="weaknesses">
                    <h4>
                      <el-icon><WarningFilled /></el-icon>
                      劣势
                    </h4>
                    <ul>
                      <li v-for="(item, index) in resultData.weaknesses" :key="index">
                        <el-icon><Close /></el-icon>
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 第四行：提升建议 -->
          <el-card class="art-card-xs result-card mt-4">
            <template #header>
              <div class="card-header">
                <span class="card-title">提升建议</span>
                <el-tag v-if="completedCount > 0" type="success" size="small">
                  已完成 {{ completedCount }}/{{ resultData.suggestions.length }}
                </el-tag>
              </div>
            </template>
            <div class="suggestions-list">
              <div
                v-for="(item, index) in categorizedSuggestions"
                :key="index"
                class="suggestion-item"
                :class="{ completed: item.completed }"
              >
                <div class="suggestion-checkbox">
                  <el-checkbox v-model="item.completed" />
                </div>
                <div class="suggestion-content">
                  <div class="suggestion-header">
                    <el-tag :type="getCategoryType(item.category)" size="small">
                      {{ getCategoryLabel(item.category) }}
                    </el-tag>
                    <el-tag
                      v-if="item.priority === 'high'"
                      type="danger"
                      size="small"
                      effect="dark"
                    >
                      紧急
                    </el-tag>
                    <el-tag v-else-if="item.priority === 'medium'" type="warning" size="small">
                      一般
                    </el-tag>
                  </div>
                  <p class="suggestion-text">{{ item.suggestion }}</p>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { onMounted } from 'vue'
  import { getAiProfile } from '@/api/ai'
  import { fetchStudentProfile, getAiHistory, saveAiHistory, deleteAiHistory } from '@/api/student'
  import { ElMessage } from 'element-plus'
  import {
    Cpu,
    Clock,
    Top,
    SuccessFilled,
    WarningFilled,
    Check,
    Close,
    User,
    DataAnalysis,
    TrendCharts,
    Delete
  } from '@element-plus/icons-vue'
  import ArtGaugeChart from '@/components/core/charts/art-gauge-chart/index.vue'
  import ArtRadarChart from '@/components/core/charts/art-radar-chart/index.vue'
  import ArtBubbleChart from '@/components/core/charts/art-bubble-chart/index.vue'

  defineOptions({ name: 'AiProfile' })

  interface ProfileResult {
    overallScore: number
    professional_match: number
    skill_match: number
    city_demand: number
    internship_score: number
    education_background: number
    strengths: string[]
    weaknesses: string[]
    suggestions: string[]
  }

  interface HistoryItem {
    record_id?: string
    date: string
    score: number
    input_data?: {
      major?: string
      gpa?: number
      skills?: string[]
      targetCity?: string
      target_city?: string
      internship?: string
    }
    data: ProfileResult
  }

  interface CategorizedSuggestion {
    suggestion: string
    category: 'skill' | 'experience' | 'job-hunting' | 'other'
    priority: 'high' | 'medium' | 'low'
    completed: boolean
  }

  const loading = ref(false)
  const showResult = ref(false)
  const HISTORY_KEY = 'ai_profile_history'
  const historyList = ref<HistoryItem[]>([])

  // 从 localStorage 加载历史记录
  const initHistory = () => {
    try {
      const saved = localStorage.getItem(HISTORY_KEY)
      if (saved) {
        historyList.value = JSON.parse(saved)
      }
    } catch (e) {
      console.error('加载本地历史记录失败:', e)
    }
  }

  // 从数据库加载历史记录（与本地同时加载）
  const loadHistoryFromServer = async () => {
    try {
      const res: any = await getAiHistory('employment_profile', 1, 20)
      // HTTP工具已解包数据，res直接是数组
      if (Array.isArray(res) && res.length > 0) {
        // 转换为 HistoryItem 格式
        const serverItems: HistoryItem[] = res.map((item: any) => ({
          record_id: item.record_id,
          date: item.date,
          score: item.score,
          input_data: item.input_data,
          data: item.result_data || {}
        }))

        // 合并本地和服务器数据（根据 record_id 去重）
        const localIds = new Set(historyList.value.map((item) => item.record_id).filter(Boolean))
        const newServerItems = serverItems.filter((item) => !localIds.has(item.record_id))

        if (newServerItems.length > 0) {
          // 追加到列表（不在此处持久化，避免覆盖本地更新）
          historyList.value = [...historyList.value, ...newServerItems]
        }
      }
    } catch (e) {
      console.error('加载服务器历史记录失败:', e)
    }
  }

  // 合并并排序所有历史记录
  const mergeAndSortHistory = () => {
    // 按日期排序（新的在前）
    historyList.value.sort((a, b) => {
      const dateA = new Date(a.date).getTime() || 0
      const dateB = new Date(b.date).getTime() || 0
      return dateB - dateA
    })
    // 只保留最近20条
    if (historyList.value.length > 20) {
      historyList.value = historyList.value.slice(0, 20)
    }
    persistHistory()
  }

  // 保存历史记录到 localStorage
  const persistHistory = () => {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(historyList.value))
    } catch (e) {
      console.error('保存本地历史记录失败:', e)
    }
  }

  const resultData = ref<ProfileResult>({
    overallScore: 0,
    professional_match: 0,
    skill_match: 0,
    city_demand: 0,
    internship_score: 0,
    education_background: 0,
    strengths: [],
    weaknesses: [],
    suggestions: []
  })

  const formData = ref({
    major: '',
    gpa: 3.0,
    skills: [] as string[],
    targetCity: '',
    internship: ''
  })

  const categorizedSuggestions = ref<CategorizedSuggestion[]>([])

  const completedCount = computed(
    () => categorizedSuggestions.value.filter((item) => item.completed).length
  )

  const SKILL_OPTIONS = [
    'JavaScript',
    'TypeScript',
    'Python',
    'Java',
    'React',
    'Vue',
    'Node.js',
    'SQL',
    'Git',
    '数据分析',
    '机器学习',
    '人工智能',
    'Go',
    'Rust',
    'Docker',
    'Kubernetes'
  ]

  const radarIndicator = computed(() => [
    { name: '专业匹配度', max: 100 },
    { name: '技能匹配度', max: 100 },
    { name: '城市需求', max: 100 },
    { name: '实习经历', max: 100 },
    { name: '学历背景', max: 100 }
  ])

  const radarData = computed(() => [
    {
      name: '当前能力',
      value: [
        resultData.value.professional_match * 100,
        resultData.value.skill_match * 100,
        resultData.value.city_demand * 100,
        resultData.value.internship_score * 100,
        resultData.value.education_background * 100
      ]
    }
  ])

  const progressList = computed(() => [
    { label: '专业匹配度', value: resultData.value.professional_match, color: '#409EFF' },
    { label: '技能匹配度', value: resultData.value.skill_match, color: '#67C23A' },
    { label: '城市需求', value: resultData.value.city_demand, color: '#E6A23C' },
    { label: '实习经历', value: resultData.value.internship_score, color: '#F56C6C' },
    { label: '学历背景', value: resultData.value.education_background, color: '#909399' }
  ])

  // 技能气泡图数据
  const skillBubbleData = computed(() => {
    return formData.value.skills.map((skill, index) => {
      // 模拟数据：随机生成掌握度和相关度
      const mastery = Math.random() * 0.5 + 0.3 // 0.3-0.8
      const relevance = Math.random() * 0.5 + 0.4 // 0.4-0.9
      return {
        name: skill,
        mastery,
        relevance,
        weight: 1 + Math.random() * 0.5
      }
    })
  })

  // 对建议进行分类和优先级排序
  const categorizeSuggestions = (suggestions: string[]): CategorizedSuggestion[] => {
    return suggestions.map((suggestion) => {
      let category: CategorizedSuggestion['category'] = 'other'
      let priority: CategorizedSuggestion['priority'] = 'medium'

      if (suggestion.includes('实习') || suggestion.includes('经验')) {
        category = 'experience'
        priority = 'high'
      } else if (
        suggestion.includes('技能') ||
        suggestion.includes('认证') ||
        suggestion.includes('证书')
      ) {
        category = 'skill'
        priority = 'medium'
      } else if (
        suggestion.includes('城市') ||
        suggestion.includes('竞争') ||
        suggestion.includes('机会')
      ) {
        category = 'job-hunting'
        priority = 'low'
      }

      return { suggestion, category, priority, completed: false }
    })
  }

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      skill: '技能提升',
      experience: '经验积累',
      'job-hunting': '求职技巧',
      other: '其他'
    }
    return labels[category] || '其他'
  }

  const getCategoryType = (category: string): '' | 'success' | 'warning' | 'info' => {
    const types: Record<string, '' | 'success' | 'warning' | 'info'> = {
      skill: 'success',
      experience: 'warning',
      'job-hunting': 'info',
      other: ''
    }
    return types[category] || ''
  }

  // 加载学生画像数据
  const loadProfile = async () => {
    try {
      const profile: any = await fetchStudentProfile()
      if (profile && profile.major !== undefined) {
        formData.value = {
          major: profile.major || '',
          gpa: profile.gpa || 3.0,
          skills: profile.skills || [],
          targetCity: profile.desire_city || '',
          internship: profile.internship || ''
        }
      }
    } catch (error) {
      console.error('加载学生画像失败:', error)
    }
  }

  // 从历史记录加载
  const loadHistory = (item: HistoryItem) => {
    resultData.value = item.data
    categorizedSuggestions.value = categorizeSuggestions(item.data.suggestions)
    // 从历史记录的 input_data 恢复表单数据（用于技能分布图）
    if (item.input_data) {
      formData.value = {
        major: item.input_data.major || '',
        gpa: item.input_data.gpa || 3.0,
        skills: item.input_data.skills || [],
        targetCity: item.input_data.targetCity || item.input_data.target_city || '',
        internship: item.input_data.internship || ''
      }
    }
    showResult.value = true
  }

  // 删除历史记录
  const deleteHistory = (index: number) => {
    ElMessageBox.confirm('确定要删除这条记录吗？', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(async () => {
        const item = historyList.value[index]
        // 如果有 record_id，尝试从服务器删除
        if (item && item.record_id) {
          try {
            await deleteAiHistory(item.record_id)
          } catch (e) {
            console.error('从服务器删除历史记录失败:', e)
          }
        }
        historyList.value.splice(index, 1)
        persistHistory()
        ElMessage.success('已删除')
      })
      .catch(() => {})
  }

  // 保存到历史记录
  const saveToHistory = async (data: ProfileResult) => {
    const now = new Date()
    const dateStr = `${now.getMonth() + 1}/${now.getDate()} ${now.getHours()}:${now.getMinutes()}`
    const newItem: HistoryItem = {
      date: dateStr,
      score: data.overallScore,
      input_data: formData.value,
      data
    }

    // 保存到数据库
    try {
      const res: any = await saveAiHistory({
        analysis_type: 'employment_profile',
        input_data: formData.value,
        result_data: data
      })
      // HTTP工具已解包数据，res直接是 { record_id: string } 格式
      if (res && res.record_id) {
        newItem.record_id = res.record_id
      }
    } catch (e) {
      console.error('保存历史记录到服务器失败:', e)
    }

    historyList.value.unshift(newItem)
    // 只保留最近5条
    if (historyList.value.length > 5) {
      historyList.value.pop()
    }
    persistHistory()
  }

  onMounted(async () => {
    // 同时加载本地缓存和数据库
    initHistory()
    await loadHistoryFromServer()
    // 合并并排序
    mergeAndSortHistory()
    loadProfile()
  })

  const handleAnalyze = async () => {
    if (!formData.value.major) {
      ElMessage.warning('请输入专业名称')
      return
    }

    // 提示用户完善目标城市信息
    if (!formData.value.targetCity) {
      ElMessage.info('目标城市未填写，AI 分析结果可能不够精准，建议先在"个人档案"中完善信息')
    }

    loading.value = true
    try {
      const res: any = await getAiProfile(formData.value)
      if (res.status === 'success') {
        // 使用真实数据或模拟数据
        const analysisData: ProfileResult = res || {
          overallScore: 78,
          professional_match: 0.82,
          skill_match: 0.75,
          city_demand: 0.68,
          internship_score: 0.65,
          education_background: 0.88,
          strengths: [
            '专业基础扎实，专业排名靠前',
            '学历背景符合目标岗位要求',
            '具备多项技术栈，学习能力强'
          ],
          weaknesses: ['实习经验相对不足', '目标城市竞争激烈', '部分技能认证缺失'],
          suggestions: [
            '建议增加2-3个月相关实习经验',
            '可考虑备考相关技能认证证书',
            '关注二三线城市就业机会，降低竞争压力',
            '建议参加行业内的技术交流活动',
            '提升项目实战经验'
          ]
        }

        resultData.value = analysisData
        categorizedSuggestions.value = categorizeSuggestions(analysisData.suggestions)
        saveToHistory(analysisData)
        showResult.value = true
        ElMessage.success('分析完成')
      } else {
        ElMessage.error(res.message || '分析失败')
      }
    } catch (error) {
      console.error('AI 分析失败:', error)
      ElMessage.error('分析失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .page-ai-profile {
    padding: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .card-title {
    font-size: 15px;
    font-weight: 600;
  }

  .ai-form {
    padding: 10px 0;
  }

  .analyze-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
  }

  /* 空白状态 */
  .empty-result {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 500px;
    background: linear-gradient(135deg, #f5f9ff 0%, #e8f4ff 100%);
    border-radius: 12px;
    border: 1px dashed #c0d9ff;
    padding: 40px;
    transition: all 0.3s ease;
  }

  .empty-illustration {
    margin-bottom: 24px;
    animation: float 3s ease-in-out infinite;
  }

  @keyframes float {
    0%,
    100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-10px);
    }
  }

  .empty-title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 12px 0;
  }

  .empty-desc {
    font-size: 14px;
    color: #909399;
    margin: 0 0 24px 0;
    text-align: center;
    max-width: 320px;
    line-height: 1.6;
  }

  .empty-features {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .feature-tag {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: #fff;
    border-radius: 20px;
    font-size: 13px;
    color: #606266;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
    border: 1px solid #e8f4ff;
  }

  .feature-tag .el-icon {
    color: #409eff;
  }

  /* 加载分析状态 */
  .loading-result {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 500px;
    background: linear-gradient(135deg, #f5f9ff 0%, #e8f4ff 100%);
    border-radius: 12px;
    border: 1px dashed #c0d9ff;
    padding: 40px;
  }

  .loading-animation {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 40px;
  }

  .loading-ring {
    position: relative;
    width: 100px;
    height: 100px;
    margin-bottom: 24px;
  }

  .ring {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 3px solid transparent;
    animation: ringPulse 2s ease-in-out infinite;
  }

  .ring-1 {
    border-top-color: #409eff;
    animation-delay: 0s;
  }

  .ring-2 {
    inset: 8px;
    border-top-color: #67c23a;
    animation-delay: 0.2s;
    animation-direction: reverse;
  }

  .ring-3 {
    inset: 16px;
    border-top-color: #e6a23c;
    animation-delay: 0.4s;
  }

  @keyframes ringPulse {
    0% {
      transform: rotate(0deg);
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
    100% {
      transform: rotate(360deg);
      opacity: 1;
    }
  }

  .loading-icon {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #409eff;
    animation: iconPulse 1s ease-in-out infinite;
  }

  @keyframes iconPulse {
    0%,
    100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.1);
    }
  }

  .loading-text {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .loading-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }

  .loading-steps {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #909399;
  }

  .step {
    padding: 4px 12px;
    background: #f0f0f0;
    border-radius: 12px;
    transition: all 0.3s ease;
  }

  .step.active {
    background: #e6f7e6;
    color: #67c23a;
  }

  .step-arrow {
    color: #c0c0c0;
  }

  .loading-cards {
    display: flex;
    gap: 20px;
    width: 100%;
    max-width: 600px;
  }

  .skeleton-card {
    flex: 1;
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  }

  .skeleton-header {
    height: 20px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 6px;
    margin-bottom: 16px;
  }

  .skeleton-body {
    height: 100px;
    background: linear-gradient(90deg, #f8f8f8 25%, #f0f0f0 50%, #f8f8f8 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px;
  }

  @keyframes shimmer {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }

  .result-content {
    animation: fadeIn 0.4s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(15px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .result-card {
    height: 100%;
  }

  .result-row {
    animation: slideUp 0.5s ease-out;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .mt-4 {
    margin-top: 16px;
  }

  /* 历史记录 */
  .history-section {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px dashed #e0e0e0;
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    font-weight: 600;
    color: #666;
    margin-bottom: 12px;
  }

  .history-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .history-item-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .history-item {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: #f5f7fa;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .history-item:hover {
    background: #ecf5ff;
    transform: translateX(4px);
  }

  .history-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex: 1;
  }

  .history-date {
    font-size: 13px;
    color: #666;
  }

  .history-score {
    font-size: 14px;
    font-weight: 600;
    color: #409eff;
    margin-left: 16px;
  }

  .history-delete {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    color: #909399;
    font-size: 16px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .history-delete:hover {
    color: #f56c6c;
    background: rgba(245, 108, 108, 0.15);
  }

  .history-delete:hover {
    color: #f56c6c;
  }

  /* 百分位信息 */
  .percentile-info {
    text-align: center;
    margin-top: -10px;
    padding: 8px;
    color: #67c23a;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }

  /* 能力进度条 */
  .progress-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 10px 0;
  }

  .progress-item {
    animation: progressSlide 0.6s ease-out both;
  }

  @keyframes progressSlide {
    from {
      opacity: 0;
      transform: translateX(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .progress-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
  }

  .progress-label {
    font-size: 14px;
    color: #333;
  }

  .progress-value {
    font-size: 14px;
    font-weight: 600;
    color: #409eff;
  }

  /* 技能图例 */
  .skill-legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: -10px;
    padding: 10px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #666;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .dot.green {
    background: #67c23a;
  }

  .dot.yellow {
    background: #e6a23c;
  }

  .dot.red {
    background: #f56c6c;
  }

  /* 优劣势分析 */
  .analysis-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .analysis-section h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-size: 15px;
  }

  .strengths h4 {
    color: #67c23a;
  }

  .weaknesses h4 {
    color: #f56c6c;
  }

  .analysis-section ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .analysis-section ul li {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 0;
    font-size: 14px;
    color: #555;
    border-bottom: 1px dashed #eee;
  }

  .analysis-section ul li:last-child {
    border-bottom: none;
  }

  .analysis-section ul li .el-icon {
    margin-top: 2px;
    flex-shrink: 0;
  }

  /* 建议列表 */
  .suggestions-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .suggestion-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    background: #f9f9f9;
    border-radius: 8px;
    transition: all 0.2s;
  }

  .suggestion-item:hover {
    background: #f0f0f0;
  }

  .suggestion-item.completed {
    opacity: 0.6;
    background: #f0f9eb;
  }

  .suggestion-item.completed .suggestion-text {
    text-decoration: line-through;
  }

  .suggestion-checkbox {
    padding-top: 2px;
  }

  .suggestion-content {
    flex: 1;
  }

  .suggestion-header {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
  }

  .suggestion-text {
    margin: 0;
    font-size: 14px;
    color: #333;
    line-height: 1.5;
  }
</style>
