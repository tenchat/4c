<!-- 简历管理页面 -->
<template>
  <div class="page-company-resumes">
    <!-- 统计卡片 -->
    <ElRow :gutter="20" class="stats-row mb-4">
      <ElCol :xs="12" :sm="6">
        <div
          class="stat-card"
          :class="{ active: filterStatus === 0 }"
          @click="handleFilterStatus(0)"
        >
          <div class="stat-icon bg-primary-light">
            <ElIcon><Document /></ElIcon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">投递总数</span>
          </div>
        </div>
      </ElCol>
      <ElCol :xs="12" :sm="6">
        <div
          class="stat-card"
          :class="{ active: filterStatus === 1 }"
          @click="handleFilterStatus(1)"
        >
          <div class="stat-icon bg-warning-light">
            <ElIcon><Filter /></ElIcon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.screening }}</span>
            <span class="stat-label">简历筛选</span>
          </div>
        </div>
      </ElCol>
      <ElCol :xs="12" :sm="6">
        <div
          class="stat-card"
          :class="{ active: filterStatus === 2 }"
          @click="handleFilterStatus(2)"
        >
          <div class="stat-icon bg-success-light">
            <ElIcon><ChatDotRound /></ElIcon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.interview }}</span>
            <span class="stat-label">面试中</span>
          </div>
        </div>
      </ElCol>
      <ElCol :xs="12" :sm="6">
        <div
          class="stat-card"
          :class="{ active: filterStatus === 4 }"
          @click="handleFilterStatus(4)"
        >
          <div class="stat-icon bg-danger-light">
            <ElIcon><CircleClose /></ElIcon>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.rejected }}</span>
            <span class="stat-label">已拒绝</span>
          </div>
        </div>
      </ElCol>
    </ElRow>

    <!-- 简历列表 -->
    <ElCard class="art-card-xs">
      <div v-loading="loading">
        <ElEmpty v-if="!loading && data.length === 0" description="暂无简历投递" />

        <div v-else class="resume-list">
          <div v-for="item in data" :key="item.application_id" class="resume-item">
            <!-- 左侧：学生信息 -->
            <div class="resume-left">
              <div class="student-avatar">
                {{ (item.student_name || '学').charAt(0) }}
              </div>
              <div class="student-info">
                <h3 class="student-name">{{ item.student_name || '未知姓名' }}</h3>
                <p class="student-meta"> {{ item.college || '' }} · {{ item.major || '' }} </p>
                <p class="student-meta">
                  <ElTag size="small" type="info">{{ degreeText(item.degree) }}</ElTag>
                  <ElTag size="small" v-if="item.graduation_year" class="ml-2">
                    {{ item.graduation_year }}届
                  </ElTag>
                  <ElTag size="small" v-if="item.student_no" class="ml-2">
                    学号: {{ item.student_no }}
                  </ElTag>
                </p>
              </div>
            </div>

            <!-- 中间：岗位信息 -->
            <div class="resume-middle">
              <h4 class="job-title">{{ item.job_title }}</h4>
              <p class="apply-time">
                <ElIcon><Clock /></ElIcon>
                {{ formatDate(item.applied_at) }}
              </p>
            </div>

            <!-- 右侧：状态和操作 -->
            <div class="resume-right">
              <ElTag :type="getStatusType(item.status)" class="status-tag">
                {{ getStatusText(item.status) }}
              </ElTag>
              <div class="action-buttons">
                <ElButton type="info" size="small" @click="handleView(item)">查看学生</ElButton>
              </div>
              <div class="action-buttons" v-if="item.status === 0 || item.status === 1">
                <ElButton
                  v-if="item.status === 0"
                  type="primary"
                  size="small"
                  @click="handleUpdateStatus(item, 1)"
                >
                  进入筛选
                </ElButton>
                <ElButton
                  v-if="item.status === 1"
                  type="success"
                  size="small"
                  @click="handleUpdateStatus(item, 2)"
                >
                  安排面试
                </ElButton>
                <ElButton type="danger" size="small" @click="handleUpdateStatus(item, 4)">
                  不合适
                </ElButton>
              </div>
              <div class="action-buttons" v-if="item.status === 2">
                <ElButton type="success" size="small" @click="handleUpdateStatus(item, 3)">
                  录用
                </ElButton>
                <ElButton type="danger" size="small" @click="handleUpdateStatus(item, 4)">
                  拒绝
                </ElButton>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="pagination.total > 0">
          <ElPagination
            v-model:current-page="pagination.current"
            v-model:page-size="pagination.size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </ElCard>

    <!-- 学生详情弹窗 -->
    <ElDialog v-model="showDetailDialog" title="学生档案详情" width="700px">
      <div v-if="studentDetail" class="detail-grid">
        <div class="detail-section">
          <div class="detail-title">基本信息</div>
          <div class="detail-row">
            <span class="detail-label">学号</span>
            <span class="detail-value">{{ studentDetail.student_no || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">姓名</span>
            <span class="detail-value">{{ studentDetail.account?.real_name || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">学院</span>
            <span class="detail-value">{{ studentDetail.college || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">专业</span>
            <span class="detail-value">{{ studentDetail.major || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">学历</span>
            <span class="detail-value">{{ degreeText(studentDetail.degree) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">毕业年份</span>
            <span class="detail-value">{{ studentDetail.graduation_year || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">生源省份</span>
            <span class="detail-value">{{ studentDetail.province_origin || '-' }}</span>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-title">账户信息</div>
          <div v-if="studentDetail.account">
            <div class="detail-row">
              <span class="detail-label">用户名</span>
              <span class="detail-value">{{ studentDetail.account.username }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">邮箱</span>
              <span class="detail-value">{{ studentDetail.account.email || '-' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">手机</span>
              <span class="detail-value">{{ studentDetail.account.phone || '-' }}</span>
            </div>
          </div>
          <div v-else class="text-gray-400 text-sm">未注册，无账户信息</div>
        </div>

        <div class="detail-section">
          <div class="detail-title">就业信息</div>
          <div class="detail-row">
            <span class="detail-label">当前公司</span>
            <span class="detail-value">{{ studentDetail.cur_company || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">当前城市</span>
            <span class="detail-value">{{ studentDetail.cur_city || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">当前行业</span>
            <span class="detail-value">{{ studentDetail.cur_industry || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">当前薪资</span>
            <span class="detail-value">
              {{ studentDetail.cur_salary ? `${studentDetail.cur_salary}元/月` : '-' }}
            </span>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-title">求职意向</div>
          <div class="detail-row">
            <span class="detail-label">期望城市</span>
            <span class="detail-value">{{ studentDetail.desire_city || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">期望行业</span>
            <span class="detail-value">{{ studentDetail.desire_industry || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">期望薪资</span>
            <span class="detail-value">
              {{
                studentDetail.desire_salary_min || studentDetail.desire_salary_max
                  ? `${studentDetail.desire_salary_min || '-'} ~ ${studentDetail.desire_salary_max || '-'} 元/月`
                  : '-'
              }}
            </span>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-title">其他信息</div>
          <div class="detail-row">
            <span class="detail-label">GPA</span>
            <span class="detail-value">{{ studentDetail.gpa || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">技能特长</span>
            <span class="detail-value">
              <template v-if="studentDetail.skills && studentDetail.skills.length">
                <ElTag v-for="s in studentDetail.skills" :key="s" size="small" class="mr-1">{{
                  s
                }}</ElTag>
              </template>
              <span v-else>-</span>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">实习经历</span>
            <span class="detail-value">{{ studentDetail.internship || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">简历</span>
            <span class="detail-value">
              <a
                v-if="studentDetail.resume_url"
                :href="studentDetail.resume_url"
                target="_blank"
                class="text-primary"
              >
                查看简历
              </a>
              <span v-else>-</span>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">档案完整度</span>
            <span class="detail-value">{{ studentDetail.profile_complete }}%</span>
          </div>
        </div>
      </div>

      <div v-else-if="detailLoading" class="text-center py-8 text-gray-400">加载中...</div>
      <div v-else class="text-center py-8 text-gray-400">未找到该学生档案</div>

      <template #footer>
        <ElButton @click="showDetailDialog = false">关闭</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<script setup lang="ts">
  import { fetchCompanyResumes, updateResumeStatus, fetchStudentByAccount } from '@/api/company'
  import { ElMessage, ElMessageBox, ElTag } from 'element-plus'
  import { Document, Filter, ChatDotRound, CircleClose, Clock } from '@element-plus/icons-vue'

  defineOptions({ name: 'CompanyResumes' })

  interface ResumeItem {
    application_id: string
    job_id: string
    job_title: string
    account_id: string
    student_name: string
    student_no: string
    college: string
    major: string
    degree: number
    graduation_year: number
    status: number
    applied_at: string
  }

  const loading = ref(false)
  const data = ref<ResumeItem[]>([])
  const filterStatus = ref<number | undefined>(undefined)
  const showDetailDialog = ref(false)
  const studentDetail = ref<any>(null)
  const detailLoading = ref(false)

  const stats = reactive({
    total: 0,
    screening: 0,
    interview: 0,
    rejected: 0
  })

  const pagination = reactive({
    current: 1,
    size: 20,
    total: 0
  })

  // 学位映射
  const degreeText = (val?: number) => {
    const map: Record<number, string> = { 1: '本科', 2: '硕士', 3: '博士', 4: '大专' }
    return map[val || 1] || '学历不限'
  }

  // 状态映射
  const getStatusText = (status: number) => {
    const map: Record<number, string> = {
      0: '已投递',
      1: '简历筛选',
      2: '面试中',
      3: '已录用',
      4: '已拒绝'
    }
    return map[status] || '未知'
  }

  const getStatusType = (status: number): 'success' | 'warning' | 'info' | 'danger' | 'primary' => {
    const map: Record<number, 'success' | 'warning' | 'info' | 'danger' | 'primary'> = {
      0: 'info',
      1: 'warning',
      2: 'primary',
      3: 'success',
      4: 'danger'
    }
    return map[status] || 'info'
  }

  // 格式化日期
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  // 获取统计数据
  const fetchStats = async () => {
    try {
      const res: any = await fetchCompanyResumes()
      if (res?.list) {
        const all = res.list as ResumeItem[]
        stats.total = all.length
        stats.screening = all.filter((i) => i.status === 1).length
        stats.interview = all.filter((i) => i.status === 2).length
        stats.rejected = all.filter((i) => i.status === 4).length
      }
    } catch (error) {
      console.error('获取统计失败:', error)
    }
  }

  // 获取简历列表
  const fetchResumes = async () => {
    loading.value = true
    try {
      const res: any = await fetchCompanyResumes({
        status: filterStatus.value,
        page: pagination.current,
        page_size: pagination.size
      })
      if (res) {
        data.value = res.list || []
        pagination.total = res.total || 0
      }
    } catch (error) {
      console.error('获取简历列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 筛选状态
  const handleFilterStatus = (status: number) => {
    filterStatus.value = filterStatus.value === status ? undefined : status
    pagination.current = 1
    fetchResumes()
  }

  // 更新状态
  const handleUpdateStatus = async (item: ResumeItem, status: number) => {
    const statusTexts: Record<number, string> = {
      1: '进入简历筛选',
      2: '安排面试',
      3: '录用',
      4: '拒绝'
    }

    const confirmText = statusTexts[status]
    if (!confirmText) return

    try {
      await ElMessageBox.confirm(
        `确定要将 "${item.student_name}" 的简历状态更新为「${confirmText}」吗？`,
        '更新状态',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      const res: any = await updateResumeStatus(item.application_id, status)
      if (res.code === 200) {
        ElMessage.success(res.message || '更新成功')
        fetchResumes()
        fetchStats()
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('更新状态失败:', error)
      }
    }
  }

  const handleSizeChange = (size: number) => {
    pagination.size = size
    pagination.current = 1
    fetchResumes()
  }

  const handleCurrentChange = (current: number) => {
    pagination.current = current
    fetchResumes()
  }

  // 查看学生详情
  const handleView = async (item: ResumeItem) => {
    showDetailDialog.value = true
    detailLoading.value = true
    studentDetail.value = null
    try {
      const res: any = await fetchStudentByAccount(item.account_id)
      studentDetail.value = res
    } catch (e: any) {
      ElMessage.error(e.message || '获取学生详情失败')
    } finally {
      detailLoading.value = false
    }
  }

  onMounted(() => {
    fetchResumes()
    fetchStats()
  })
</script>

<style scoped>
  .page-company-resumes {
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
    gap: 14px;
    align-items: center;
    padding: 18px;
    cursor: pointer;
    background: var(--el-bg-color);
    border: 2px solid transparent;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgb(0 0 0 / 4%);
    transition: all 0.3s;
  }

  .stat-card:hover {
    box-shadow: 0 4px 16px rgb(0 0 0 / 8%);
    transform: translateY(-2px);
  }

  .stat-card.active {
    background: var(--el-color-primary-light-9);
    border-color: var(--el-color-primary-light-5);
  }

  .stat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    font-size: 22px;
    border-radius: 12px;
  }

  .bg-primary-light {
    color: var(--el-color-primary);
    background: rgb(64 158 255 / 12%);
  }

  .bg-warning-light {
    color: var(--el-color-warning);
    background: rgb(230 162 60 / 12%);
  }

  .bg-success-light {
    color: var(--el-color-success);
    background: rgb(103 194 58 / 12%);
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
    font-size: 24px;
    font-weight: 700;
    line-height: 1;
    color: var(--el-text-color-primary);
  }

  .stat-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  /* 简历列表 */
  .resume-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .resume-item {
    display: flex;
    align-items: center;
    padding: 20px;
    background: var(--el-fill-color-light);
    border-radius: 12px;
    transition: all 0.2s;
  }

  .resume-item:hover {
    background: var(--el-fill-color);
    box-shadow: 0 2px 12px rgb(0 0 0 / 4%);
  }

  /* 左侧学生信息 */
  .resume-left {
    display: flex;
    flex: 0 0 280px;
    gap: 16px;
    align-items: center;
  }

  .student-avatar {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    font-size: 20px;
    font-weight: 600;
    color: var(--el-color-primary);
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-5),
      var(--el-color-primary-light-8)
    );
    border-radius: 50%;
  }

  .student-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }

  .student-name {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .student-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    margin: 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  /* 中间岗位信息 */
  .resume-middle {
    flex: 1;
    padding: 0 20px;
  }

  .job-title {
    margin: 0 0 8px;
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .apply-time {
    display: flex;
    gap: 6px;
    align-items: center;
    margin: 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  /* 右侧状态和操作 */
  .resume-right {
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    gap: 12px;
    align-items: flex-end;
  }

  .status-tag {
    border-radius: 16px;
  }

  .action-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
  }

  /* 分页 */
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    padding: 20px 0 10px;
  }

  .ml-2 {
    margin-left: 8px;
  }

  @media (width <= 768px) {
    .resume-item {
      flex-direction: column;
      gap: 16px;
      align-items: flex-start;
    }

    .resume-left {
      flex: none;
      width: 100%;
    }

    .resume-middle {
      width: 100%;
      padding: 0;
    }

    .resume-right {
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      width: 100%;
    }
  }

  /* 学生详情弹窗样式 */
  .detail-grid {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .detail-section {
    border: 1px solid #ebeef5;
    border-radius: 8px;
    padding: 12px 16px;
  }

  .detail-title {
    font-weight: 600;
    font-size: 14px;
    color: #303133;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f0f0f0;
  }

  .detail-row {
    display: flex;
    align-items: flex-start;
    font-size: 13px;
    line-height: 28px;
  }

  .detail-label {
    color: #909399;
    min-width: 80px;
    flex-shrink: 0;
  }

  .detail-value {
    color: #303133;
    word-break: break-all;
  }
</style>
