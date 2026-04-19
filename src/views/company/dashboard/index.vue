<template>
  <div class="company-dashboard">
    <!-- 顶部欢迎栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">欢迎回来，{{ companyName || '企业用户' }}</h1>
        <span class="page-subtitle"
          >{{ industry || '未填写行业' }} · {{ city || '未填写城市' }}</span
        >
      </div>
      <div class="header-right">
        <el-button @click="$router.push('/company/profile')">
          <el-icon><Edit /></el-icon>
          编辑企业信息
        </el-button>
      </div>
    </div>

    <!-- 状态卡片区 -->
    <div class="stat-row">
      <ArtStatsCard
        icon="ri:briefcase-line"
        iconStyle="bg-blue-500"
        :count="stats.publishedJobs"
        description="发布岗位"
      />
      <ArtStatsCard
        icon="ri:file-list-3-line"
        iconStyle="bg-green-500"
        :count="stats.receivedResumes"
        description="收到简历"
      />
      <ArtStatsCard
        icon="ri:user-follow-line"
        iconStyle="bg-orange-500"
        :count="stats.hiredCount"
        description="已录用"
      />
      <ArtStatsCard
        icon="ri:add-circle-line"
        iconStyle="bg-red-500"
        :count="stats.newThisMonth"
        description="本月新增"
      />
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧栏 -->
      <div class="left-column">
        <!-- 企业信息卡片 -->
        <div class="card">
          <div class="card-header">
            <span>企业信息</span>
            <el-button link type="primary" @click="$router.push('/company/profile')">
              编辑
            </el-button>
          </div>
          <div class="card-body">
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">企业规模</span>
                <span class="info-value">{{ scaleText }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">所在城市</span>
                <span class="info-value">{{ city || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">行业类型</span>
                <span class="info-value">{{ industry || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">认证状态</span>
                <span class="info-value">
                  <el-tag :type="verified ? 'success' : 'warning'" size="small">
                    {{ verified ? '已认证' : '未认证' }}
                  </el-tag>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 岗位管理 -->
        <div class="card">
          <div class="card-header">
            <span>岗位管理</span>
          </div>
          <div class="card-body">
            <div class="ai-tools">
              <div class="ai-tool" @click="$router.push('/company/post-job')">
                <el-icon><Plus /></el-icon>
                <span>发布岗位</span>
              </div>
              <div class="ai-tool" @click="$router.push('/company/jobs')">
                <el-icon><List /></el-icon>
                <span>管理岗位</span>
              </div>
              <div class="ai-tool" @click="$router.push('/company/resumes')">
                <el-icon><Document /></el-icon>
                <span>收到简历</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 简历统计 -->
        <div class="card">
          <div class="card-header">
            <span>简历统计</span>
            <el-button link type="primary" @click="$router.push('/company/resumes')">
              全部
            </el-button>
          </div>
          <div class="card-body">
            <div v-if="resumeStats.total > 0" class="app-stats">
              <div class="app-stat">
                <span class="stat-num">{{ resumeStats.total }}</span>
                <span class="stat-label">收到简历</span>
              </div>
              <div class="app-stat">
                <span class="stat-num">{{ resumeStats.viewed }}</span>
                <span class="stat-label">已查看</span>
              </div>
              <div class="app-stat">
                <span class="stat-num">{{ resumeStats.interested }}</span>
                <span class="stat-label">感兴趣</span>
              </div>
            </div>
            <el-empty v-else description="暂无简历记录" :image-size="50" />
          </div>
        </div>

        <!-- AI工具 start
        <div class="card">
          <div class="card-header">
            <span>AI助手</span>
          </div>
          <div class="card-body">
            <div class="ai-tools">
              <div class="ai-tool" @click="$router.push('/company/ai-analysis')">
                <el-icon><DataAnalysis /></el-icon>
                <span>人才分析</span>
              </div>
              <div class="ai-tool" @click="$router.push('/company/ai-match')">
                <el-icon><Connection /></el-icon>
                <span>智能匹配</span>
              </div>
              <div class="ai-tool" @click="$router.push('/company/ai-interview')">
                <el-icon><ChatDotRound /></el-icon>
                <span>面试辅助</span>
              </div>
            </div>
          </div>
        </div>
        AI工具 end -->
      </div>

      <!-- 中间栏 -->
      <div class="center-column">
        <!-- 招聘中的岗位 -->
        <div class="card">
          <div class="card-header">
            <span>招聘中的岗位</span>
            <el-button link type="primary" @click="$router.push('/company/jobs')">
              查看更多
            </el-button>
          </div>
          <div class="card-body">
            <div v-if="jobStatusList.length" class="job-list">
              <div
                v-for="job in jobStatusList"
                :key="job.job_id"
                class="job-item"
                @click="handleEditJob(job)"
              >
                <div class="job-info">
                  <span class="job-title">{{ job.title }}</span>
                  <el-tag :type="job.status === 1 ? 'success' : 'info'" size="small">
                    {{ job.status === 1 ? '招聘中' : job.status === 0 ? '已暂停' : '已结束' }}
                  </el-tag>
                </div>
                <div class="job-meta">
                  <span class="job-city"
                    ><el-icon><Location /></el-icon>{{ job.city }}</span
                  >
                  <span class="job-salary"
                    >{{ job.min_salary || '-' }}-{{ job.max_salary || '-' }}元/月</span
                  >
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无招聘中的岗位" :image-size="60" />
          </div>
        </div>

        <!-- 数据大屏入口 -->
        <div class="card databoard-card" @click="$router.push('/company/databoard')">
          <div class="databoard-content">
            <div class="databoard-icon">
              <el-icon :size="32"><DataLine /></el-icon>
            </div>
            <div class="databoard-text">
              <span class="databoard-title">企业数据大屏</span>
              <span class="databoard-desc">查看招聘数据分析</span>
            </div>
            <el-icon class="databoard-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 右侧栏 -->
      <div class="right-column">
        <!-- 岗位分布 -->
        <div class="card">
          <div class="card-header">
            <span>岗位分布</span>
          </div>
          <div class="card-body">
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">招聘中</span>
                <span class="info-value">{{ jobStatusCount.active || 0 }} 个</span>
              </div>
              <div class="info-item">
                <span class="info-label">已暂停</span>
                <span class="info-value">{{ jobStatusCount.paused || 0 }} 个</span>
              </div>
              <div class="info-item">
                <span class="info-label">已结束</span>
                <span class="info-value">{{ jobStatusCount.ended || 0 }} 个</span>
              </div>
              <div class="info-item">
                <span class="info-label">本月新增</span>
                <span class="info-value">{{ jobStatusCount.newThisMonth || 0 }} 个</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 最新投递 -->
        <div class="card" style="flex: 1">
          <div class="card-header">
            <span>最新投递</span>
            <el-button link type="primary" @click="$router.push('/company/resumes')">
              查看全部
            </el-button>
          </div>
          <div class="card-body" style="flex: 1">
            <div v-if="recentResumes.length" class="resume-activity-list">
              <div
                v-for="item in recentResumes"
                :key="item.application_id"
                class="resume-activity-item"
              >
                <div class="resume-activity-avatar">
                  {{ (item.student_name || '学').charAt(0) }}
                </div>
                <div class="resume-activity-content">
                  <div class="resume-activity-top">
                    <span class="resume-activity-name">{{ item.student_name }}</span>
                    <el-tag :type="getResumeStatusType(item.status)" size="small">
                      {{ getResumeStatusText(item.status) }}
                    </el-tag>
                  </div>
                  <div class="resume-activity-meta">
                    <span>{{ item.job_title }}</span>
                    <span>{{ formatResumeDate(item.applied_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无简历投递" :image-size="50" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import {
    Edit,
    Plus,
    List,
    Document,
    Location,
    DataLine,
    ArrowRight
  } from '@element-plus/icons-vue'
  import { fetchCompanyDashboard, fetchCompanyJobs, fetchCompanyResumes } from '@/api/company'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'

  defineOptions({ name: 'CompanyDashboard' })

  const router = useRouter()

  const companyName = ref('')
  const city = ref('')
  const industry = ref('')
  const verified = ref(false)
  const scale = ref(0)

  interface Stats {
    publishedJobs: number
    receivedResumes: number
    hiredCount: number
    newThisMonth: number
  }

  const stats = ref<Stats>({
    publishedJobs: 0,
    receivedResumes: 0,
    hiredCount: 0,
    newThisMonth: 0
  })

  interface Job {
    job_id: string
    title: string
    city: string
    min_salary: number
    max_salary: number
    status: number
  }

  interface ResumeItem {
    application_id: string
    job_id: string
    job_title: string
    student_name: string
    status: number
    applied_at: string
  }

  const jobStatusList = ref<Job[]>([])
  const jobStatusCount = ref<Record<string, number>>({})
  const resumeStats = ref({ total: 0, viewed: 0, interested: 0 })
  const recentResumes = ref<ResumeItem[]>([])

  // 简历状态映射
  const getResumeStatusText = (status: number) => {
    const map: Record<number, string> = {
      0: '已投递',
      1: '简历筛选',
      2: '面试中',
      3: '已录用',
      4: '已拒绝'
    }
    return map[status] || '未知'
  }

  const getResumeStatusType = (
    status: number
  ): 'success' | 'warning' | 'info' | 'danger' | 'primary' => {
    const map: Record<number, 'success' | 'warning' | 'info' | 'danger' | 'primary'> = {
      0: 'info',
      1: 'warning',
      2: 'primary',
      3: 'success',
      4: 'danger'
    }
    return map[status] || 'info'
  }

  const formatResumeDate = (dateStr: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const scaleText = computed(() => {
    const map: Record<number, string> = {
      1: '1-20人',
      2: '21-50人',
      3: '51-100人',
      4: '101-500人',
      5: '500人以上'
    }
    return map[scale.value] || '未填写'
  })

  const loadCompanyProfile = async () => {
    try {
      const res: any = await fetchCompanyDashboard()
      if (res) {
        companyName.value = res.company_name || ''
        city.value = res.city || ''
        industry.value = res.industry || ''
        verified.value = res.verified || false
        scale.value = res.scale || 0
        stats.value = {
          publishedJobs: res.published_jobs || 0,
          receivedResumes: res.received_resumes || 0,
          hiredCount: res.hired_count || 0,
          newThisMonth: res.new_this_month || 0
        }
        resumeStats.value = {
          total: res.received_resumes || 0,
          viewed: Math.floor((res.received_resumes || 0) * 0.6),
          interested: Math.floor((res.received_resumes || 0) * 0.3)
        }
      }
    } catch (error) {
      console.error('获取企业信息失败:', error)
    }
  }

  const loadJobs = async () => {
    try {
      const res: any = await fetchCompanyJobs({ status: 1, page: 1, page_size: 5 })
      if (res?.list) {
        jobStatusList.value = res.list
      }
      // 统计各状态岗位数量
      const allRes: any = await fetchCompanyJobs({ page: 1, page_size: 100 })
      if (allRes?.list) {
        const jobs = allRes.list
        jobStatusCount.value = {
          active: jobs.filter((j: Job) => j.status === 1).length,
          paused: jobs.filter((j: Job) => j.status === 0).length,
          ended: jobs.filter((j: Job) => j.status === 2).length,
          newThisMonth: stats.value.newThisMonth
        }
      }
    } catch (error) {
      console.error('获取岗位列表失败:', error)
    }
  }

  const handleEditJob = (row: Job) => {
    router.push(`/company/post-job?id=${row.job_id}`)
  }

  const loadRecentResumes = async () => {
    try {
      const res: any = await fetchCompanyResumes({ page: 1, page_size: 5 })
      if (res?.list) {
        recentResumes.value = res.list
      }
    } catch (error) {
      console.error('获取最近简历失败:', error)
    }
  }

  onMounted(async () => {
    await Promise.all([loadCompanyProfile(), loadJobs(), loadRecentResumes()])
  })
</script>

<style lang="scss" scoped>
  .company-dashboard {
    min-height: 100vh;
    padding-bottom: 24px;
    background: #f0f2f5;
  }

  // 顶部标题栏
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    background: #fff;
    border-bottom: 1px solid #e8e8e8;

    .header-left {
      display: flex;
      gap: 10px;
      align-items: baseline;

      .page-title {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
      }

      .page-subtitle {
        font-size: 13px;
        color: #8c8c8c;
      }
    }

    .header-right {
      display: flex;
      gap: 16px;
      align-items: center;
    }
  }

  // 数字卡片行
  .stat-row {
    display: flex;
    gap: 12px;
    padding: 20px 32px;

    > :deep(.art-card) {
      flex: 1;
      min-width: 0;
    }
  }

  // 主内容区
  .main-content {
    display: grid;
    grid-template-columns: 1fr 1.5fr 1fr;
    gap: 16px;
    padding: 0 32px;
  }

  .left-column,
  .center-column,
  .right-column {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  // 卡片样式
  .card {
    overflow: hidden;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 10px;

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 16px;
      font-size: 14px;
      font-weight: 500;
      color: #1a1a1a;
      border-bottom: 1px solid #f0f0f0;
    }

    .card-body {
      padding: 16px;
    }
  }

  // 信息列表
  .info-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .info-item {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .info-label {
      font-size: 13px;
      color: #8c8c8c;
    }

    .info-value {
      font-size: 13px;
      font-weight: 500;
      color: #1a1a1a;
    }
  }

  // AI工具
  .ai-tools {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;

    .ai-tool {
      display: flex;
      flex-direction: column;
      gap: 6px;
      align-items: center;
      padding: 14px 8px;
      color: #606266;
      cursor: pointer;
      background: #f5f7fa;
      border-radius: 8px;
      transition: background 0.2s;

      &:hover {
        background: #e8ecf1;
      }

      .el-icon {
        font-size: 20px;
        color: #409eff;
      }

      span {
        font-size: 12px;
        text-align: center;
      }
    }
  }

  // 岗位列表
  .job-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .job-item {
    padding: 12px;
    cursor: pointer;
    border: 1px solid #f0f0f0;
    border-radius: 6px;
    transition: all 0.2s;

    &:hover {
      background: #fafafa;
      border-color: #409eff;
    }

    .job-info {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 6px;

      .job-title {
        font-size: 14px;
        font-weight: 500;
        color: #1a1a1a;
      }
    }

    .job-meta {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #606266;

      .job-city {
        display: flex;
        gap: 4px;
        align-items: center;
      }

      .job-salary {
        font-weight: 500;
        color: #f56c6c;
      }
    }
  }

  // 数据大屏入口
  .databoard-card {
    cursor: pointer;
    background: linear-gradient(135deg, #e8f4f8 0%, #dbeafe 100%);
    border: none;
    transition: transform 0.2s;

    &:hover {
      transform: scale(1.01);
    }
  }

  .databoard-content {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 4px;

    .databoard-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      color: #409eff;
      background: #fff;
      border-radius: 8px;
    }

    .databoard-text {
      display: flex;
      flex: 1;
      flex-direction: column;
      gap: 4px;

      .databoard-title {
        font-size: 14px;
        font-weight: 600;
        color: #1a1a1a;
      }

      .databoard-desc {
        font-size: 12px;
        color: #8c8c8c;
      }
    }

    .databoard-arrow {
      font-size: 18px;
      color: #8c8c8c;
    }
  }

  // 简历统计
  .app-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    text-align: center;

    .app-stat {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .stat-num {
        font-size: 22px;
        font-weight: 700;
        color: #409eff;
      }

      .stat-label {
        font-size: 12px;
        color: #8c8c8c;
      }
    }
  }

  // 最新动态
  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .activity-item {
    display: flex;
    gap: 10px;
    align-items: flex-start;

    .activity-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      background: #f5f7fa;
      border-radius: 6px;
    }

    .activity-content {
      display: flex;
      flex: 1;
      flex-direction: column;
      gap: 2px;

      .activity-text {
        font-size: 13px;
        color: #1a1a1a;
      }

      .activity-time {
        font-size: 11px;
        color: #8c8c8c;
      }
    }
  }

  // 最新投递
  .resume-activity-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .resume-activity-item {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }
  }

  .resume-activity-avatar {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    font-size: 14px;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(135deg, #409eff, #66b1ff);
    border-radius: 50%;
  }

  .resume-activity-content {
    display: flex;
    flex: 1;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }

  .resume-activity-top {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
  }

  .resume-activity-name {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a1a;
  }

  .resume-activity-meta {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #8c8c8c;
  }

  // 空状态
  :deep(.el-empty) {
    padding: 12px 0;

    .el-empty__description {
      margin-top: 8px;
      font-size: 12px;
    }
  }

  // 响应式
  @media (width <= 1200px) {
    .main-content {
      grid-template-columns: 1fr 1fr;
    }

    .right-column {
      grid-column: span 2;
    }
  }

  @media (width <= 768px) {
    .stat-row {
      flex-wrap: wrap;
      gap: 8px;
      padding: 16px;
    }

    .main-content {
      grid-template-columns: 1fr;
      padding: 0 16px;
    }

    .right-column {
      grid-column: auto;
    }

    .page-header {
      flex-direction: column;
      gap: 12px;
      align-items: flex-start;
      padding: 12px 16px;
    }
  }
</style>
