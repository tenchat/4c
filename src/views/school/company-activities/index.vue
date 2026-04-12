<script setup lang="ts">
  import { ref, h } from 'vue'
  import { useTable } from '@/hooks/core/useTable'
  import { fetchCompanyActivities, type CompanyActivity } from '@/api/school'

  defineOptions({ name: 'SchoolCompanyActivities' })

  const detailVisible = ref(false)
  const currentActivity = ref<CompanyActivity | null>(null)

  const ACTIVITY_TYPE_MAP: Record<string, string> = {
    seminar: '宣讲会',
    job_fair: '招聘会',
    other: '其他活动'
  }

  const searchForm = ref({
    keyword: '',
    company_name: '',
    activity_type: '',
    year: undefined as number | undefined
  })

  const { columns, data, loading, pagination, getData, handleSizeChange, handleCurrentChange } = useTable({
    core: {
      apiFn: fetchCompanyActivities as any,
      paginationKey: { current: 'page', size: 'page_size' },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'title', label: '活动标题', minWidth: 200 },
        { prop: 'company_name', label: '主办企业', minWidth: 150 },
        { prop: 'city', label: '所在城市', minWidth: 100 },
        {
          prop: 'type',
          label: '活动类型',
          width: 100,
          formatter: (row: CompanyActivity) => ACTIVITY_TYPE_MAP[row.type] ?? row.type
        },
        { prop: 'activity_date', label: '活动日期', minWidth: 120 },
        { prop: 'location', label: '活动地点', minWidth: 150 },
        { prop: 'expected_num', label: '预计人数', width: 100 },
        {
          label: '操作',
          width: 100,
          formatter: (row: CompanyActivity) =>
            h('span', { class: 'text-primary cursor-pointer', onClick: () => showDetail(row) }, '查看详情')
        }
      ]
    }
  })

  const showDetail = (row: CompanyActivity) => {
    currentActivity.value = row
    detailVisible.value = true
  }

  const handleSearch = () => {
    getData()
  }

  const handleReset = () => {
    searchForm.value = {
      keyword: '',
      company_name: '',
      activity_type: '',
      year: undefined
    }
    getData()
  }
</script>

<template>
  <div class="page-school-company-activities">
    <ElCard class="art-card-xs mb-4">
      <ElForm :model="searchForm" inline>
        <ElFormItem label="关键词">
          <ElInput v-model="searchForm.keyword" placeholder="搜索活动标题" clearable style="width: 160px" />
        </ElFormItem>
        <ElFormItem label="企业名称">
          <ElInput v-model="searchForm.company_name" placeholder="企业名称" clearable style="width: 140px" />
        </ElFormItem>
        <ElFormItem label="活动类型">
          <ElSelect v-model="searchForm.activity_type" placeholder="请选择" clearable style="width: 140px">
            <ElOption
              v-for="(label, value) in ACTIVITY_TYPE_MAP"
              :key="value"
              :label="label"
              :value="value"
            />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="年份">
          <ElSelect v-model="searchForm.year" placeholder="请选择" clearable style="width: 120px">
            <ElOption v-for="y in [2024, 2025, 2026]" :key="y" :label="`${y}年`" :value="y" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" @click="handleSearch">搜索</ElButton>
          <ElButton @click="handleReset">重置</ElButton>
        </ElFormItem>
      </ElForm>
    </ElCard>

    <ElCard class="art-table-card">
      <ArtTable
        :data="data"
        :loading="loading"
        :columns="columns"
        :pagination="pagination"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      >
        <template #empty>
          <ElEmpty description="暂无活动" />
        </template>
      </ArtTable>
    </ElCard>

    <ElDialog v-model="detailVisible" title="活动详情" width="640px" destroy-on-close>
      <template v-if="currentActivity">
        <ElDescriptions :column="1" border>
          <ElDescriptionsItem label="活动标题">{{ currentActivity.title }}</ElDescriptionsItem>
          <ElDescriptionsItem label="主办企业">{{ currentActivity.company_name }}</ElDescriptionsItem>
          <ElDescriptionsItem label="所在城市">{{ currentActivity.city || '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="活动类型">
            {{ ACTIVITY_TYPE_MAP[currentActivity.type] ?? currentActivity.type }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="活动日期">{{ currentActivity.activity_date || '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="开始时间">{{ currentActivity.start_time || '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="结束时间">{{ currentActivity.end_time || '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="活动地点">{{ currentActivity.location || '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="预计人数">{{ currentActivity.expected_num ?? '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="实际人数">{{ currentActivity.actual_num ?? '-' }}</ElDescriptionsItem>
        </ElDescriptions>
        <ElDivider />
        <div class="activity-content">
          <h4>活动说明</h4>
          <div class="content-text">{{ currentActivity.description || '暂无说明' }}</div>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
  .page-school-company-activities {
    padding: 20px;
  }

  .activity-content h4 {
    margin-bottom: 12px;
    font-weight: 600;
  }

  .content-text {
    white-space: pre-wrap;
    line-height: 1.8;
    color: var(--el-text-color-regular);
  }

  .text-primary {
    color: var(--el-color-primary);
  }

  .cursor-pointer {
    cursor: pointer;
  }
</style>
