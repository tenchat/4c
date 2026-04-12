<script setup lang="ts">
  import { ref, h } from 'vue'
  import { useTable } from '@/hooks/core/useTable'
  import { fetchCompanyAnnouncements, type CompanyAnnouncement } from '@/api/school'

  defineOptions({ name: 'SchoolCompanyAnnouncements' })

  const detailVisible = ref(false)
  const currentAnnouncement = ref<CompanyAnnouncement | null>(null)

  const DEGREE_MAP: Record<number, string> = {
    0: '不限',
    1: '高中/中专',
    2: '大专',
    3: '本科',
    4: '硕士',
    5: '博士'
  }

  const searchForm = ref({
    keyword: '',
    company_name: '',
    major: '',
    degree: undefined as number | undefined,
    year: undefined as number | undefined
  })

  const { columns, data, loading, pagination, getData, handleSizeChange, handleCurrentChange } = useTable({
    core: {
      apiFn: fetchCompanyAnnouncements as any,
      paginationKey: { current: 'page', size: 'page_size' },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'title', label: '公告标题', minWidth: 200 },
        { prop: 'company_name', label: '发布企业', minWidth: 150 },
        { prop: 'city', label: '所在城市', minWidth: 100 },
        { prop: 'target_major', label: '目标专业', minWidth: 120 },
        {
          prop: 'target_degree',
          label: '学历要求',
          width: 100,
          formatter: (row: CompanyAnnouncement) => DEGREE_MAP[row.target_degree ?? 0] ?? '-'
        },
        {
          prop: 'headcount',
          label: '招聘人数',
          minWidth: 100,
          formatter: (row: CompanyAnnouncement) => row.headcount ?? '-'
        },
        { prop: 'deadline', label: '截止日期', minWidth: 120 },
        {
          label: '操作',
          width: 100,
          formatter: (row: CompanyAnnouncement) =>
            h('span', { class: 'text-primary cursor-pointer', onClick: () => showDetail(row) }, '查看详情')
        }
      ]
    }
  })

  const showDetail = (row: CompanyAnnouncement) => {
    currentAnnouncement.value = row
    detailVisible.value = true
  }

  const handleSearch = () => {
    getData()
  }

  const handleReset = () => {
    searchForm.value = {
      keyword: '',
      company_name: '',
      major: '',
      degree: undefined,
      year: undefined
    }
    getData()
  }
</script>

<template>
  <div class="page-school-company-announcements">
    <ElCard class="art-card-xs mb-4">
      <ElForm :model="searchForm" inline>
        <ElFormItem label="关键词">
          <ElInput v-model="searchForm.keyword" placeholder="搜索公告标题" clearable style="width: 160px" />
        </ElFormItem>
        <ElFormItem label="企业名称">
          <ElInput v-model="searchForm.company_name" placeholder="企业名称" clearable style="width: 140px" />
        </ElFormItem>
        <ElFormItem label="专业">
          <ElInput v-model="searchForm.major" placeholder="目标专业" clearable style="width: 120px" />
        </ElFormItem>
        <ElFormItem label="学历">
          <ElSelect v-model="searchForm.degree" placeholder="请选择" clearable style="width: 120px">
            <ElOption
              v-for="(label, value) in DEGREE_MAP"
              :key="value"
              :label="label"
              :value="Number(value)"
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
          <ElEmpty description="暂无公告" />
        </template>
      </ArtTable>
    </ElCard>

    <ElDialog v-model="detailVisible" title="公告详情" width="640px" destroy-on-close>
      <template v-if="currentAnnouncement">
        <ElDescriptions :column="1" border>
          <ElDescriptionsItem label="公告标题">{{ currentAnnouncement.title }}</ElDescriptionsItem>
          <ElDescriptionsItem label="发布企业">{{ currentAnnouncement.company_name }}</ElDescriptionsItem>
          <ElDescriptionsItem label="所在城市">{{ currentAnnouncement.city || '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="目标专业">{{ currentAnnouncement.target_major || '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="学历要求">
            {{ DEGREE_MAP[currentAnnouncement.target_degree ?? 0] ?? '-' }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="招聘人数">{{ currentAnnouncement.headcount ?? '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="截止日期">{{ currentAnnouncement.deadline || '-' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="发布时间">{{ currentAnnouncement.published_at || '-' }}</ElDescriptionsItem>
        </ElDescriptions>
        <ElDivider />
        <div class="announcement-content">
          <h4>公告内容</h4>
          <div class="content-text">{{ currentAnnouncement.content }}</div>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
  .page-school-company-announcements {
    padding: 20px;
  }

  .announcement-content h4 {
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
