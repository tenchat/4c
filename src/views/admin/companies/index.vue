<!-- 企业审核管理页面 -->
<template>
  <div class="page-admin-companies art-full-height">
    <ElCard class="art-card-xs">
      <div class="tab-bar flex items-center gap-4">
        <ElRadioGroup v-model="activeTab" @change="(val: any) => handleTabChange(val)">
          <ElRadioButton :value="0">待审核 ({{ pendingCount }})</ElRadioButton>
          <ElRadioButton :value="1">已审核 ({{ approvedCount }})</ElRadioButton>
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
      <ElDialog v-model="verifyDialogVisible" title="企业审核" width="500px">
        <div v-if="currentCompany" class="company-detail">
          <ElDescriptions :column="1" border>
            <ElDescriptionsItem label="企业名称">
              {{ currentCompany.company_name }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="行业">
              {{ INDUSTRY_MAP[currentCompany.industry] || currentCompany.industry }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="企业规模">
              {{ SCALE_MAP[currentCompany.size] || currentCompany.size || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="城市">
              {{ currentCompany.city || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="企业简介">
              {{ currentCompany.description || '-' }}
            </ElDescriptionsItem>
          </ElDescriptions>

          <ElForm class="mt-4" label-width="80px">
            <ElFormItem label="审核备注">
              <ElInput
                v-model="verifyRemark"
                type="textarea"
                :rows="3"
                placeholder="请输入审核备注（可选）"
              />
            </ElFormItem>
          </ElForm>
        </div>
        <template #footer>
          <ElSpace>
            <ElButton @click="verifyDialogVisible = false">取消</ElButton>
            <ElButton type="danger" @click="handleReject" :loading="actionLoading"> 拒绝 </ElButton>
            <ElButton type="success" @click="handleApprove" :loading="actionLoading">
              通过
            </ElButton>
          </ElSpace>
        </template>
      </ElDialog>

      <!-- 查看详情弹窗 -->
      <ElDialog v-model="detailDialogVisible" title="企业详情" width="600px">
        <div v-if="currentCompany" class="company-detail">
          <ElDescriptions :column="1" border>
            <ElDescriptionsItem label="企业名称">
              {{ currentCompany.company_name }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="行业">
              {{ INDUSTRY_MAP[currentCompany.industry] || currentCompany.industry }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="企业规模">
              {{ SCALE_MAP[currentCompany.size] || currentCompany.size || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="城市">
              {{ currentCompany.city || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="企业简介">
              {{ currentCompany.description || '-' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="审核状态">
              <ElTag :type="activeTab === 1 ? 'success' : 'info'">
                {{ activeTab === 1 ? '已审核' : '待审核' }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem label="创建时间">
              {{ currentCompany.created_at }}
            </ElDescriptionsItem>
          </ElDescriptions>
        </div>
      </ElDialog>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchPendingCompanies, verifyCompany } from '@/api/admin'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { ElTag, ElMessage, ElMessageBox } from 'element-plus'

  defineOptions({ name: 'AdminCompanies' })

  interface CompanyItem {
    company_id: string
    company_name: string
    industry: string
    city: string
    size: string
    description: string
    verified: boolean
    created_at: string
  }

  const activeTab = ref(0)
  const pendingCount = ref(0)
  const approvedCount = ref(0)

  const verifyDialogVisible = ref(false)
  const detailDialogVisible = ref(false)
  const actionLoading = ref(false)
  const currentCompany = ref<CompanyItem | null>(null)
  const verifyRemark = ref('')

  const INDUSTRY_MAP: Record<string, string> = {
    // 英文key (企业表)
    internet: '互联网/IT',
    finance: '金融',
    education: '教育',
    manufacturing: '制造业',
    real_estate: '房地产',
    healthcare: '医疗健康',
    government: '政府/事业单位',
    other: '其他',
    // 中文值 (学生表cur_industry)
    互联网: '互联网/IT',
    '金融/银行': '金融/银行',
    教育培训: '教育培训',
    '房地产/建筑': '房地产/建筑',
    医药生物: '医药生物',
    '政府/公共事业': '政府/公共事业',
    计算机软件: '计算机软件',
    '电子/半导体': '电子/半导体',
    化工: '化工',
    '机械/装备制造': '机械/装备制造',
    '汽车/交通设备': '汽车/交通设备',
    '通信/网络设备': '通信/网络设备',
    '电力/能源': '电力/能源',
    新材料: '新材料',
    航空航天: '航空航天',
    现代农业: '现代农业',
    '批发/零售': '批发/零售',
    '文化/传媒': '文化/传媒',
    保险: '保险',
    环保: '环保',
    // desire_industry 混合值
    金融: '金融',
    '互联网/IT': '互联网/IT'
  }

  const SCALE_MAP: Record<string, string> = {
    small: '小微企业(20人以下)',
    medium: '中型企业(20-500人)',
    large: '大型企业(500人以上)'
  }

  const {
    columns,
    data,
    loading,
    pagination,
    getData,
    handleSizeChange,
    handleCurrentChange,
    refreshData,
    replaceSearchParams
  } = useTable({
    core: {
      apiFn: fetchPendingCompanies as any,
      apiParams: {
        current: 1,
        size: 20,
        status: activeTab.value
      },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'company_name', label: '企业名称', minWidth: 200 },
        {
          prop: 'industry',
          label: '行业',
          width: 120,
          formatter: (row: CompanyItem) => INDUSTRY_MAP[row.industry] || row.industry || '-'
        },
        {
          prop: 'size',
          label: '企业规模',
          width: 150,
          formatter: (row: CompanyItem) => SCALE_MAP[row.size] || row.size || '-'
        },
        { prop: 'city', label: '城市', width: 120 },
        {
          prop: 'status',
          label: '审核状态',
          width: 100,
          formatter: (row: CompanyItem) =>
            h(
              ElTag,
              {
                type: row.verified ? 'success' : 'danger',
                size: 'small'
              },
              () => (row.verified ? '通过' : '未通过')
            )
        },
        { prop: 'created_at', label: '申请时间', width: 180 },
        {
          prop: 'operation',
          label: '操作',
          width: 180,
          fixed: 'right',
          formatter: (row: CompanyItem) =>
            h('div', [
              h(ArtButtonTable, {
                type: 'view',
                onClick: () => handleView(row)
              }),
              activeTab.value === 0
                ? h(ArtButtonTable, {
                    type: 'edit',
                    onClick: () => handleVerify(row)
                  })
                : null
            ])
        }
      ]
    }
  })

  // 监听分页总数变化，更新待审核/已审核数量
  watch(
    () => pagination.total,
    (newTotal) => {
      if (activeTab.value === 0) {
        pendingCount.value = newTotal || 0
      } else {
        approvedCount.value = newTotal || 0
      }
    }
  )

  const handleTabChange = (tab: number) => {
    activeTab.value = tab
    // 先重置搜索参数，确保 status 被正确更新
    replaceSearchParams({ status: tab })
    handleCurrentChange(1)
  }

  const handleView = (row: CompanyItem) => {
    currentCompany.value = row
    detailDialogVisible.value = true
  }

  const handleVerify = (row: CompanyItem) => {
    currentCompany.value = row
    verifyRemark.value = ''
    verifyDialogVisible.value = true
  }

  const handleApprove = async () => {
    if (!currentCompany.value?.company_id) return
    try {
      actionLoading.value = true
      const res: any = await verifyCompany(currentCompany.value.company_id, 'approve')
      if (res) {
        ElMessage.success('审核通过')
        verifyDialogVisible.value = false
        refreshData()
      }
    } catch (error) {
      console.error('审核失败:', error)
    } finally {
      actionLoading.value = false
    }
  }

  const handleReject = async () => {
    if (!currentCompany.value?.company_id) return
    try {
      await ElMessageBox.confirm('确定要拒绝该企业的入驻申请吗？', '拒绝审核', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      actionLoading.value = true
      const res: any = await verifyCompany(currentCompany.value.company_id, 'reject')
      if (res) {
        ElMessage.success('已拒绝')
        verifyDialogVisible.value = false
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
  .page-admin-companies {
    padding: 20px;
  }

  .tab-bar {
    padding: 10px 0;
  }

  .company-detail {
    padding: 10px 0;
  }
</style>
