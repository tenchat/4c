<template>
  <div class="page-school-dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>学校管理中心</h2>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="6">
        <ArtStatsCard
          title="学生总数"
          :count="stats.totalStudents"
          :description="stats.totalStudents + ' 人'"
          icon="ri:user-line"
          iconStyle="bg-blue-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="就业率"
          :count="stats.employmentRate"
          :description="stats.employmentRate + '%'"
          icon="ri:trend-charts-line"
          iconStyle="bg-green-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="待就业人数"
          :count="stats.unemployed"
          :description="stats.unemployed + ' 人'"
          icon="ri:warning-line"
          iconStyle="bg-orange-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="升学人数"
          :count="stats.furtherStudy"
          :description="stats.furtherStudy + ' 人'"
          icon="ri:school-line"
          iconStyle="bg-gray-500"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <art-card-banner title="学院就业率排名" description="查看各学院学生就业情况">
          <el-table :data="collegeRankings" style="width: 100%">
            <el-table-column prop="college_name" label="学院" />
            <el-table-column prop="employment_rate" label="就业率" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.employment_rate" />
              </template>
            </el-table-column>
            <el-table-column prop="employed_nums" label="已就业" width="100" />
            <el-table-column prop="graduate_nums" label="毕业生总数" width="100" />
          </el-table>
        </art-card-banner>
      </el-col>
      <el-col :span="12">
        <art-card-banner title="就业预警" description="关注需要帮助的学生">
          <el-empty v-if="warnings.length === 0" description="暂无预警" />
          <el-table v-else :data="warnings" style="width: 100%">
            <el-table-column prop="account_id" label="学生账号" />
            <el-table-column prop="warning_type" label="预警类型" width="120">
              <template #default="{ row }">
                {{ getWarningTypeText(row.warning_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="level" label="级别" width="80">
              <template #default="{ row }">
                <el-tag :type="row.level === 1 ? 'danger' : row.level === 2 ? 'warning' : 'info'">
                  {{ row.level === 1 ? '红' : row.level === 2 ? '黄' : '绿' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <template #footer>
            <el-button link type="primary" @click="$router.push('/school/warnings')">
              查看全部预警
            </el-button>
          </template>
        </art-card-banner>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { fetchSchoolDashboard } from '@/api/school'
  import { onMounted, ref } from 'vue'

  defineOptions({ name: 'SchoolDashboard' })

  interface Stats {
    totalStudents: number
    employmentRate: number
    unemployed: number
    furtherStudy: number
  }

  const stats = ref<Stats>({
    totalStudents: 0,
    employmentRate: 0,
    unemployed: 0,
    furtherStudy: 0
  })

  interface CollegeRanking {
    college_name: string
    employment_rate: number
    employed_nums: number
    graduate_nums: number
  }

  interface Warning {
    warning_id: string
    account_id: string
    warning_type: string
    level: number
    handled: boolean
  }

  const collegeRankings = ref<CollegeRanking[]>([])
  const warnings = ref<Warning[]>([])

  const WARNING_TYPE_MAP: Record<string, string> = {
    employment: '就业困难',
    low_salary: '薪资偏低',
    unemployed: '长期未就业',
    gap_year: 'Gap Year',
    other: '其他'
  }

  const getWarningTypeText = (type: string): string => {
    return WARNING_TYPE_MAP[type] || type || '未知'
  }

  onMounted(async () => {
    try {
      const res: any = await fetchSchoolDashboard()
      if (res) {
        stats.value = {
          totalStudents: res.total_students || 0,
          employmentRate: res.employment_rate || 0,
          unemployed: res.unemployed_nums || 0,
          furtherStudy: res.further_study_nums || 0
        }
        collegeRankings.value = res.college_rankings || []
        warnings.value = res.warnings || []
      }
    } catch (error) {
      console.error('获取学校首页数据失败:', error)
    }
  })
</script>

<style scoped>
  .page-school-dashboard {
    padding: 20px;
  }
</style>
