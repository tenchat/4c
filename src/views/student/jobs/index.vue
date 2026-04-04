<!-- 岗位推荐页面 -->
<template>
  <div class="page-student-jobs">
    <!-- 顶部统计卡片 -->
    <ElRow :gutter="20" class="stats-row mb-5">
      <ElCol :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon bg-primary-light">
            <ElIcon><Briefcase /></ElIcon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ pagination.total }}</span>
            <span class="stat-label">在招职位</span>
          </div>
        </div>
      </ElCol>
      <ElCol :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon bg-success-light">
            <ElIcon><CircleCheck /></ElIcon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ appliedCount }}</span>
            <span class="stat-label">已投递</span>
          </div>
        </div>
      </ElCol>
      <ElCol :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon bg-warning-light">
            <ElIcon><TrendCharts /></ElIcon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ viewedCount }}</span>
            <span class="stat-label">薪资最高</span>
          </div>
        </div>
      </ElCol>
      <ElCol :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon bg-danger-light">
            <ElIcon><Star /></ElIcon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ newJobCount }}</span>
            <span class="stat-label">新增职位</span>
          </div>
        </div>
      </ElCol>
    </ElRow>

    <!-- 搜索筛选区域 -->
    <ElCard class="search-card mb-4" shadow="never">
      <div class="search-content">
        <div class="search-row">
          <ElInput
            v-model="searchForm.keyword"
            placeholder="搜索职位名称、公司名称"
            class="search-input"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <ElIcon><Search /></ElIcon>
            </template>
          </ElInput>

          <ElSelect
            v-model="searchForm.city"
            placeholder="选择城市"
            class="filter-select"
            clearable
          >
            <ElOption label="北京" value="北京" />
            <ElOption label="上海" value="上海" />
            <ElOption label="广州" value="广州" />
            <ElOption label="深圳" value="深圳" />
            <ElOption label="杭州" value="杭州" />
            <ElOption label="成都" value="成都" />
            <ElOption label="武汉" value="武汉" />
            <ElOption label="西安" value="西安" />
          </ElSelect>

          <ElSelect
            v-model="searchForm.industry"
            placeholder="选择行业"
            class="filter-select"
            clearable
          >
            <ElOption
              v-for="item in INDUSTRY_OPTIONS"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </ElSelect>

          <ElSelect v-model="salaryRange" placeholder="薪资范围" class="filter-select" clearable>
            <ElOption label="5k以下" value="0-5000" />
            <ElOption label="5k-10k" value="5000-10000" />
            <ElOption label="10k-20k" value="10000-20000" />
            <ElOption label="20k以上" value="20000-999999" />
          </ElSelect>
        </div>

        <div class="action-row">
          <ElButton type="primary" @click="handleSearch">
            <ElIcon><Search /></ElIcon>
            搜索
          </ElButton>
          <ElButton @click="handleReset">
            <ElIcon><RefreshLeft /></ElIcon>
            重置
          </ElButton>
          <ElButton type="success" @click="handleAIRecommend">
            <ElIcon><MagicStick /></ElIcon>
            AI智能推荐
          </ElButton>
        </div>
      </div>
    </ElCard>

    <!-- 排序和结果信息 -->
    <div class="list-header mb-4">
      <div class="result-info">
        <span class="result-text">
          共找到 <span class="highlight">{{ pagination.total }}</span> 个职位
        </span>
      </div>
      <div class="sort-info">
        <ElDropdown @command="handleSortCommand">
          <span class="sort-trigger">
            <ElIcon><Sort /></ElIcon>
            {{ sortLabel }}
            <ElIcon><ArrowDown /></ElIcon>
          </span>
          <template #dropdown>
            <ElDropdownMenu>
              <ElDropdownItem command="default" :class="{ active: sortField === 'default' }">
                默认排序
              </ElDropdownItem>
              <ElDropdownItem
                command="salary_desc"
                :class="{ active: sortField === 'salary_desc' }"
              >
                薪资最高
              </ElDropdownItem>
              <ElDropdownItem command="salary_asc" :class="{ active: sortField === 'salary_asc' }">
                薪资最低
              </ElDropdownItem>
              <ElDropdownItem command="time_desc" :class="{ active: sortField === 'time_desc' }">
                最新发布
              </ElDropdownItem>
            </ElDropdownMenu>
          </template>
        </ElDropdown>
      </div>
    </div>

    <!-- 职位列表 -->
    <div class="job-list" v-loading="loading">
      <ElEmpty v-if="!loading && data.length === 0" description="暂无符合条件的职位" />

      <ElRow :gutter="20" v-else>
        <ElCol
          v-for="job in data"
          :key="job.job_id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          class="job-col"
        >
          <ArtJobCard
            :jobId="job.job_id"
            :title="job.title"
            :companyName="job.company_name || '未知公司'"
            :industry="job.industry"
            :city="job.city"
            :province="job.province"
            :minSalary="job.min_salary || 0"
            :maxSalary="job.max_salary || 0"
            :keywords="job.keywords || []"
            :publishedAt="job.published_at"
            :expiredAt="job.expired_at"
            :degree="job.min_degree || 1"
            :experience="job.min_exp_years || 0"
            :description="job.description"
            @click="handleViewJob(job)"
            @apply="handleApply(job)"
          />
        </ElCol>
      </ElRow>

      <!-- 分页 -->
      <div class="pagination-wrapper mt-6" v-if="pagination.total > 0">
        <ElPagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[12, 24, 36, 48]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 职位详情抽屉 -->
    <ElDrawer
      v-model="drawerVisible"
      :title="currentJob?.title || '职位详情'"
      size="480px"
      class="job-drawer"
    >
      <div class="job-detail" v-if="currentJob">
        <!-- 公司信息 -->
        <div class="detail-section company-section">
          <div class="company-header">
            <div class="company-logo">
              {{ (currentJob.company_name || '企').charAt(0) }}
            </div>
            <div class="company-info">
              <h3 class="company-name">{{ currentJob.company_name }}</h3>
              <p class="company-meta">
                <ElIcon><OfficeBuilding /></ElIcon>
                {{ industryText(currentJob.industry) }}
              </p>
              <p class="company-meta">
                <ElIcon><Location /></ElIcon>
                {{ currentJob.city || '未知城市' }}
                <template v-if="currentJob.province"> · {{ currentJob.province }}</template>
              </p>
            </div>
          </div>
        </div>

        <!-- 薪资信息 -->
        <div class="detail-section salary-section">
          <div class="salary-display">
            <span class="salary-value">
              {{ getSalaryDisplay(currentJob.min_salary, currentJob.max_salary) }}
            </span>
            <span
              class="salary-unit"
              v-if="getSalaryDisplay(currentJob.min_salary, currentJob.max_salary) !== '面议'"
              >元/月</span
            >
          </div>
        </div>

        <!-- 基本要求 -->
        <div class="detail-section">
          <h4 class="section-title">
            <ElIcon><Document /></ElIcon>
            职位要求
          </h4>
          <div class="requirement-grid">
            <div class="requirement-item">
              <span class="req-label">学历要求</span>
              <span class="req-value">{{ degreeText(currentJob.min_degree) }}</span>
            </div>
            <div class="requirement-item">
              <span class="req-label">经验要求</span>
              <span class="req-value">
                {{ currentJob.min_exp_years === 0 ? '经验不限' : `${currentJob.min_exp_years}年` }}
              </span>
            </div>
            <div class="requirement-item">
              <span class="req-label">工作城市</span>
              <span class="req-value">{{ currentJob.city || '未知' }}</span>
            </div>
            <div class="requirement-item">
              <span class="req-label">职位行业</span>
              <span class="req-value">{{ industryText(currentJob.industry) }}</span>
            </div>
          </div>
        </div>

        <!-- 技能标签 -->
        <div class="detail-section" v-if="currentJob.keywords?.length">
          <h4 class="section-title">
            <ElIcon><Collection /></ElIcon>
            技能要求
          </h4>
          <div class="keywords-display">
            <ElTag
              v-for="(kw, idx) in currentJob.keywords"
              :key="idx"
              :type="['primary', 'success', 'warning'][idx % 3]"
              class="keyword-tag"
            >
              {{ kw }}
            </ElTag>
          </div>
        </div>

        <!-- 职位描述 -->
        <div class="detail-section">
          <h4 class="section-title">
            <ElIcon><Reading /></ElIcon>
            职位描述
          </h4>
          <div class="description-content">
            {{ currentJob.description || '暂无职位描述' }}
          </div>
        </div>

        <!-- 发布时间 -->
        <div class="detail-section time-section">
          <ElIcon><Clock /></ElIcon>
          发布时间：{{ formatFullDate(currentJob.published_at) }}
          <template v-if="currentJob.expired_at">
            · 截止：{{ formatFullDate(currentJob.expired_at) }}
          </template>
        </div>
      </div>

      <template #footer>
        <div class="drawer-footer">
          <ElButton @click="drawerVisible = false">关闭</ElButton>
          <ElButton type="primary" @click="handleApplyFromDrawer">
            <ElIcon><Position /></ElIcon>
            投递简历
          </ElButton>
        </div>
      </template>
    </ElDrawer>

    <!-- AI智能推荐弹窗 -->
    <ElDialog v-model="recommendDialogVisible" title="AI智能推荐" width="720px" :close-on-click-modal="false">
      <template #header>
        <span>AI智能推荐</span>
        <el-link type="primary" class="rules-link" @click="showRulesDialog = true">推荐规则</el-link>
      </template>
      <div v-loading="recommendLoading">
        <ElEmpty v-if="!recommendations.length" description="暂未找到合适的推荐，请先完善您的简历信息" />
        <div v-else class="recommend-list">
          <div v-for="item in recommendations" :key="item.job_id" class="recommend-card">
            <div class="recommend-header">
              <h4 class="recommend-title">{{ item.title }}</h4>
              <ElTag type="success">{{ (item.match_score * 100).toFixed(0) }}% 匹配</ElTag>
            </div>
            <p class="recommend-company">
              <ElIcon><OfficeBuilding /></ElIcon>
              {{ item.company_name }}
            </p>
            <p class="recommend-meta">
              <ElIcon><Location /></ElIcon>
              {{ item.city }}
              <span class="salary-range">{{ item.min_salary }}-{{ item.max_salary }}元/月</span>
            </p>
            <div class="recommend-reason" v-if="item.description">
              <p class="reason-label">推荐理由：</p>
              <p class="reason-text">{{ item.description.substring(0, 100) }}{{ item.description.length > 100 ? '...' : '' }}</p>
            </div>
            <div class="recommend-actions">
              <ElButton size="small" type="primary" @click="handleViewRecommendJob(item)">查看详情</ElButton>
              <ElButton size="small" @click="handleApply(item as any)">投递简历</ElButton>
            </div>
          </div>
        </div>
      </div>
    </ElDialog>

    <!-- 推荐规则说明弹窗 -->
    <ElDialog v-model="showRulesDialog" title="推荐规则说明" width="500px">
      <div class="rules-content">
        <p class="rules-title">匹配度计算方式</p>
        <p class="rules-formula">匹配度 = (向量相似度分 + 规则匹配分) ÷ 2</p>

        <div class="rules-detail">
          <div class="rule-item">
            <span class="rule-icon">🔍</span>
            <div class="rule-info">
              <span class="rule-name">向量相似度 (50%)</span>
              <span class="rule-desc">基于您的简历信息（专业、技能、期望城市等）与岗位描述的语义匹配程度</span>
            </div>
          </div>

          <div class="rule-item">
            <span class="rule-icon">📍</span>
            <div class="rule-info">
              <span class="rule-name">城市匹配 (+20%)</span>
              <span class="rule-desc">您的期望城市与岗位所在城市匹配时加分</span>
            </div>
          </div>

          <div class="rule-item">
            <span class="rule-icon">💼</span>
            <div class="rule-info">
              <span class="rule-name">行业匹配 (+20%)</span>
              <span class="rule-desc">您的期望行业与岗位所属行业匹配时加分</span>
            </div>
          </div>

          <div class="rule-item">
            <span class="rule-icon">💰</span>
            <div class="rule-info">
              <span class="rule-name">薪资匹配 (+10%)</span>
              <span class="rule-desc">岗位薪资符合您的期望薪资范围时加分</span>
            </div>
          </div>
        </div>

        <p class="rules-tip">建议：完善您的简历信息（专业、期望城市、期望行业、期望薪资等）可获得更精准的推荐结果</p>
      </div>
    </ElDialog>
  </div>
