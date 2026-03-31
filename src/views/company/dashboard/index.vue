<template>
  <div class="page-company-dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>企业管理中心</h2>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="6">
        <ArtStatsCard
          title="发布岗位"
          :count="stats.publishedJobs"
          :description="stats.publishedJobs + ' 个'"
          icon="ri:briefcase-line"
          iconStyle="bg-blue-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="收到简历"
          :count="stats.receivedResumes"
          :description="stats.receivedResumes + ' 份'"
          icon="ri:file-list-3-line"
          iconStyle="bg-green-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="已录用"
          :count="stats.hiredCount"
          :description="stats.hiredCount + ' 人'"
          icon="ri:user-follow-line"
          iconStyle="bg-orange-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="本月新增"
          :count="stats.newThisMonth"
          :description="stats.newThisMonth + ' 个'"
          icon="ri:add-circle-line"
          iconStyle="bg-red-500"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="24">
        <art-card-banner title="岗位管理" description="查看所有岗位状态">
          <el-table :data="jobStatusList" style="width: 100%">
            <el-table-column prop="title" label="岗位名称" minWidth="150" />
            <el-table-column prop="city" label="工作城市" width="100" />
            <el-table-column prop="min_salary" label="最低薪资" width="120">
              <template #default="{ row }">
                {{ row.min_salary || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="max_salary" label="最高薪资" width="120">
              <template #default="{ row }">
                {{ row.max_salary || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 1 ? 'success' : 'info'">
                  {{ row.status === 1 ? '招聘中' : row.status === 0 ? '已暂停' : '已结束' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="handleEditJob(row)">
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <template #footer>
            <el-button link type="primary" @click="$router.push('/company/jobs')">
              管理全部岗位
            </el-button>
          </template>
        </art-card-banner>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { fetchCompanyDashboard, fetchCompanyJobs } from '@/api/company'
  import { onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'

  defineOptions({ name: 'CompanyDashboard' })

  const router = useRouter()

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

  const jobStatusList = ref<Job[]>([])

  const loadDashboard = async () => {
    try {
      const res: any = await fetchCompanyDashboard()
      if (res) {
        stats.value = {
          publishedJobs: res.published_jobs || 0,
          receivedResumes: res.received_resumes || 0,
          hiredCount: res.hired_count || 0,
          newThisMonth: 0
        }
      }
    } catch (error) {
      console.error('获取企业首页数据失败:', error)
    }
  }

  const loadJobs = async () => {
    try {
      const res: any = await fetchCompanyJobs({ status: 1, page: 1, page_size: 5 })
      if (res) {
        jobStatusList.value = res.list || []
      }
    } catch (error) {
      console.error('获取岗位列表失败:', error)
    }
  }

  const handleEditJob = (row: Job) => {
    router.push(`/company/post-job?id=${row.job_id}`)
  }

  onMounted(async () => {
    await Promise.all([loadDashboard(), loadJobs()])
  })
</script>

<style scoped>
  .page-company-dashboard {
    padding: 20px;
  }
</style>
