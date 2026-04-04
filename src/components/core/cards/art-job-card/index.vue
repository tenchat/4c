<!-- 职位卡片组件 -->
<template>
  <div class="art-job-card" @click="handleClick">
    <!-- 顶部区域：企业信息 + 状态标签 -->
    <div class="card-header">
      <div class="company-info">
        <div class="company-logo">
          <span>{{ companyInitial }}</span>
        </div>
        <div class="company-detail">
          <h3 class="company-name">{{ companyName }}</h3>
          <p class="company-industry">{{ industryText }}</p>
        </div>
      </div>
      <ElTag v-if="isNew" type="success" size="small" class="new-tag">最新</ElTag>
    </div>

    <!-- 职位信息区域 -->
    <div class="card-body">
      <h2 class="job-title">{{ title }}</h2>

      <!-- 基本信息 -->
      <div class="info-grid">
        <div class="info-item">
          <ElIcon><Location /></ElIcon>
          <span>{{ city || '未知城市' }}</span>
        </div>
        <div class="info-item">
          <ElIcon><Briefcase /></ElIcon>
          <span>{{ experienceText }}</span>
        </div>
        <div class="info-item">
          <ElIcon><Reading /></ElIcon>
          <span>{{ degreeText }}</span>
        </div>
      </div>

      <!-- 薪资区域 -->
      <div class="salary-section">
        <span class="salary-label">月薪</span>
        <span class="salary-value">{{ salaryDisplay }}</span>
        <span class="salary-unit" v-if="salaryDisplay !== '面议'">元</span>
      </div>

      <!-- 技能标签 -->
      <div class="skills-section" v-if="keywords && keywords.length > 0">
        <ElTag
          v-for="(keyword, index) in displayKeywords"
          :key="index"
          :type="getTagType(index)"
          size="small"
          class="skill-tag"
        >
          {{ keyword }}
        </ElTag>
        <ElTag v-if="keywords.length > 3" size="small" class="more-tag">
          +{{ keywords.length - 3 }}
        </ElTag>
      </div>
    </div>

    <!-- 底部区域：时间 + 操作 -->
    <div class="card-footer">
      <div class="time-info">
        <ElIcon><Clock /></ElIcon>
        <span>{{ formatDate(publishedAt) }}</span>
      </div>
      <ElButton type="primary" size="small" class="apply-btn" @click.stop="handleApply">
        投递简历
      </ElButton>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { Location, Briefcase, Reading, Clock } from '@element-plus/icons-vue'

  defineOptions({ name: 'ArtJobCard' })

  interface Props {
    jobId: string
    title: string
    companyName: string
    industry?: string
    city?: string
    province?: string
    minSalary?: number
    maxSalary?: number
    keywords?: string[]
    publishedAt?: string
    expiredAt?: string
    degree?: number
    experience?: number
    description?: string
  }

  const props = withDefaults(defineProps<Props>(), {
    jobId: '',
    title: '',
    companyName: '',
    industry: '',
    city: '',
    province: '',
    minSalary: 0,
    maxSalary: 0,
    keywords: () => [],
    publishedAt: '',
    expiredAt: '',
    degree: 1,
    experience: 0,
    description: ''
  })

  const emit = defineEmits<{
    (e: 'click', job: Props): void
    (e: 'apply', job: Props): void
  }>()

  // 企业简称首字母
  const companyInitial = computed(() => {
    if (!props.companyName) return '企'
    return props.companyName.charAt(0).toUpperCase()
  })

  // 行业映射
  const INDUSTRY_MAP: Record<string, string> = {
    internet: '互联网/IT',
    finance: '金融',
    education: '教育',
    manufacturing: '制造业',
    real_estate: '房地产',
    healthcare: '医疗健康',
    government: '政府/事业单位',
    other: '其他'
  }

  const industryText = computed(() => INDUSTRY_MAP[props.industry || ''] || props.industry || '')

  // 经验要求文本
  const experienceText = computed(() => {
    if (props.experience === 0) return '经验不限'
    return `${props.experience}年经验`
  })

  // 学历要求文本
  const degreeText = computed(() => {
    const map: Record<number, string> = {
      1: '本科',
      2: '硕士',
      3: '博士',
      4: '大专'
    }
    return map[props.degree] || '学历不限'
  })

  // 是否为最新职位（7天内发布）
  const isNew = computed(() => {
    if (!props.publishedAt) return false
    const publishDate = new Date(props.publishedAt)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - publishDate.getTime()) / (1000 * 60 * 60 * 24))
    return diffDays <= 7
  })

  // 显示的关键词（最多3个）
  const displayKeywords = computed(() => props.keywords?.slice(0, 3) || [])

  // 获取标签类型
  const getTagType = (index: number) => {
    const types = ['primary', 'success', 'warning', 'info']
    return types[index % types.length] as any
  }

  // 格式化日期
  const formatDate = (dateStr: string | undefined): string => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }

  // 薪资显示文本
  const salaryDisplay = computed(() => {
    if (!props.minSalary && !props.maxSalary) return '面议'
    return `${props.minSalary || 0}~${props.maxSalary || 0}`
  })

  const handleClick = () => {
    emit('click', props)
  }

  const handleApply = () => {
    emit('apply', props)
  }
