<!-- 学校端学生管理页面 -->
<template>
  <div class="page-school-students art-full-height">
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
            <ElButton @click="handleExport" v-ripple>导出Excel</ElButton>
            <ElButton type="primary" @click="showImportDialog = true" v-ripple>批量导入</ElButton>
            <ElButton
              v-if="selectedRows.length > 0"
              type="danger"
              @click="handleBatchDelete"
              v-ripple
            >
              批量删除 ({{ selectedRows.length }})
            </ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />
    </ElCard>

    <!-- 批量导入预览弹窗 -->
    <ElDialog
      v-model="showImportDialog"
      title="批量导入学生"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="!importPreviewData">
        <ElUpload
          ref="uploadRef"
          class="import-upload"
          drag
          :auto-upload="false"
          :accept="'.xlsx,.xls,.csv'"
          :on-change="handleFileChange"
          :limit="1"
        >
          <ElIcon><Upload /></ElIcon>
          <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .xlsx/.xls/.csv 文件，请确保包含 <strong>student_no</strong> 列
            </div>
          </template>
        </ElUpload>
        <div class="mt-4 text-xs text-gray-500">
          <p>Excel/CSV 格式说明：</p>
          <p>必需列：student_no（学号）</p>
          <p>
            可选列：college（学院）、major（专业）、degree（学历1-5）、graduation_year（毕业年份）、class（班级）、province_origin（生源省份）、employment_status（就业状态0-3）
          </p>
        </div>
      </div>

      <div v-else>
        <ElAlert
          :title="`共 ${importPreviewData.total ?? 0} 条数据，其中 ${(importPreviewData.preview ?? []).filter((r: any) => r.is_registered).length} 条已注册`"
          type="info"
          :closable="false"
          class="mb-4"
        />
        <ElTable :data="importPreviewData.preview ?? []" stripe max-height="400" size="small">
          <ElTableColumn type="index" width="50" label="序号" />
          <ElTableColumn prop="student_no" label="学号" width="120" />
          <ElTableColumn prop="college" label="学院" min-width="120" />
          <ElTableColumn prop="major" label="专业" min-width="120" />
          <ElTableColumn prop="class_name" label="班级" width="100" />
          <ElTableColumn prop="degree" label="学历" width="70">
            <template #default="{ row }">
              {{ DEGREE_MAP[row.degree] || row.degree }}
            </template>
          </ElTableColumn>
          <ElTableColumn prop="graduation_year" label="毕业年份" width="100" />
          <ElTableColumn prop="is_registered" label="状态" width="90">
            <template #default="{ row }">
              <ElTag :type="row.is_registered ? 'success' : 'info'" size="small">
                {{ row.is_registered ? '已注册' : '未注册' }}
              </ElTag>
            </template>
          </ElTableColumn>
        </ElTable>

        <div v-if="importPreviewData.errors?.length" class="mt-4">
          <ElAlert
            v-for="(err, i) in importPreviewData.errors"
            :key="i"
            :title="err"
            type="warning"
            :closable="false"
            class="mb-2"
          />
        </div>
      </div>

      <template #footer>
        <ElButton @click="cancelImport">取消</ElButton>
        <ElButton
          v-if="!importPreviewData"
          type="primary"
          :loading="previewLoading"
          @click="handlePreview"
        >
          预览
        </ElButton>
        <ElButton v-else type="primary" :loading="importLoading" @click="handleConfirmImport">
          确认导入 ({{ importPreviewData.total }} 条)
        </ElButton>
      </template>
    </ElDialog>

    <!-- 学生详情弹窗 -->
    <ElDialog v-model="showDetailDialog" title="学生档案详情" width="700px">
      <div v-if="studentDetail" class="detail-grid">
        <div class="detail-section">
          <div class="detail-title">基本信息</div>
          <div class="detail-row">
            <span class="detail-label">学号</span>
            <span class="detail-value">{{ studentDetail.student_no }}</span>
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
            <span class="detail-label">班级</span>
            <span class="detail-value">{{ studentDetail.class_name || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">学历</span>
            <span class="detail-value">{{ studentDetail.degree_text }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">毕业年份</span>
            <span class="detail-value">{{ studentDetail.graduation_year || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">生源省份</span>
            <span class="detail-value">{{ studentDetail.province_origin || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">注册状态</span>
            <ElTag :type="studentDetail.is_registered ? 'success' : 'info'" size="small">
              {{ studentDetail.is_registered ? '已注册' : '未注册' }}
            </ElTag>
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
            <span class="detail-label">就业状态</span>
            <ElTag
              :type="EMPLOYMENT_STATUS_MAP[studentDetail.employment_status]?.type || 'info'"
              size="small"
            >
              {{ studentDetail.employment_status_text }}
            </ElTag>
          </div>
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
            <span class="detail-value">{{
              INDUSTRY_MAP[studentDetail.cur_industry] || studentDetail.cur_industry || '-'
            }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">当前薪资</span>
            <span class="detail-value">{{
              studentDetail.cur_salary ? `${studentDetail.cur_salary}元/月` : '-'
            }}</span>
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
            <span class="detail-value">{{
              INDUSTRY_MAP[studentDetail.desire_industry] || studentDetail.desire_industry || '-'
            }}</span>
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
  import {
    fetchSchoolStudents,
    fetchStudentDetail,
    importStudentsPreview,
    confirmImportStudents,
    batchDeleteStudents,
    exportSchoolStudents
  } from '@/api/school'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { Upload } from '@element-plus/icons-vue'
  import { ElTag, ElMessage, ElMessageBox, ElIcon } from 'element-plus'

  defineOptions({ name: 'SchoolStudents' })

  interface StudentItem {
    profile_id: string
    account_id: string
    student_no: string
    college: string
    major: string
    class_name?: string
    degree: number
    graduation_year: number
    employment_status: number
    cur_company?: string
    cur_city?: string
    is_registered: boolean
  }

  const selectedRows = ref<StudentItem[]>([])
  const showImportDialog = ref(false)
  const previewLoading = ref(false)
  const importLoading = ref(false)
  const importFile = ref<File | null>(null)
  const importPreviewData = ref<any>(null)
  const uploadRef = ref()
  const showDetailDialog = ref(false)
  const studentDetail = ref<any>(null)
  const detailLoading = ref(false)

  const searchForm = ref({
    college: undefined,
    major: undefined,
    employment_status: undefined,
    graduation_year: undefined,
    keyword: undefined
  })

  const EMPLOYMENT_STATUS_MAP: Record<number, { type: string; text: string }> = {
    0: { type: 'info', text: '待就业' },
    1: { type: 'success', text: '已就业' },
    2: { type: 'warning', text: '升学' },
    3: { type: 'primary', text: '出国' }
  }

  const DEGREE_MAP: Record<number, string> = {
    1: '本科',
    2: '硕士',
    3: '博士',
    4: '大专',
    5: '其他'
  }

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
    '互联网': '互联网/IT',
    '金融/银行': '金融/银行',
    '教育培训': '教育培训',
    '房地产/建筑': '房地产/建筑',
    '医药生物': '医药生物',
    '政府/公共事业': '政府/公共事业',
    '计算机软件': '计算机软件',
    '电子/半导体': '电子/半导体',
    '化工': '化工',
    '机械/装备制造': '机械/装备制造',
    '汽车/交通设备': '汽车/交通设备',
    '通信/网络设备': '通信/网络设备',
    '电力/能源': '电力/能源',
    '新材料': '新材料',
    '航空航天': '航空航天',
    '现代农业': '现代农业',
    '批发/零售': '批发/零售',
    '文化/传媒': '文化/传媒',
    '保险': '保险',
    '环保': '环保',
    // desire_industry 混合值
    '金融': '金融',
    '互联网/IT': '互联网/IT',
  }

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
      apiFn: fetchSchoolStudents as any,
      apiParams: {
        page: 1,
        page_size: 20,
        ...searchForm.value
      },
      paginationKey: {
        current: 'page',
        size: 'page_size'
      },
      columnsFactory: () => [
        { type: 'selection', width: 60 },
        { type: 'index', width: 60, label: '序号' },
        { prop: 'student_no', label: '学号', width: 140 },
        { prop: 'college', label: '学院', minWidth: 150 },
        { prop: 'major', label: '专业', minWidth: 150 },
        { prop: 'class_name', label: '班级', minWidth: 100, show: false },
        {
          prop: 'degree',
          label: '学历',
          width: 80,
          formatter: (row: StudentItem) => DEGREE_MAP[row.degree] || '-'
        },
        { prop: 'graduation_year', label: '毕业年份', width: 100 },
        {
          prop: 'employment_status',
          label: '就业状态',
          width: 100,
          formatter: (row: StudentItem) => {
            const config = EMPLOYMENT_STATUS_MAP[row.employment_status] || {
              type: 'info',
              text: '未知'
            }
            return h(ElTag, { type: config.type as any }, () => config.text)
          }
        },
        {
          prop: 'is_registered',
          label: '注册状态',
          width: 100,
          formatter: (row: StudentItem) =>
            h(ElTag, { type: row.is_registered ? 'success' : 'info', size: 'small' }, () =>
              row.is_registered ? '已注册' : '未注册'
            )
        },
        { prop: 'cur_company', label: '当前公司', minWidth: 150, show: false },
        { prop: 'cur_city', label: '当前城市', width: 100, show: false },
        {
          prop: 'operation',
          label: '操作',
          width: 120,
          fixed: 'right',
          formatter: (row: StudentItem, _col: any, _cell: any, $index: number) =>
            h('div', [h(ArtButtonTable, { type: 'view', onClick: () => handleViewByIndex($index) })])
        }
      ]
    }
  })

  const searchItems = computed(() => [
    {
      key: 'college',
      label: '学院',
      type: 'input' as const,
      props: { placeholder: '请输入学院', clearable: true }
    },
    {
      key: 'major',
      label: '专业',
      type: 'input' as const,
      props: { placeholder: '请输入专业', clearable: true }
    },
    {
      key: 'employment_status',
      label: '就业状态',
      type: 'select' as const,
      props: {
        placeholder: '请选择',
        options: Object.entries(EMPLOYMENT_STATUS_MAP).map(([value, config]) => ({
          label: config.text,
          value: Number(value)
        })),
        clearable: true
      }
    },
    {
      key: 'graduation_year',
      label: '届次',
      type: 'number' as const,
      props: { placeholder: '请输入毕业年份', min: 2000, max: 2100 }
    }
  ])

  const handleSearch = (params: Record<string, unknown>) => {
    replaceSearchParams(params)
    getData()
  }

  const handleReset = () => {
    resetSearchParams()
  }

  const handleSelectionChange = (selection: StudentItem[]) => {
    selectedRows.value = selection
  }

  const handleView = async (row: StudentItem) => {
    showDetailDialog.value = true
    detailLoading.value = true
    studentDetail.value = null
    try {
      const res = await fetchStudentDetail(row.profile_id)
      studentDetail.value = res.data ?? res
    } catch (e: any) {
      ElMessage.error(e.message || '获取学生详情失败')
      showDetailDialog.value = false
    } finally {
      detailLoading.value = false
    }
  }

  const handleViewByIndex = async (index: number) => {
    const row = data.value[index] as StudentItem | undefined
    if (!row) return
    showDetailDialog.value = true
    detailLoading.value = true
    studentDetail.value = null
    try {
      const res = await fetchStudentDetail(row.profile_id)
      studentDetail.value = res.data ?? res
    } catch (e: any) {
      ElMessage.error(e.message || '获取学生详情失败')
      showDetailDialog.value = false
    } finally {
      detailLoading.value = false
    }
  }

  const handleExport = async () => {
    try {
      ElMessage.info('正在导出，请稍候...')
      const params: Record<string, unknown> = {
        ...searchForm.value,
        page: undefined,
        page_size: undefined
      }
      // 如果有选中行，则导出选中学生；否则按搜索条件导出全部
      if (selectedRows.value.length > 0) {
        params.profile_ids = selectedRows.value.map((r) => r.profile_id)
      }
      const res = await exportSchoolStudents(params as any)
      // axios returns AxiosResponse, blob is in res.data
      const blob = res.data instanceof Blob
          ? res.data
          : new Blob([res.data], {
              type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      const timestamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15)
      link.download = `students_export_${timestamp}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    } catch (e: any) {
      ElMessage.error(e.message || '导出失败')
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning('请先选择要删除的学生')
      return
    }
    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedRows.value.length} 名学生吗？此操作不可恢复。`,
        '批量删除',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      const ids = selectedRows.value.map((r) => r.profile_id)
      await batchDeleteStudents(ids)
      ElMessage.success('删除成功')
      selectedRows.value = []
      refreshData()
    } catch (e: any) {
      if (e !== 'cancel') {
        ElMessage.error(e.message || '删除失败')
      }
    }
  }

  const handleFileChange = (file: any) => {
    importFile.value = file.raw
    importPreviewData.value = null
  }

  const handlePreview = async () => {
    if (!importFile.value) {
      ElMessage.warning('请先上传文件')
      return
    }
    previewLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', importFile.value)
      const res = await importStudentsPreview(formData)
      // HTTP utility returns res.data.data if nested (fallback: res.data = BaseResponse)
      // BaseResponse: {code, message, data: innerData}
      // innerData (preview success): {success, preview: [...], total, errors}
      // innerData (error): {success: 0, errors: [...]} — no preview/total
      const inner = res.data ?? res
      if (Array.isArray(inner.preview)) {
        importPreviewData.value = inner
      } else {
        // Error case: build a minimal preview object
        importPreviewData.value = {
          success: inner.success ?? 0,
          preview: [],
          total: 0,
          errors: inner.errors ?? []
        }
      }
      if (importPreviewData.value.errors?.length) {
        ElMessage.warning(`${importPreviewData.value.errors.length} 条数据存在格式问题，请检查`)
      }
    } catch (e: any) {
      ElMessage.error(e.message || '预览失败')
    } finally {
      previewLoading.value = false
    }
  }

  const handleConfirmImport = async () => {
    if (!importPreviewData.value?.preview) return
    importLoading.value = true
    try {
      // 取全部数据（不只是预览的50条）
      const res = await confirmImportStudents(importPreviewData.value.preview)
      ElMessage.success(`导入完成：成功 ${res.success} 条，跳过 ${res.skipped} 条`)
      showImportDialog.value = false
      cancelImport()
      refreshData()
    } catch (e: any) {
      ElMessage.error(e.message || '导入失败')
    } finally {
      importLoading.value = false
    }
  }

  const cancelImport = () => {
    showImportDialog.value = false
    importPreviewData.value = null
    importFile.value = null
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
  }
</script>

<style scoped>
  .page-school-students {
    padding: 20px;
  }
  .import-upload {
    width: 100%;
  }
  .text-xs {
    font-size: 12px;
  }
  .text-gray-500 {
    color: #909399;
  }
  .mb-4 {
    margin-bottom: 16px;
  }
  .mb-2 {
    margin-bottom: 8px;
  }
  .mt-4 {
    margin-top: 16px;
  }
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
