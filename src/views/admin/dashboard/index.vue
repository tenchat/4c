<template>
  <div class="page-admin-dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>系统管理后台</h2>
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
          title="企业总数"
          :count="stats.totalCompanies"
          :description="stats.totalCompanies + ' 家'"
          icon="ri:building-line"
          iconStyle="bg-green-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="在招岗位"
          :count="stats.totalJobs"
          :description="stats.totalJobs + ' 个'"
          icon="ri:briefcase-line"
          iconStyle="bg-orange-500"
        />
      </el-col>
      <el-col :span="6">
        <ArtStatsCard
          title="整体就业率"
          :count="stats.overallRate"
          :description="stats.overallRate + '%'"
          icon="ri:trend-charts-line"
          iconStyle="bg-red-500"
        />
      </el-col>
    </el-row>

    <!-- 企业招聘统计区块 -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="24">
        <div class="section-title">本年度企业招聘活动</div>
      </el-col>
      <el-col
        :xs="12"
        :sm="8"
        :md="6"
        :lg="4"
        v-for="item in enterpriseStatsConfig"
        :key="item.key"
      >
        <ArtStatsCard
          :title="item.label"
          :count="statsEnterprise[item.key] ?? 0"
          :icon="item.icon"
          :icon-style="item.iconStyle"
          :description="String(statsEnterprise.year ?? new Date().getFullYear())"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <art-card-banner title="平台数据概览" description="各高校就业率统计">
          <el-table :data="universityStats" style="width: 100%">
            <el-table-column prop="name" label="学校名称" minWidth="150" />
            <el-table-column prop="province" label="省份" width="100" />
            <el-table-column prop="total_students" label="学生数" width="100" />
            <el-table-column prop="employed" label="已就业" width="100" />
            <el-table-column prop="employment_rate" label="就业率" width="120">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.employment_rate"
                  :color="
                    row.employment_rate >= 80
                      ? '#67c23a'
                      : row.employment_rate >= 60
                        ? '#e6a23c'
                        : '#f56c6c'
                  "
                />
              </template>
            </el-table-column>
          </el-table>
        </art-card-banner>
      </el-col>
      <el-col :span="12">
        <art-card-banner title="企业审核" description="审核注册企业账号">
          <el-table :data="pendingCompanies" style="width: 100%">
            <el-table-column prop="company_name" label="企业名称" />
            <el-table-column prop="industry" label="行业" />
            <el-table-column prop="created_at" label="申请时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" type="success" @click="handleApprove(row.company_id)">
                  通过
                </el-button>
                <el-button size="small" type="danger" @click="handleReject(row.company_id)">
                  拒绝
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <template #footer>
            <el-button link type="primary" @click="$router.push('/admin/companies')">
              查看全部
            </el-button>
          </template>
        </art-card-banner>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="24">
        <art-card-banner title="稀缺人才数据" description="各地区紧缺人才分析">
          <el-table :data="scarceTalents" style="width: 100%">
            <el-table-column prop="province" label="省份" width="120" />
            <el-table-column prop="job_type" label="岗位类型" />
            <el-table-column prop="industry" label="行业" width="120" />
            <el-table-column prop="shortage_level" label="紧缺程度" width="120">
              <template #default="{ row }">
                <el-tag
                  :type="
                    row.shortage_level === 3
                      ? 'danger'
                      : row.shortage_level === 2
                        ? 'warning'
                        : 'info'
                  "
                >
                  {{
                    row.shortage_level === 3 ? '严重' : row.shortage_level === 2 ? '中等' : '轻微'
                  }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="data_year" label="数据年份" width="120" />
          </el-table>
        </art-card-banner>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import {
    fetchAdminDashboard,
    fetchScarceTalents,
    fetchPendingCompanies,
    fetchAdminDataboard,
    verifyCompany
  } from '@/api/admin'
  import { getEnterpriseStats } from '@/api/stats'
  import { onMounted, ref } from 'vue'
  import { ElMessage } from 'element-plus'

  defineOptions({ name: 'AdminDashboard' })

  interface Stats {
    totalStudents: number
    totalCompanies: number
    totalJobs: number
    overallRate: number
  }

  const stats = ref<Stats>({
    totalStudents: 0,
    totalCompanies: 0,
    totalJobs: 0,
    overallRate: 0
  })

  interface UniversityStat {
    name: string
    province: string
    total_students: number
    employed: number
    employment_rate: number
  }

  interface Company {
    company_id: string
    company_name: string
    industry: string
    created_at: string
  }

  interface ScarceTalent {
    province: string
    job_type: string
    industry: string
    shortage_level: number
    data_year: number
  }

  const universityStats = ref<UniversityStat[]>([])
  const pendingCompanies = ref<Company[]>([])
  const scarceTalents = ref<ScarceTalent[]>([])
  const statsEnterprise = ref<Record<string, number>>({})

  const enterpriseStatsConfig = [
    {
      key: 'total_companies',
      label: '总单位数',
      icon: 'ri:building-line',
      iconStyle: 'bg-blue-100 text-blue-600'
    },
    {
      key: 'new_companies_this_year',
      label: '本年度单位数',
      icon: 'ri:building-4-line',
      iconStyle: 'bg-teal-100 text-teal-600'
    },
    {
      key: 'job_demand_this_year',
      label: '本年度岗位需求',
      icon: 'ri:briefcase-line',
      iconStyle: 'bg-purple-100 text-purple-600'
    },
    {
      key: 'seminars_this_year',
      label: '本年度宣讲会',
      icon: 'ri:presentation-line',
      iconStyle: 'bg-amber-100 text-amber-600'
    },
    {
      key: 'job_fairs_this_year',
      label: '本年度招聘会',
      icon: 'ri:team-line',
      iconStyle: 'bg-rose-100 text-rose-600'
    },
    {
      key: 'announcements_this_year',
      label: '本年度招聘公告',
      icon: 'ri:megaphone-line',
      iconStyle: 'bg-green-100 text-green-600'
    },
    {
      key: 'positions_this_year',
      label: '本年度职位数',
      icon: 'ri:file-list-3-line',
      iconStyle: 'bg-pink-100 text-pink-600'
    }
  ]

  const loadDashboard = async () => {
    try {
      const res: any = await fetchAdminDashboard()
      if (res) {
        stats.value = {
          totalStudents: res.total_students || 0,
          totalCompanies: res.total_companies || 0,
          totalJobs: res.total_jobs || 0,
          overallRate: res.overall_employment_rate || 0
        }
      }
    } catch (error) {
      console.error('获取管理首页数据失败:', error)
    }
  }

  const loadDataboard = async () => {
    try {
      const res: any = await fetchAdminDataboard()
      if (res) {
        universityStats.value = res.university_stats || []
      }
    } catch (error) {
      console.error('获取数据大屏数据失败:', error)
    }
  }

  const loadPendingCompanies = async () => {
    const t0 = performance.now()
    console.log('[Dashboard] loadPendingCompanies 开始')
    try {
      const res: any = await fetchPendingCompanies()
      const t1 = performance.now()
      console.log(`[Dashboard] loadPendingCompanies API完成，耗时: ${t1 - t0}ms`)
      console.log('[Dashboard] loadPendingCompanies 响应:', res)
      if (res && Array.isArray(res)) {
        pendingCompanies.value = res.slice(0, 5)
      }
      console.log(`[Dashboard] loadPendingCompanies 总耗时: ${performance.now() - t0}ms`)
    } catch (error) {
      console.error('[Dashboard] 获取待审核企业失败:', error)
    }
  }

  const loadScarceTalents = async () => {
    try {
      const res: any = await fetchScarceTalents()
      if (res) {
        scarceTalents.value = (res.list || []).slice(0, 10)
      }
    } catch (error) {
      console.error('获取稀缺人才数据失败:', error)
    }
  }

  const loadEnterpriseStats = async () => {
    try {
      const data = await getEnterpriseStats()
      statsEnterprise.value = data as Record<string, number>
    } catch (e) {
      console.error('Failed to load enterprise stats:', e)
    }
  }

  const handleApprove = async (id: string) => {
    if (!id) {
      ElMessage.error('企业ID不存在，请刷新页面后重试')
      return
    }
    try {
      const res: any = await verifyCompany(id, 'approve')
      if (res) {
        ElMessage.success('已通过审核')
        pendingCompanies.value = pendingCompanies.value.filter((c) => c.company_id !== id)
      }
    } catch {
      ElMessage.error('操作失败')
    }
  }

  const handleReject = async (id: string) => {
    if (!id) {
      ElMessage.error('企业ID不存在，请刷新页面后重试')
      return
    }
    try {
      const res: any = await verifyCompany(id, 'reject')
      if (res) {
        ElMessage.success('已拒绝')
        pendingCompanies.value = pendingCompanies.value.filter((c) => c.company_id !== id)
      }
    } catch {
      ElMessage.error('操作失败')
    }
  }

  onMounted(async () => {
    const t0 = performance.now()
    console.log('[Dashboard] onMounted 开始加载')
    await Promise.all([
      loadDashboard(),
      loadDataboard(),
      loadPendingCompanies(),
      loadScarceTalents(),
      loadEnterpriseStats()
    ])
    console.log(`[Dashboard] onMounted 全部加载完成，耗时: ${performance.now() - t0}ms`)
  })
</script>

<style scoped>
  .page-admin-dashboard {
    padding: 20px;
  }
</style>
