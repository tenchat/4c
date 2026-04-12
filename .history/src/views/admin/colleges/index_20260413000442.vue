<!-- 学院就业管理页面 -->
<template>
  <div class="page-admin-colleges art-full-height">
    <ElCard class="art-card-xs">
      <ArtSearchBar
        v-model="searchForm"
        :items="searchItems"
        :span="6"
        :gutter="12"
        @search="handleSearch"
        @reset="handleReset"
      />
    </ElCard>

    <ElCard class="art-table-card mt-4">
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
        <template #left>
          <ElSpace wrap>
            <ElButton @click="handleImport" v-ripple>导入数据</ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchAdminColleges } from '@/api/admin'
  import { fetchSchoolColleges } from '@/api/school'
  import { useTable } from '@/hooks/core/useTable'
  import { ElMessage, ElProgress } from 'element-plus'
  import { useUserStore, RoleEnum } from '@/store/modules/user'

  defineOptions({ name: 'AdminColleges' })

  interface CollegeItem {
    record_id: string
    college_name: string
    graduation_year: number
    graduate_nums: number
    employed_nums: number
    employment_rate: number
    further_study_nums: number
    overseas_nums: number
    avg_salary: number
  }

  const userStore = useUserStore()
  const isSchoolAdmin = computed(() => userStore.info.roles?.includes(RoleEnum.SCHOOL))

  // 根据用户角色选择 API
  const collegesApi = computed(() => isSchoolAdmin.value ? fetchSchoolColleges : fetchAdminColleges)

  const searchForm = ref({
    year: undefined as number | undefined
  })

  const yearOptions = [
    { label: '全部年份', value: undefined },
    { label: '2022', value: 2022 },
    { label: '2023', value: 2023 },
    { label: '2024', value: 2024 },
    { label: '2025', value: 2025 }
  ]

  const {
    columns,
    columnChecks,
    data,
    loading,
    pagination,
    getData,
    replaceSearchParams,
    resetSearchParams,
    handleSizeChange,
    handleCurrentChange,
    refreshData
  } = useTable({
    core: {
      apiFn: collegesApi.value as any,
      apiParams: {
        current: 1,
        size: 20,
        year: searchForm.value.year
      },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'college_name', label: '学院名称', minWidth: 150 },
        {
          prop: 'employment_rate',
          label: '就业率',
          width: 180,
          formatter: (row: any) =>
            h('div', { class: 'flex items-center gap-2' }, [
              h(ElProgress, {
                percentage: row.employment_rate || 0,
                width: 60,
                type: 'circle',
                strokeWidth: 6
              }),
              h('span', {}, `${row.employment_rate || 0}%`)
            ])
        },
        { prop: 'graduate_nums', label: '毕业生总数', width: 100 },
        { prop: 'employed_nums', label: '已就业人数', width: 100 },
        { prop: 'further_study_nums', label: '深造人数', width: 100 },
        { prop: 'overseas_nums', label: '出国人数', width: 100 },
        { prop: 'avg_salary', label: '平均薪资', width: 120 }
      ]
    }
  })

  const searchItems = computed(() => [
    {
      key: 'year',
      label: '毕业年份',
      type: 'select' as const,
      props: {
        placeholder: '选择年份',
        clearable: true,
        options: yearOptions
      }
    }
  ])

  const handleSearch = (params: Record<string, unknown>) => {
    replaceSearchParams(params)
    getData()
  }

  const handleReset = () => {
    resetSearchParams()
  }

  const handleImport = () => {
    ElMessage.info('导入功能开发中')
  }
</script>

<style scoped>
  .page-admin-colleges {
    padding: 20px;
  }
</style>
