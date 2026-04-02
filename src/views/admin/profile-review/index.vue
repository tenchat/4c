<!-- 企业信息审核管理页面 -->
<template>
  <div class="page-admin-profile-review art-full-height">
    <ElCard class="art-card-xs">
      <div class="tab-bar flex items-center gap-4">
        <ElRadioGroup v-model="activeTab" @change="(val: any) => handleTabChange(val)">
          <ElRadioButton :value="'pending'">待审核 ({{ pendingCount }})</ElRadioButton>
          <ElRadioButton :value="'approved'">已通过 ({{ approvedCount }})</ElRadioButton>
          <ElRadioButton :value="'rejected'">已拒绝 ({{ rejectedCount }})</ElRadioButton>
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
      <ElDialog v-model="reviewDialogVisible" title="企业信息审核" width="700px">
        <div v-if="currentUpdate" class="review-detail">
          <ElAlert :title="diffMessage" type="info" :closable="false" class="mb-4" />

          <ElDescriptions :column="2" border>
            <ElDescriptionsItem label="企业名称" :span="2">
              {{ currentUpdate.company_name }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="行业">
              {{ currentUpdate.industry || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="企业规模">
              {{ currentUpdate.size || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="城市">
              {{ currentUpdate.city || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="地址">
              <span
                :class="{ 'text-primary': currentUpdate.address !== currentUpdate.current_address }"
              >
                {{ currentUpdate.address || '-' }}
              </span>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="邮箱">
              <span
                :class="{ 'text-primary': currentUpdate.email !== currentUpdate.current_email }"
              >
                {{ currentUpdate.email || '-' }}
              </span>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="联系人">
              <span
                :class="{ 'text-primary': currentUpdate.contact !== currentUpdate.current_contact }"
              >
                {{ currentUpdate.contact || '-' }}
              </span>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="联系方式">
              <span
                :class="{
                  'text-primary':
                    currentUpdate.contact_phone !== currentUpdate.current_contact_phone
                }"
              >
                {{ currentUpdate.contact_phone || '-' }}
              </span>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="企业简介" :span="2">
              {{ currentUpdate.description || '-' }}
            </ElDescriptionsItem>
          </ElDescriptions>

          <ElForm class="mt-4" label-width="80px">
            <ElFormItem label="拒绝原因" v-if="activeTab === 'pending'">
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
              @click="handleReject"
              :loading="actionLoading"
              v-if="activeTab === 'pending'"
            >
              拒绝
            </ElButton>
            <ElButton
              type="success"
              @click="handleApprove"
              :loading="actionLoading"
              v-if="activeTab === 'pending'"
            >
              通过
            </ElButton>
          </ElSpace>
        </template>
      </ElDialog>

      <!-- 查看详情弹窗 -->
      <ElDialog v-model="detailDialogVisible" title="企业信息详情" width="600px">
        <div v-if="currentUpdate" class="company-detail">
          <ElDescriptions :column="1" border>
            <ElDescriptionsItem label="企业名称">
              {{ currentUpdate.company_name }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="行业">
              {{ currentUpdate.industry || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="企业规模">
              {{ currentUpdate.size || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="城市">
              {{ currentUpdate.city || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="地址">
              {{ currentUpdate.address || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="邮箱">
              {{ currentUpdate.email || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="联系人">
              {{ currentUpdate.contact || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="联系方式">
              {{ currentUpdate.contact_phone || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="企业简介">
              {{ currentUpdate.description || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="审核状态">
              <ElTag :type="getStatusType(currentUpdate.status)">
                {{ getStatusText(currentUpdate.status) }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="申请时间">
              {{ currentUpdate.submitted_at }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="拒绝原因" v-if="currentUpdate.reject_reason">
              {{ currentUpdate.reject_reason }}
            </ElDescriptionsItem>
          </ElDescriptions>
        </div>
      </ElDialog>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchPendingProfileUpdates, reviewProfileUpdate } from '@/api/admin'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { ElTag, ElMessage, ElMessageBox } from 'element-plus'

  defineOptions({ name: 'AdminProfileReview' })

  interface ProfileUpdateItem {
    pending_id: string
    company_id: string
    company_name: string
    industry: string
    city: string
    size: string
    description: string
    current_address: string
    current_email: string
    current_contact: string
    current_contact_phone: string
    address: string
    email: string
    contact: string
    contact_phone: string
    status: string
    reject_reason: string
    submitted_at: string
    reviewed_at: string
  }

  const activeTab = ref('pending')
  const pendingCount = ref(0)
  const approvedCount = ref(0)
  const rejectedCount = ref(0)

  const reviewDialogVisible = ref(false)
  const detailDialogVisible = ref(false)
  const actionLoading = ref(false)
  const currentUpdate = ref<ProfileUpdateItem | null>(null)
  const rejectReason = ref('')

  const diffMessage = computed(() => {
    if (!currentUpdate.value) return ''
    const changes: string[] = []
    if (currentUpdate.value.address !== currentUpdate.value.current_address) {
      changes.push('地址')
    }
    if (currentUpdate.value.email !== currentUpdate.value.current_email) {
      changes.push('邮箱')
    }
    if (currentUpdate.value.contact !== currentUpdate.value.current_contact) {
      changes.push('联系人')
    }
    if (currentUpdate.value.contact_phone !== currentUpdate.value.current_contact_phone) {
      changes.push('联系方式')
    }
    return changes.length > 0 ? `以下信息有变更：${changes.join('、')}` : '暂无信息变更'
  })

  const getStatusType = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success'
      case 'rejected':
        return 'danger'
      default:
        return 'warning'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved':
        return '已通过'
      case 'rejected':
        return '已拒绝'
      default:
        return '待审核'
    }
  }

  const {
    columns,
    data,
    loading,
    pagination,
    getData,
    handleSizeChange,
    handleCurrentChange,
    refreshData
  } = useTable({
    core: {
      apiFn: fetchPendingProfileUpdates as any,
      apiParams: {
        current: 1,
        size: 20,
        status: activeTab.value
      },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'company_name', label: '企业名称', minWidth: 180 },
        { prop: 'industry', label: '行业', width: 100 },
        { prop: 'city', label: '城市', width: 100 },
        {
          prop: 'status',
          label: '状态',
          width: 100,
          formatter: (row: ProfileUpdateItem) =>
            h(
              ElTag,
              {
                type: getStatusType(row.status),
                size: 'small'
              },
              () => getStatusText(row.status)
            )
        },
        { prop: 'submitted_at', label: '申请时间', width: 180 },
        {
          prop: 'operation',
          label: '操作',
          width: 180,
          fixed: 'right',
          formatter: (row: ProfileUpdateItem) =>
            h('div', [
              h(ArtButtonTable, {
                type: 'view',
                onClick: () => handleView(row)
              }),
              activeTab.value === 'pending'
                ? h(ArtButtonTable, {
                    type: 'edit',
                    onClick: () => handleReview(row)
                  })
                : null
            ])
        }
      ]
    }
  })

  // 监听数据变化，更新数量
  watch(data, (newData) => {
    const list = newData as ProfileUpdateItem[]
    if (activeTab.value === 'pending') {
      pendingCount.value = list?.length || 0
    } else if (activeTab.value === 'approved') {
      approvedCount.value = list?.length || 0
    } else {
      rejectedCount.value = list?.length || 0
    }
  })

  const handleTabChange = (tab: string) => {
    activeTab.value = tab
    handleCurrentChange(1)
    getData({ status: tab })
  }

  const handleView = (row: ProfileUpdateItem) => {
    currentUpdate.value = row
    detailDialogVisible.value = true
  }

  const handleReview = (row: ProfileUpdateItem) => {
    currentUpdate.value = row
    rejectReason.value = ''
    reviewDialogVisible.value = true
  }

  const handleApprove = async () => {
    if (!currentUpdate.value?.pending_id) return
    try {
      actionLoading.value = true
      const res: any = await reviewProfileUpdate(currentUpdate.value.pending_id, {
        action: 'approve'
      })
      if (res) {
        ElMessage.success('审核通过')
        reviewDialogVisible.value = false
        refreshData()
      }
    } catch (error) {
      console.error('审核失败:', error)
    } finally {
      actionLoading.value = false
    }
  }

  const handleReject = async () => {
    if (!currentUpdate.value?.pending_id) return
    if (!rejectReason.value.trim()) {
      ElMessage.warning('请输入拒绝原因')
      return
    }
    try {
      await ElMessageBox.confirm('确定要拒绝该企业的信息更新吗？', '拒绝审核', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      actionLoading.value = true
      const res: any = await reviewProfileUpdate(currentUpdate.value.pending_id, {
        action: 'reject',
        reject_reason: rejectReason.value
      })
      if (res) {
        ElMessage.success('已拒绝')
        reviewDialogVisible.value = false
        refreshData()
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('拒绝失败:', error)
      }
    } finally {
      actionLoading.value = false
    }
  }

  onMounted(() => {
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

  .review-detail {
    padding: 10px 0;
  }

  .text-primary {
    font-weight: bold;
    color: var(--el-color-primary);
  }
</style>
