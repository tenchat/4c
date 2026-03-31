<template>
  <div class="page-student-dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>学生中心</h2>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="6">
        <ArtStatsCard
          title="档案完整度"
          :count="profileComplete"
          :description="profileComplete + '%'"
          icon="ri:checkbox-circle-line"
          iconStyle="bg-green-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="就业状态"
          :count="1"
          :description="employmentStatusText"
          icon="ri:user-line"
          iconStyle="bg-blue-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="已投递简历"
          :count="appliedCount"
          :description="appliedCount + ' 份'"
          icon="ri:file-list-3-line"
          iconStyle="bg-orange-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="收到面试邀请"
          :count="interviewCount"
          :description="interviewCount + ' 个'"
          icon="ri:message-3-line"
          iconStyle="bg-red-500"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <art-card-banner title="AI 就业竞争力分析" description="通过AI分析您的就业竞争力">
          <div class="ai-profile-placeholder">
            <el-icon :size="48"><TrendCharts /></el-icon>
            <p>AI 就业竞争力分析</p>
            <el-button type="primary" @click="$router.push('/student/ai-profile')">
              开始分析
            </el-button>
          </div>
        </art-card-banner>
      </el-col>
      <el-col :span="12">
        <art-card-banner title="推荐岗位" description="根据您的简历推荐最匹配的岗位">
          <div class="job-list">
            <el-empty v-if="recommendedJobs.length === 0" description="暂无推荐" />
            <div v-else v-for="job in recommendedJobs" :key="job.job_id" class="job-item">
              <div class="job-info">
                <span class="job-title">{{ job.title }}</span>
                <span class="job-city">{{ job.city }}</span>
              </div>
              <div class="job-salary">
                {{ job.min_salary }}-{{ job.max_salary }}元/月
              </div>
            </div>
          </div>
          <template #footer>
            <el-button link type="primary" @click="$router.push('/student/jobs')">
              查看更多岗位
            </el-button>
          </template>
        </art-card-banner>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="24">
        <art-card-banner title="求职进度" description="跟踪您的求职申请状态">
          <el-timeline v-if="timelineItems.length > 0">
            <el-timeline-item
              v-for="(item, index) in timelineItems"
              :key="index"
              :timestamp="item.timestamp"
              placement="top"
              :type="item.type"
            >
              {{ item.content }}
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无求职记录" />
        </art-card-banner>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { fetchStudentDashboard, fetchStudentJobs } from '@/api/student'
  import { TrendCharts } from '@element-plus/icons-vue'
  import { onMounted, ref } from 'vue'

  defineOptions({ name: 'StudentDashboard' })

  const profileComplete = ref(0)
  const employmentStatus = ref(0)
  const appliedCount = ref(0)
  const interviewCount = ref(0)
  const recommendedJobs = ref<any[]>([])
  const timelineItems = ref<any[]>([])

  const employmentStatusText = computed(() => {
    const map: Record<number, string> = {
      0: '待就业',
      1: '已就业',
      2: '升学',
      3: '出国'
    }
    return map[employmentStatus.value] || '待就业'
  })

  const loadDashboardData = async () => {
    try {
      const res: any = await fetchStudentDashboard()
      if (res) {
        profileComplete.value = res.profile_complete || 0
        employmentStatus.value = res.employment_status || 0
        recommendedJobs.value = res.recommended_jobs || []
      }
    } catch (error) {
      console.error('获取学生首页数据失败:', error)
    }
  }

  const loadRecommendedJobs = async () => {
    try {
      const res: any = await fetchStudentJobs({ page: 1, page_size: 5 })
      if (res) {
        recommendedJobs.value = res.list || []
      }
    } catch (error) {
      console.error('获取推荐岗位失败:', error)
    }
  }

  onMounted(async () => {
    await Promise.all([loadDashboardData(), loadRecommendedJobs()])
  })
</script>

<style scoped>
  .page-student-dashboard {
    padding: 20px;
  }

  .ai-profile-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    color: #909399;
  }

  .ai-profile-placeholder p {
    margin: 16px 0;
    font-size: 16px;
  }

  .job-list {
    min-height: 100px;
  }

  .job-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;
  }

  .job-item:last-child {
    border-bottom: none;
  }

  .job-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .job-title {
    font-weight: 500;
    color: #303133;
  }

  .job-city {
    font-size: 12px;
    color: #909399;
  }

  .job-salary {
    color: #f56c6c;
    font-weight: 500;
  }
</style>
