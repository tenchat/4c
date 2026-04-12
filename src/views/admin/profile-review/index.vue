<!-- 信息审核管理页面（企业信息更新 + 管理员账号）-->
<template>
  <div class="page-admin-profile-review art-full-height">
    <ElCard class="art-card-xs">
      <div class="tab-bar flex items-center gap-4">
        <ElRadioGroup v-model="reviewType" @change="(val: any) => handleReviewTypeChange(val)">
          <ElRadioButton value="company">企业信息审核</ElRadioButton>
          <ElRadioButton value="school">学校管理员审核</ElRadioButton>
        </ElRadioGroup>
      </div>
    </ElCard>

    <!-- 企业管理员审核 -->
    <template v-if="reviewType === 'company'">
      <ElCard class="art-card-xs mt-4">
        <div class="sub-tab-bar flex items-center gap-4">
          <ElRadioGroup v-model="activeTab" @change="(val: any) => handleTabChange(val)">
            <ElRadioButton :value="2">待审核 ({{ pendingCount }})</ElRadioButton>
            <ElRadioButton :value="1">已通过 ({{ approvedCount }})</ElRadioButton>
            <ElRadioButton :value="0">已拒绝 ({{ rejectedCount }})</ElRadioButton>
          </ElRadioGroup>
        </div>
      </ElCard>

      <ElCard class="art-table-card mt-4">
        <ArtTable
          v-loading="loading"
          :data="data"
          :columns="columns"
          :pagination="pagination"
          @pagination:size-change="handleSizeChange"
          @pagination:current-change="handleCurrentChange"
        />

        <!-- 审核弹窗 -->
        <ElDialog v-model="reviewDialogVisible" title="企业管理员审核" width="500px">
          <div v-if="currentCompanyAdmin" class="review-detail">
            <ElDescriptions :column="1" border>
              <ElDescriptionsItem label="用户名">
                {{ currentCompanyAdmin.username }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="真实姓名">
                {{ currentCompanyAdmin.real_name || '-' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="邮箱">
                {{ currentCompanyAdmin.email || '-' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="账号状态">
                <ElTag :type="getStatusType(currentCompanyAdmin.status)">
                  {{ getStatusText(currentCompanyAdmin.status) }}
                </ElTag>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="注册时间">
                {{ currentCompanyAdmin.created_at }}
              </ElDescriptionsItem>
            </ElDescriptions>

            <ElForm class="mt-4" label-width="80px">
              <ElFormItem label="拒绝原因" v-if="activeTab === 2">
                <ElInput
                  v-model="rejectReason"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入拒绝原因（审核拒绝时必填）"
                />
              </ElFormItem>
            </ElForm>
          </div>
          <template #footer>
            <ElSpace>
              <ElButton @click="reviewDialogVisible = false">取消</ElButton>
              <ElButton
                type="danger"
                @click="handleCompanyReject"
                :loading="actionLoading"
                v-if="activeTab === 2"
              >
                拒绝
              </ElButton>
              <ElButton
                type="success"
                @click="handleCompanyApprove"
                :loading="actionLoading"
                v-if="activeTab === 2"
              >
                通过
              </ElButton>
            </ElSpace>
          </template>
        </ElDialog>

        <!-- 详情弹窗 -->
        <ElDialog v-model="detailDialogVisible" title="企业管理员详情" width="500px">
          <div v-if="currentCompanyAdmin">
            <ElDescriptions :column="1" border>
              <ElDescriptionsItem label="用户名">
                {{ currentCompanyAdmin.username }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="真实姓名">
                {{ currentCompanyAdmin.real_name || '-' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="邮箱">
                {{ currentCompanyAdmin.email || '-' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="账号状态">
                <ElTag :type="getStatusType(currentCompanyAdmin.status)">
                  {{ getStatusText(currentCompanyAdmin.status) }}
                </ElTag>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="注册时间">
                {{ currentCompanyAdmin.created_at }}
              </ElDescriptionsItem>
            </ElDescriptions>
          </div>
        </ElDialog>
      </ElCard>
    </template>

    <!-- 学校管理员审核 -->
    <template v-else>
      <ElCard class="art-card-xs mt-4">
        <div class="sub-tab-bar flex items-center gap-4">
          <ElRadioGroup v-model="schoolActiveTab" @change="(val: any) => handleSchoolTabChange(val)">
            <ElRadioButton :value="2">待审核 ({{ schoolPendingCount }})</ElRadioButton>
            <ElRadioButton :value="1">已通过 ({{ schoolApprovedCount }})</ElRadioButton>
            <ElRadioButton :value="0">已拒绝 ({{ schoolRejectedCount }})</ElRadioButton>
          </ElRadioGroup>
        </div>
      </ElCard>

      <ElCard class="art-table-card mt-4">
        <ArtTable
          v-loading="schoolLoading"
          :data="schoolData"
          :columns="schoolColumns"
          :pagination="schoolPagination"
          @pagination:size-change="handleSchoolSizeChange"
          @pagination:current-change="handleSchoolCurrentChange"
        />

        <!-- 审核弹窗 -->
        <ElDialog v-model="schoolReviewDialogVisible" title="学校管理员审核" width="500px">
          <div v-if="currentSchoolAdmin" class="review-detail">
            <ElDescriptions :column="1" border>
              <ElDescriptionsItem label="用户名">
                {{ currentSchoolAdmin.username }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="真实姓名">
                {{ currentSchoolAdmin.real_name || '-' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="邮箱">
                {{ currentSchoolAdmin.email || '-' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="账号状态">
                <ElTag :type="getSchoolStatusType(currentSchoolAdmin.status)">
                  {{ getSchoolStatusText(currentSchoolAdmin.status) }}
                </ElTag>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="注册时间">
                {{ currentSchoolAdmin.created_at }}
              </ElDescriptionsItem>
            </ElDescriptions>

            <ElForm class="mt-4" label-width="80px">
              <ElFormItem label="拒绝原因" v-if="schoolActiveTab === 2">
                <ElInput
                  v-model="schoolRejectReason"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入拒绝原因（审核拒绝时必填）"
                />
              </ElFormItem>
            </ElForm>
          </div>
          <template #footer>
            <ElSpace>
              <ElButton @click="schoolReviewDialogVisible = false">取消</ElButton>
              <ElButton
                type="danger"
                @click="handleSchoolReject"
                :loading="schoolActionLoading"
                v-if="schoolActiveTab === 2"
              >
                拒绝
              </ElButton>
              <ElButton
                type="success"
                @click="handleSchoolApprove"
                :loading="schoolActionLoading"
                v-if="schoolActiveTab === 2"
              >
                通过
              </ElButton>
            </ElSpace>
          </template>
        </ElDialog>

        <!-- 详情弹窗 -->
        <ElDialog v-model="schoolDetailDialogVisible" title="学校管理员详情" width="500px">
          <div v-if="currentSchoolAdmin">
            <ElDescriptions :column="1" border>
              <ElDescriptionsItem label="用户名">
                {{ currentSchoolAdmin.username }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="真实姓名">
                {{ currentSchoolAdmin.real_name || '-' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="邮箱">
                {{ currentSchoolAdmin.email || '-' }}
              </ElDescriptionsItem>
              <ElDescriptionsItem label="账号状态">
                <ElTag :type="getSchoolStatusType(currentSchoolAdmin.status)">
                  {{ getSchoolStatusText(currentSchoolAdmin.status) }}
                </ElTag>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="注册时间">
                {{ currentSchoolAdmin.created_at }}
              </ElDescriptionsItem>
            </ElDescriptions>
          </div>
        </ElDialog>
      </ElCard>
    </template>
  </div>
</template>

<script setup lang="ts">
  import {
    fetchCompanyAdmins,
    verifyCompanyAdmin,
    fetchSchoolAdmins,
    verifySchoolAdmin
  } from '@/api/admin'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { ElTag, ElMessage, ElMessageBox } from 'element-plus'
  import { h } from 'vue'

  defineOptions({ name: 'AdminProfileReview' })

  // ========== 企业管理员审核相关 ==========
  const reviewType = ref('company')
  const activeTab = ref(2)
  const pendingCount = ref(0)
  const approvedCount = ref(0)
  const rejectedCount = ref(0)

  const reviewDialogVisible = ref(false)
  const detailDialogVisible = ref(false)
  const actionLoading = ref(false)
  const loading = ref(false)
  const currentCompanyAdmin = ref<any>(null)
  const rejectReason = ref('')

  const pagination = ref({ current: 1, size: 20, total: 0 })
  const data = ref<any[]>([])

  const getStatusType = (status: number) => {
    switch (status) {
      case 1:
        return 'success'
      case 0:
        return 'danger'
      default:
        return 'warning'
    }
  }

  const getStatusText = (status: number) => {
    switch (status) {
      case 1:
        return '已通过'
      case 0:
        return '已拒绝'
      default:
        return '待审核'
    }
  }

  const columns = computed(() => [
    { type: 'index', width: 60, label: '序号' },
    { prop: 'username', label: '用户名', minWidth: 150 },
    { prop: 'real_name', label: '真实姓名', width: 120 },
    { prop: 'email', label: '邮箱', minWidth: 180 },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      formatter: (row: any) =>
        h(ElTag, { type: getStatusType(row.status), size: 'small' }, () =>
          getStatusText(row.status)
        )
    },
    { prop: 'created_at', label: '注册时间', width: 180 },
    {
      prop: 'operation',
      label: '操作',
      width: 180,
      fixed: 'right',
      formatter: (row: any) =>
        h('div', [
          h(ArtButtonTable, { type: 'view', onClick: () => handleView(row) }),
          activeTab.value === 2
            ? h(ArtButtonTable, { type: 'edit', onClick: () => handleReview(row) })
            : null
        ])
    }
  ])

  const getData = async (params: { status?: number; current?: number; size?: number } = {}) => {
    try {
      loading.value = true
      const res: any = await fetchCompanyAdmins({
        status: params.status ?? activeTab.value,
        current: params.current ?? pagination.value.current,
        size: params.size ?? pagination.value.size
      })
      const listData = res?.data?.list ?? res?.data ?? res?.list ?? []
      const totalData = res?.data?.total ?? res?.total ?? 0
      data.value = listData
      pagination.value.total = totalData
      if (activeTab.value === 2) pendingCount.value = totalData
      else if (activeTab.value === 1) approvedCount.value = totalData
      else rejectedCount.value = totalData
    } catch (error) {
      console.error('获取企业管理员列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const refreshAllCompanyCounts = async () => {
    try {
      const [pendingRes, approvedRes, rejectedRes]: any = await Promise.all([
        fetchCompanyAdmins({ status: 2, current: 1, size: 1 }),
        fetchCompanyAdmins({ status: 1, current: 1, size: 1 }),
        fetchCompanyAdmins({ status: 0, current: 1, size: 1 })
      ])
      pendingCount.value = pendingRes?.data?.total ?? pendingRes?.total ?? 0
      approvedCount.value = approvedRes?.data?.total ?? approvedRes?.total ?? 0
      rejectedCount.value = rejectedRes?.data?.total ?? rejectedRes?.total ?? 0
    } catch (error) {
      console.error('获取企业管理员数量失败:', error)
    }
  }

  const handleTabChange = (tab: number) => {
    activeTab.value = tab
    pagination.value.current = 1
    getData({ status: tab, current: 1 })
  }

  const handleSizeChange = (size: number) => {
    pagination.value.size = size
    getData({ status: activeTab.value, size })
  }

  const handleCurrentChange = (current: number) => {
    pagination.value.current = current
    getData({ status: activeTab.value, current })
  }

  const handleView = (row: any) => {
    currentCompanyAdmin.value = row
    detailDialogVisible.value = true
  }

  const handleReview = (row: any) => {
    currentCompanyAdmin.value = row
    rejectReason.value = ''
    reviewDialogVisible.value = true
  }

  const handleCompanyApprove = async () => {
    if (!currentCompanyAdmin.value?.account_id) return
    try {
      actionLoading.value = true
      const res: any = await verifyCompanyAdmin(currentCompanyAdmin.value.account_id, 'approve')
      if (res) {
        ElMessage.success('审核通过')
        reviewDialogVisible.value = false
        getData({ status: activeTab.value })
        await refreshAllCompanyCounts()
      }
    } catch (error) {
      console.error('审核失败:', error)
    } finally {
      actionLoading.value = false
    }
  }

  const handleCompanyReject = async () => {
    if (!currentCompanyAdmin.value?.account_id) return
    if (!rejectReason.value.trim()) {
      ElMessage.warning('请输入拒绝原因')
      return
    }
    try {
      await ElMessageBox.confirm('确定要拒绝该企业管理员的注册申请吗？', '拒绝审核', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      actionLoading.value = true
      const res: any = await verifyCompanyAdmin(currentCompanyAdmin.value.account_id, 'reject')
      if (res) {
        ElMessage.success('已拒绝')
        reviewDialogVisible.value = false
        getData({ status: activeTab.value })
        await refreshAllCompanyCounts()
      }
    } catch (error) {
      if (error !== 'cancel') console.error('拒绝失败:', error)
    } finally {
      actionLoading.value = false
    }
  }

  // ========== 学校管理员审核相关 ==========
  const handleReviewTypeChange = async (type: string) => {
    if (type === 'company') {
      await refreshAllCompanyCounts()
      getData({ status: activeTab.value })
    } else {
      pagination.value.current = 1
      await refreshAllSchoolCounts()
      getSchoolData({ status: schoolActiveTab.value, current: 1 })
    }
  }

  const refreshAllSchoolCounts = async () => {
    try {
      const [pendingRes, approvedRes, rejectedRes]: any = await Promise.all([
        fetchSchoolAdmins({ status: 2, current: 1, size: 1 }),
        fetchSchoolAdmins({ status: 1, current: 1, size: 1 }),
        fetchSchoolAdmins({ status: 0, current: 1, size: 1 })
      ])
      schoolPendingCount.value = pendingRes?.data?.total ?? pendingRes?.total ?? 0
      schoolApprovedCount.value = approvedRes?.data?.total ?? approvedRes?.total ?? 0
      schoolRejectedCount.value = rejectedRes?.data?.total ?? rejectedRes?.total ?? 0
    } catch (error) {
      console.error('获取学校管理员数量失败:', error)
    }
  }

  const schoolActiveTab = ref(2)
  const schoolPendingCount = ref(0)
  const schoolApprovedCount = ref(0)
  const schoolRejectedCount = ref(0)

  const schoolReviewDialogVisible = ref(false)
  const schoolDetailDialogVisible = ref(false)
  const schoolActionLoading = ref(false)
  const currentSchoolAdmin = ref<any>(null)
  const schoolRejectReason = ref('')

  const getSchoolStatusType = (status: number) => {
    switch (status) {
      case 1:
        return 'success'
      case 0:
        return 'danger'
      default:
        return 'warning'
    }
  }

  const getSchoolStatusText = (status: number) => {
    switch (status) {
      case 1:
        return '已通过'
      case 0:
        return '已拒绝'
      default:
        return '待审核'
    }
  }

  interface SchoolAdminItem {
    account_id: string
    username: string
    real_name: string
    email: string
    status: number
    created_at: string
  }

  const schoolData = ref<SchoolAdminItem[]>([])
  const schoolLoading = ref(false)
  const schoolPagination = ref({
    current: 1,
    size: 20,
    total: 0
  })

  const schoolColumns = computed(() => [
    { type: 'index', width: 60, label: '序号' },
    { prop: 'username', label: '用户名', minWidth: 150 },
    { prop: 'real_name', label: '真实姓名', width: 120 },
    { prop: 'email', label: '邮箱', width: 180 },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      formatter: (row: SchoolAdminItem) =>
        h(
          ElTag,
          {
            type: getSchoolStatusType(row.status),
            size: 'small'
          },
          () => getSchoolStatusText(row.status)
        )
    },
    { prop: 'created_at', label: '注册时间', width: 180 },
    {
      prop: 'operation',
      label: '操作',
      width: 180,
      fixed: 'right',
      formatter: (row: SchoolAdminItem) =>
        h('div', [
          h(ArtButtonTable, {
            type: 'view',
            onClick: () => handleSchoolView(row)
          }),
          schoolActiveTab.value === 2
            ? h(ArtButtonTable, {
                type: 'edit',
                onClick: () => handleSchoolReview(row)
              })
            : null
        ])
    }
  ])

  const getSchoolData = async (params: { status?: number; current?: number; size?: number } = {}) => {
    try {
      schoolLoading.value = true
      const res: any = await fetchSchoolAdmins({
        status: params.status ?? schoolActiveTab.value,
        current: params.current ?? schoolPagination.value.current,
        size: params.size ?? schoolPagination.value.size
      })
      // 处理响应数据，可能是 { data: { list, total } } 或直接是 { list, total }
      const listData = res?.data?.list ?? res?.data ?? res?.list ?? []
      const totalData = res?.data?.total ?? res?.total ?? 0
      schoolData.value = listData
      schoolPagination.value.total = totalData
      // 更新计数 - 根据当前tab更新对应的计数
      if (schoolActiveTab.value === 2) {
        schoolPendingCount.value = totalData
      } else if (schoolActiveTab.value === 1) {
        schoolApprovedCount.value = totalData
      } else {
        schoolRejectedCount.value = totalData
      }
    } catch (error) {
      console.error('获取学校管理员列表失败:', error)
    } finally {
      schoolLoading.value = false
    }
  }

  const handleSchoolTabChange = (tab: number) => {
    schoolActiveTab.value = tab
    schoolPagination.value.current = 1
    getSchoolData({ status: tab, current: 1 })
  }

  const handleSchoolSizeChange = (size: number) => {
    schoolPagination.value.size = size
    getSchoolData({ status: schoolActiveTab.value, size })
  }

  const handleSchoolCurrentChange = (current: number) => {
    schoolPagination.value.current = current
    getSchoolData({ status: schoolActiveTab.value, current })
  }

  const handleSchoolView = (row: SchoolAdminItem) => {
    currentSchoolAdmin.value = row
    schoolDetailDialogVisible.value = true
  }

  const handleSchoolReview = (row: SchoolAdminItem) => {
    currentSchoolAdmin.value = row
    schoolRejectReason.value = ''
    schoolReviewDialogVisible.value = true
  }

  const handleSchoolApprove = async () => {
    if (!currentSchoolAdmin.value?.account_id) return
    try {
      schoolActionLoading.value = true
      const res: any = await verifySchoolAdmin(currentSchoolAdmin.value.account_id, 'approve')
      if (res) {
        ElMessage.success('审核通过')
        schoolReviewDialogVisible.value = false
        getSchoolData({ status: schoolActiveTab.value })
      }
    } catch (error) {
      console.error('审核失败:', error)
    } finally {
      schoolActionLoading.value = false
    }
  }

  const handleSchoolReject = async () => {
    if (!currentSchoolAdmin.value?.account_id) return
    if (!schoolRejectReason.value.trim()) {
      ElMessage.warning('请输入拒绝原因')
      return
    }
    try {
      await ElMessageBox.confirm('确定要拒绝该学校管理员的注册申请吗？', '拒绝审核', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      schoolActionLoading.value = true
      const res: any = await verifySchoolAdmin(currentSchoolAdmin.value.account_id, 'reject')
      if (res) {
        ElMessage.success('已拒绝')
        schoolReviewDialogVisible.value = false
        getSchoolData({ status: schoolActiveTab.value })
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('拒绝失败:', error)
      }
    } finally {
      schoolActionLoading.value = false
    }
  }

  onMounted(async () => {
    await refreshAllCompanyCounts()
    getData({ status: activeTab.value })
  })
</script>

<style scoped>
  .page-admin-profile-review {
    padding: 20px;
  }

  .tab-bar {
    padding: 10px 0;
  }

  .sub-tab-bar {
    padding: 10px 0;
  }

  .review-detail {
    padding: 10px 0;
  }

  .text-primary {
    font-weight: bold;
    color: var(--el-color-primary);
  }
</style>