<template>
  <div class="student-dashboard">
    <!-- 顶部欢迎栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">欢迎回来，{{ realName || '同学' }}</h1>
        <span class="page-subtitle">{{ universityName }} · {{ college }} · {{ major }}</span>
      </div>
      <div class="header-right">
        <el-button @click="$router.push('/student/profile')">
          <el-icon><Edit /></el-icon>
          编辑档案
        </el-button>
      </div>
    </div>

    <!-- 状态卡片区 -->
    <div class="stat-row">
      <ArtStatsCard
        icon="ri:checkbox-circle-line"
        iconStyle="bg-blue-500"
        :count="profileComplete"
        description="档案完整度"
        suffix="%"
      />
      <ArtStatsCard
        icon="ri:user-line"
        iconStyle="bg-green-500"
        :title="employmentStatusText"
      />
      <ArtStatsCard
        icon="ri:file-list-3-line"
        iconStyle="bg-orange-500"
        :count="appliedCount"
        description="已投递简历"
      />
      <ArtStatsCard
        icon="ri:message-3-line"
        iconStyle="bg-purple-500"
        :count="interviewCount"
        description="收到面试"
      />
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧栏 -->
      <div class="left-column">
        <!-- 求职意向卡片 -->
        <div class="card">
          <div class="card-header">
            <span>求职意向</span>
            <el-button link type="primary" @click="$router.push('/student/profile')">编辑</el-button>
          </div>
          <div class="card-body">
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">期望城市</span>
                <span class="info-value">{{ profile?.desire_city || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">期望行业</span>
                <span class="info-value">{{ profile?.desire_industry || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">期望薪资</span>
                <span class="info-value">
                  {{ profile?.desire_salary_min ? `${profile.desire_salary_min}-${profile.desire_salary_max}元/月` : '未填写' }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">学历层次</span>
                <span class="info-value">{{ degreeText }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 技能特长 -->
        <div class="card">
          <div class="card-header">
            <span>技能特长</span>
          </div>
          <div class="card-body">
            <div v-if="profile?.skills?.length" class="skill-tags">
              <el-tag v-for="skill in profile.skills" :key="skill" type="info">{{ skill }}</el-tag>
            </div>
            <el-empty v-else description="暂未填写" :image-size="50" />
          </div>
        </div>

        <!-- 实习经历 -->
        <div class="card">
          <div class="card-header">
            <span>实习经历</span>
          </div>
          <div class="card-body">
            <div v-if="profile?.internship" class="internship-info">
              <el-icon color="#409eff"><Briefcase /></el-icon>
              <span>{{ profile.internship }}</span>
            </div>
            <el-empty v-else description="暂未填写" :image-size="50" />
          </div>
        </div>

        <!-- AI工具 -->
        <div class="card">
          <div class="card-header">
            <span>AI助手</span>
          </div>
          <div class="card-body">
            <div class="ai-tools">
              <div class="ai-tool" @click="$router.push('/student/ai-profile')">
                <el-icon><DataAnalysis /></el-icon>
                <span>就业画像</span>
              </div>
              <div class="ai-tool" @click="$router.push('/student/ai-resume')">
                <el-icon><Document /></el-icon>
                <span>简历优化</span>
              </div>
              <div class="ai-tool" @click="$router.push('/student/interview-prep')">
                <el-icon><ChatDotRound /></el-icon>
                <span>面试助手</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间栏 -->
      <div class="center-column">
        <!-- 推荐岗位 -->
        <div class="card">
          <div class="card-header">
            <span>为你推荐</span>
            <el-button link type="primary" @click="$router.push('/student/jobs')">查看更多</el-button>
          </div>
          <div class="card-body">
            <div v-if="recommendedJobs.length" class="job-list">
              <div v-for="job in recommendedJobs" :key="job.job_id" class="job-item">
                <div class="job-info">
                  <span class="job-title">{{ job.title }}</span>
                  <span class="job-company">{{ job.company_name || '未知公司' }}</span>
                </div>
                <div class="job-meta">
                  <span class="job-city"><el-icon><Location /></el-icon>{{ job.city }}</span>
                  <span class="job-salary">{{ job.min_salary }}-{{ job.max_salary }}元/月</span>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无推荐岗位" :image-size="60" />
          </div>
        </div>

        <!-- 数据大屏入口 -->
        <div class="card databoard-card" @click="$router.push('/student/databoard')">
          <div class="databoard-content">
            <div class="databoard-icon">
              <el-icon :size="32"><DataLine /></el-icon>
            </div>
            <div class="databoard-text">
              <span class="databoard-title">就业数据大屏</span>
              <span class="databoard-desc">查看全校就业数据分析</span>
            </div>
            <el-icon class="databoard-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 右侧栏 -->
      <div class="right-column">
        <!-- 投递统计 -->
        <div class="card">
          <div class="card-header">
            <span>投递记录</span>
            <el-button link type="primary" @click="$router.push('/student/jobs')">全部</el-button>
          </div>
          <div class="card-body">
            <div v-if="applicationStats.total > 0" class="app-stats">
              <div class="app-stat">
                <span class="stat-num">{{ applicationStats.total }}</span>
                <span class="stat-label">已投递</span>
              </div>
              <div class="app-stat">
                <span class="stat-num">{{ applicationStats.viewed }}</span>
                <span class="stat-label">已查看</span>
              </div>
              <div class="app-stat">
                <span class="stat-num">{{ applicationStats.interested }}</span>
                <span class="stat-label">感兴趣</span>
              </div>
            </div>
            <el-empty v-else description="暂无投递记录" :image-size="50" />
          </div>
        </div>

        <!-- 当前信息 -->
        <div class="card">
          <div class="card-header">
            <span>当前信息</span>
          </div>
          <div class="card-body">
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">当前公司</span>
                <span class="info-value">{{ profile?.cur_company || '未就业' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">当前城市</span>
                <span class="info-value">{{ profile?.cur_city || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">当前行业</span>
                <span class="info-value">{{ profile?.cur_industry || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">当前薪资</span>
                <span class="info-value">{{ profile?.cur_salary ? `${profile.cur_salary}元/月` : '未填写' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 个人基本信息 -->
        <div class="card">
          <div class="card-header">
            <span>基本信息</span>
          </div>
          <div class="card-body">
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">学号</span>
                <span class="info-value">{{ profile?.student_no || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">毕业年份</span>
                <span class="info-value">{{ profile?.graduation_year || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">生源省份</span>
                <span class="info-value">{{ profile?.province_origin || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">GPA</span>
                <span class="info-value">{{ profile?.gpa || '未填写' }}</span>
              </div>
            </div>
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
    Edit, Briefcase, DataAnalysis, Document, ChatDotRound,
    Location, DataLine, ArrowRight
  } from '@element-plus/icons-vue'
  import { fetchStudentProfile, fetchStudentJobs, fetchJobStatistics } from '@/api/student'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'

  defineOptions({ name: 'StudentDashboard' })

  const router = useRouter()
  const realName = ref('')
  const universityName = ref('')
  const profile = ref<any>(null)
  const profileComplete = ref(0)
  const employmentStatus = ref(0)
  const appliedCount = ref(0)
  const interviewCount = ref(0)
  const recommendedJobs = ref<any[]>([])
  const applicationStats = ref({ total: 0, viewed: 0, interested: 0 })

  const employmentStatusText = computed(() => {
    const map: Record<number, string> = { 0: '待就业', 1: '已就业', 2: '升学', 3: '出国' }
    return map[employmentStatus.value] || '待就业'
  })

  const degreeText = computed(() => {
    const map: Record<number, string> = { 1: '本科', 2: '硕士', 3: '博士', 4: '大专', 5: '其他' }
    return map[profile.value?.degree] || '本科'
  })

  const loadProfile = async () => {
    try {
      const res: any = await fetchStudentProfile()
      if (res) {
        profile.value = res
        realName.value = res.real_name || ''
        universityName.value = '某某大学'
        profileComplete.value = res.profile_complete || 0
        employmentStatus.value = res.employment_status || 0
      }
    } catch (error) {
      console.error('获取档案失败:', error)
    }
  }

  const loadJobs = async () => {
    try {
      const res: any = await fetchStudentJobs({ page: 1, page_size: 6 })
      if (res?.list) {
        recommendedJobs.value = res.list
      }
    } catch (error) {
      console.error('获取岗位失败:', error)
    }
  }

  const loadStats = async () => {
    try {
      const res: any = await fetchJobStatistics()
      if (res) {
        appliedCount.value = res.applied_count || 0
        interviewCount.value = Math.floor((res.applied_count || 0) * 0.15)
        applicationStats.value.total = res.applied_count || 0
        applicationStats.value.viewed = Math.floor((res.applied_count || 0) * 0.6)
        applicationStats.value.interested = Math.floor((res.applied_count || 0) * 0.2)
      }
    } catch (error) {
      console.error('获取统计失败:', error)
    }
  }

  onMounted(async () => {
    await Promise.all([loadProfile(), loadJobs(), loadStats()])
  })
</script>

<style lang="scss" scoped>
  .student-dashboard {
    min-height: 100vh;
    background: #f0f2f5;
    padding-bottom: 24px;
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
      align-items: baseline;
      gap: 10px;

      .page-title {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
      }

      .page-subtitle {
        font-size: 13px;
        color: #8c8c8c;
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;
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

  .left-column, .center-column, .right-column {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  // 卡片样式
  .card {
    background: #fff;
    border-radius: 10px;
    border: 1px solid #eee;
    overflow: hidden;

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 16px;
      border-bottom: 1px solid #f0f0f0;
      font-size: 14px;
      font-weight: 500;
      color: #1a1a1a;
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
    justify-content: space-between;
    align-items: center;

    .info-label {
      font-size: 13px;
      color: #8c8c8c;
    }

    .info-value {
      font-size: 13px;
      color: #1a1a1a;
      font-weight: 500;
    }
  }

  // 技能标签
  .skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    :deep(.el-tag) {
      border-radius: 4px;
      background: #f5f7fa;
      border: none;
      color: #606266;
    }
  }

  // 实习信息
  .internship-info {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    color: #606266;
    font-size: 13px;
    line-height: 1.5;

    .el-icon {
      margin-top: 2px;
      color: #409eff;
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
      align-items: center;
      gap: 6px;
      padding: 14px 8px;
      background: #f5f7fa;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.2s;
      color: #606266;

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
    border: 1px solid #f0f0f0;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: #409eff;
      background: #fafafa;
    }

    .job-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 6px;

      .job-title {
        font-size: 14px;
        font-weight: 500;
        color: #1a1a1a;
      }

      .job-company {
        font-size: 12px;
        color: #8c8c8c;
      }
    }

    .job-meta {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #606266;

      .job-city {
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .job-salary {
        color: #f56c6c;
        font-weight: 500;
      }
    }
  }

  // 数据大屏入口
  .databoard-card {
    border: none;
    background: linear-gradient(135deg, #e8f4f8 0%, #dbeafe 100%);
    cursor: pointer;
    transition: transform 0.2s;

    &:hover {
      transform: scale(1.01);
    }
  }

  .databoard-content {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 4px;

    .databoard-icon {
      width: 48px;
      height: 48px;
      background: #fff;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #409eff;
    }

    .databoard-text {
      flex: 1;
      display: flex;
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

  // 投递统计
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

  // 空状态
  :deep(.el-empty) {
    padding: 12px 0;

    .el-empty__description {
      margin-top: 8px;
      font-size: 12px;
    }
  }

  // 响应式
  @media (max-width: 1200px) {
    .main-content {
      grid-template-columns: 1fr 1fr;
    }
    .right-column {
      grid-column: span 2;
    }
  }

  @media (max-width: 768px) {
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
      padding: 12px 16px;
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
  }
</style>