</script>

<style scoped>
  .art-job-card {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 20px;
    cursor: pointer;
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-light);
    border-radius: 12px;
    transition: all 0.3s ease;
  }

  .art-job-card:hover {
    border-color: var(--el-color-primary-light-5);
    box-shadow: 0 8px 24px rgb(0 0 0 / 8%);
    transform: translateY(-4px);
  }

  /* 头部区域 */
  .card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .company-info {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .company-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    font-size: 20px;
    font-weight: 600;
    color: var(--el-color-primary);
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-5),
      var(--el-color-primary-light-8)
    );
    border-radius: 10px;
  }

  .company-detail {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .company-name {
    margin: 0;
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .company-industry {
    margin: 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .new-tag {
    flex-shrink: 0;
  }

  /* 职位主体 */
  .card-body {
    display: flex;
    flex: 1;
    flex-direction: column;
  }

  .job-title {
    margin: 0 0 12px;
    font-size: 18px;
    font-weight: 600;
    line-height: 1.4;
    color: var(--el-text-color-primary);
  }

  /* 信息网格 */
  .info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 16px;
  }

  .info-item {
    display: flex;
    gap: 6px;
    align-items: center;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .info-item .el-icon {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }

  /* 薪资区域 */
  .salary-section {
    display: flex;
    gap: 4px;
    align-items: baseline;
    padding: 12px;
    margin-bottom: 16px;
    background: linear-gradient(
      135deg,
      rgba(var(--el-color-primary-rgb), 0.08),
      rgba(var(--el-color-primary-rgb), 0.03)
    );
    border-radius: 8px;
  }

  .salary-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .salary-value {
    font-size: 22px;
    font-weight: 700;
    color: var(--el-color-danger);
    letter-spacing: -0.5px;
  }

  .salary-unit {
    font-size: 12px;
    color: var(--el-color-danger);
  }

  /* 技能标签 */
  .skills-section {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .skill-tag {
    border-radius: 4px;
  }

  .more-tag {
    color: var(--el-text-color-secondary);
    background: var(--el-fill-color-light);
    border-color: var(--el-border-color-lighter);
    border-radius: 4px;
  }

  /* 底部区域 */
  .card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 16px;
    margin-top: 16px;
    border-top: 1px solid var(--el-border-color-extra-light);
  }

  .time-info {
    display: flex;
    gap: 6px;
    align-items: center;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .time-info .el-icon {
    font-size: 14px;
  }

  .apply-btn {
    padding: 6px 16px;
    border-radius: 16px;
  }
</style>