</template>

<script setup lang="ts">
  import { fetchStudentJobs, applyForJob, getJobRecommendations, type JobRecommendation } from '@/api/student'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    Search,
    RefreshLeft,
    Sort,
    ArrowDown,
    Briefcase,
    CircleCheck,
    TrendCharts,
    Star,
    OfficeBuilding,
    Location,
    Document,
    Collection,
    Reading,
    Clock,
    Position,
    MagicStick
  } from '@element-plus/icons-vue'
  import ArtJobCard from '@/components/core/cards/art-job-card/index.vue'

  defineOptions({ name: 'StudentJobs' })

  interface JobItem {
    job_id: string
    title: string
    company_name?: string
    city: string
    province: string
    industry: string
    min_salary: number
    max_salary: number
    keywords: string[]
    status: number
    published_at: string
    expired_at: string
    min_degree: number
    min_exp_years: number
    description: string
  }

  const loading = ref(false)
  const data = ref<JobItem[]>([])
  const appliedCount = ref(0)
  const viewedCount = ref(0)
  const newJobCount = ref(0)

  const searchForm = ref({
    keyword: '',
    city: '',
    industry: '',
    min_salary: undefined as number | undefined,
    max_salary: undefined as number | undefined
  })

  const salaryRange = ref('')

  const pagination = reactive({
    current: 1,
    size: 12,
    total: 0
  })

  const sortField = ref('default')
  const sortLabel = ref('默认排序')

  const drawerVisible = ref(false)
  const currentJob = ref<JobItem | null>(null)

  const recommendDialogVisible = ref(false)
  const recommendations = ref<JobRecommendation[]>([])
  const recommendLoading = ref(false)
  const showRulesDialog = ref(false)

  const INDUSTRY_OPTIONS = [
    { label: '互联网/IT', value: 'internet' },
    { label: '金融', value: 'finance' },
    { label: '教育', value: 'education' },
    { label: '制造业', value: 'manufacturing' },
    { label: '房地产', value: 'real_estate' },
    { label: '医疗健康', value: 'healthcare' },
    { label: '政府/事业单位', value: 'government' },
    { label: '其他', value: 'other' }
  ]

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

  const industryText = (val?: string) => INDUSTRY_MAP[val || ''] || val || ''

  const degreeText = (val?: number) => {
    const map: Record<number, string> = { 1: '本科', 2: '硕士', 3: '博士', 4: '大专' }
    return map[val || 1] || '学历不限'
  }

  const formatFullDate = (dateStr?: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  // 薪资显示（0~0显示为面议）
  const getSalaryDisplay = (min?: number, max?: number) => {
    if (!min && !max) return '面议'
    return `${min || 0}~${max || 0}`
  }

  const handleSortCommand = (command: string) => {
    sortField.value = command
    const sortMap: Record<string, string> = {
      default: '默认排序',
      salary_desc: '薪资最高',
      salary_asc: '薪资最低',
      time_desc: '最新发布'
    }
    sortLabel.value = sortMap[command] || '默认排序'
    fetchJobs()
  }

  const fetchJobs = async () => {
    loading.value = true
    try {
      // 处理薪资范围
      if (salaryRange.value) {
        const [min, max] = salaryRange.value.split('-').map(Number)
        searchForm.value.min_salary = min
        searchForm.value.max_salary = max === 999999 ? undefined : max
      } else {
        searchForm.value.min_salary = undefined
        searchForm.value.max_salary = undefined
      }

      const res: any = await fetchStudentJobs({
        ...searchForm.value,
        page: pagination.current,
        page_size: pagination.size
      })

      if (res) {
        // 按排序字段处理数据
        let list = res.list || []
        if (sortField.value === 'salary_desc') {
          list = list.sort((a: JobItem, b: JobItem) => b.max_salary - a.max_salary)
        } else if (sortField.value === 'salary_asc') {
          list = list.sort((a: JobItem, b: JobItem) => a.min_salary - b.min_salary)
        } else if (sortField.value === 'time_desc') {
          list = list.sort(
            (a: JobItem, b: JobItem) =>
              new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
          )
        }

        data.value = list
        pagination.total = res.total || 0

        // 更新统计
        newJobCount.value = list.filter((j: JobItem) => {
          if (!j.published_at) return false
          const diff = new Date().getTime() - new Date(j.published_at).getTime()
          return diff / (1000 * 60 * 60 * 24) <= 7
        }).length
      }
    } catch (error) {
      console.error('获取岗位列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const handleSearch = () => {
    pagination.current = 1
    fetchJobs()
  }

  const handleReset = () => {
    searchForm.value = {
      keyword: '',
      city: '',
      industry: '',
      min_salary: undefined,
      max_salary: undefined
    }
    salaryRange.value = ''
    sortField.value = 'default'
    sortLabel.value = '默认排序'
    pagination.current = 1
    fetchJobs()
  }

  const handleSizeChange = (size: number) => {
    pagination.size = size
    pagination.current = 1
    fetchJobs()
  }

  const handleCurrentChange = (current: number) => {
    pagination.current = current
    fetchJobs()
  }

  const handleViewJob = (job: JobItem) => {
    currentJob.value = job
    drawerVisible.value = true
  }

  const handleApply = async (job: JobItem) => {
    try {
      await ElMessageBox.confirm(`确定要投递 "${job.title}" 岗位吗？`, '投递简历', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      })
      const res: any = await applyForJob(job.job_id)
      if (res.code === 200) {
        ElMessage.success('投递成功')
        appliedCount.value++
      } else {
        ElMessage.error(res.message || '投递失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('投递失败:', error)
      }
    }
  }

  const handleApplyFromDrawer = () => {
    if (currentJob.value) {
      handleApply(currentJob.value)
    }
  }

  const handleAIRecommend = async () => {
    recommendDialogVisible.value = true
    recommendLoading.value = true
    try {
      const res: any = await getJobRecommendations(6)
      recommendations.value = res?.recommendations || []
    } catch (e) {
      console.error('获取推荐失败', e)
      ElMessage.error('获取推荐失败')
    } finally {
      recommendLoading.value = false
    }
  }

  const handleViewRecommendJob = (item: JobRecommendation) => {
    const job: JobItem = {
      job_id: item.job_id,
      title: item.title,
      company_name: item.company_name,
      city: item.city,
      province: item.province,
      industry: item.industry,
      min_salary: item.min_salary,
      max_salary: item.max_salary,
      keywords: typeof item.keywords === 'string' ? item.keywords.split(',') : (item.keywords || []),
      status: 1,
      published_at: '',
      expired_at: '',
      min_degree: 1,
      min_exp_years: 0,
      description: item.description || ''
    }
    handleViewJob(job)
  }

  onMounted(() => {
    fetchJobs()
  })
</script>

<style scoped>
  .page-student-jobs {
    min-height: calc(100vh - 140px);
    padding: 20px;
    background: var(--el-fill-color-lighter);
  }

  /* 统计卡片 */
  .stats-row {
    margin-bottom: 16px;
  }

  .stat-card {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 20px;
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-extra-light);
    border-radius: 12px;
    box-shadow: 0 2px 12px rgb(0 0 0 / 4%);
  }

  .stat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    font-size: 24px;
    border-radius: 12px;
  }

  .bg-primary-light {
    color: var(--el-color-primary);
    background: rgb(64 158 255 / 12%);
  }

  .bg-success-light {
    color: var(--el-color-success);
    background: rgb(103 194 58 / 12%);
  }

  .bg-warning-light {
    color: var(--el-color-warning);
    background: rgb(230 162 60 / 12%);
  }

  .bg-danger-light {
    color: var(--el-color-danger);
    background: rgb(245 108 108 / 12%);
  }

  .stat-content {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .stat-value {
    font-size: 26px;
    font-weight: 700;
    line-height: 1;
    color: var(--el-text-color-primary);
  }

  .stat-label {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  /* 搜索卡片 */
  .search-card {
    background: var(--el-bg-color);
    border: none;
    border-radius: 12px;
  }

  .search-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .search-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .search-input {
    flex: 1;
    min-width: 200px;
  }

  .filter-select {
    width: 160px;
  }

  .action-row {
    display: flex;
    gap: 12px;
  }

  /* 列表头部 */
  .list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .result-info {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .result-text {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }

  .result-text .highlight {
    font-weight: 600;
    color: var(--el-color-primary);
  }

  .sort-trigger {
    display: flex;
    gap: 6px;
    align-items: center;
    padding: 8px 12px;
    font-size: 14px;
    color: var(--el-text-color-regular);
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .sort-trigger:hover {
    color: var(--el-color-primary);
    background: var(--el-fill-color-light);
  }

  /* 职位列表 */
  .job-col {
    margin-bottom: 20px;
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    padding: 20px 0;
  }

  /* 抽屉样式 */
  .job-detail {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .detail-section {
    padding-bottom: 20px;
    border-bottom: 1px solid var(--el-border-color-extra-light);
  }

  .detail-section:last-child {
    border-bottom: none;
  }

  .section-title {
    display: flex;
    gap: 8px;
    align-items: center;
    margin: 0 0 16px;
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  /* 公司信息 */
  .company-header {
    display: flex;
    gap: 16px;
  }

  .company-logo {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    font-size: 26px;
    font-weight: 600;
    color: var(--el-color-primary);
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-5),
      var(--el-color-primary-light-8)
    );
    border-radius: 14px;
  }

  .company-info {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .company-name {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .company-meta {
    display: flex;
    gap: 6px;
    align-items: center;
    margin: 0;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  /* 薪资展示 */
  .salary-section {
    padding: 20px;
    margin: 0 -20px;
    background: linear-gradient(135deg, rgb(64 158 255 / 8%), rgb(64 158 255 / 3%));
    border-radius: 12px;
  }

  .salary-display {
    display: flex;
    gap: 4px;
    align-items: baseline;
    justify-content: center;
  }

  .salary-value {
    font-size: 32px;
    font-weight: 700;
    color: var(--el-color-danger);
    letter-spacing: -1px;
  }

  .salary-unit {
    font-size: 14px;
    color: var(--el-color-danger);
  }

  /* 要求网格 */
  .requirement-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .requirement-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .req-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .req-value {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  /* 技能标签 */
  .keywords-display {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .keyword-tag {
    padding: 4px 12px;
    border-radius: 6px;
  }

  /* 描述内容 */
  .description-content {
    font-size: 14px;
    line-height: 1.8;
    color: var(--el-text-color-regular);
    white-space: pre-wrap;
  }

  /* 时间信息 */
  .time-section {
    display: flex;
    gap: 8px;
    align-items: center;
    padding-bottom: 0;
    font-size: 13px;
    color: var(--el-text-color-secondary);
    border-bottom: none;
  }

  /* 抽屉底部 */
  .drawer-footer {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }

  /* 下拉菜单选中状态 */
  :deep(.el-dropdown-menu__item.active) {
    font-weight: 500;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  /* AI智能推荐弹窗样式 */
  .recommend-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-height: 60vh;
    overflow-y: auto;
    padding-right: 8px;
  }

  .recommend-card {
    padding: 16px;
    background: var(--el-fill-color-lightest);
    border: 1px solid var(--el-border-color-extra-light);
    border-radius: 12px;
    transition: all 0.2s;
  }

  .recommend-card:hover {
    border-color: var(--el-color-primary-light-5);
    box-shadow: 0 4px 12px rgb(0 0 0 / 6%);
  }

  .recommend-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .recommend-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .recommend-company {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 0 0 6px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .recommend-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 0 0 12px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .salary-range {
    margin-left: 12px;
    font-weight: 500;
    color: var(--el-color-danger);
  }

  .recommend-reason {
    padding: 10px 12px;
    margin-bottom: 12px;
    background: var(--el-bg-color);
    border-radius: 8px;
  }

  .reason-label {
    margin: 0 0 4px;
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-regular);
  }

  .reason-text {
    margin: 0;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }

  .recommend-actions {
    display: flex;
    gap: 8px;
  }

  /* 推荐规则弹窗样式 */
  .rules-link {
    margin-left: auto;
    font-size: 13px;
  }

  .rules-content {
    padding: 8px 0;
  }

  .rules-title {
    margin: 0 0 8px;
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .rules-formula {
    margin: 0 0 16px;
    padding: 12px;
    font-family: monospace;
    font-size: 14px;
    color: var(--el-color-primary);
    background: var(--el-fill-color-light);
    border-radius: 6px;
  }

  .rules-detail {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
  }

  .rule-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }

  .rule-icon {
    font-size: 18px;
    line-height: 1.4;
  }

  .rule-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .rule-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .rule-desc {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .rules-tip {
    margin: 0;
    padding: 12px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    background: var(--el-color-primary-light-9);
    border-radius: 6px;
  }
</style>
