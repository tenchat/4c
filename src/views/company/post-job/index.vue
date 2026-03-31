<!-- 发布岗位页面 -->
<template>
  <div class="page-post-job art-full-height">
    <ElCard class="art-card-xs">
      <template #header>
        <span class="text-lg font-medium">{{ isEdit ? '编辑岗位' : '发布新岗位' }}</span>
      </template>

      <ArtForm
        ref="formRef"
        v-model="formData"
        :items="formItems"
        :rules="formRules"
        :labelWidth="labelWidth"
        :span="span"
        :gutter="20"
        :showReset="false"
        :showSubmit="false"
        @submit="handleSubmit"
        @reset="handleReset"
      >
        <template #keywords>
          <ElSelect
            v-model="formData.keywords"
            multiple
            filterable
            allow-create
            default-first-option
            :reserve-keyword="false"
            placeholder="输入技能后按回车添加"
            style="width: 100%"
          >
            <ElOption
              v-for="item in skillOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </ElSelect>
        </template>

        <template #description>
          <ElInput
            v-model="formData.description"
            type="textarea"
            :rows="6"
            placeholder="请详细描述岗位职责、要求、福利待遇等..."
            maxlength="2000"
            show-word-limit
          />
        </template>
      </ArtForm>

      <div class="mt-4 flex justify-end gap-3">
        <ElButton @click="handleSaveDraft" :loading="draftLoading">保存草稿</ElButton>
        <ElButton @click="handleReset">重置</ElButton>
        <ElButton type="primary" :loading="submitLoading" @click="handlePublish">
          {{ isEdit ? '保存修改' : '立即发布' }}
        </ElButton>
      </div>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { createJob, updateJob, getJob, type JobCreateParams } from '@/api/company'
  import { ElMessage } from 'element-plus'
  import { h } from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'

  defineOptions({ name: 'CompanyPostJob' })

  const route = useRoute()
  const router = useRouter()

  const isEdit = computed(() => !!route.query.id)
  const jobId = computed(() => route.query.id as string | undefined)

  const formRef = ref<FormInstance>()
  const submitLoading = ref(false)
  const draftLoading = ref(false)
  const labelWidth = '140px'
  const span = 12

  interface JobFormData {
    title: string
    city: string
    province: string
    industry: string
    min_salary: number | undefined
    max_salary: number | undefined
    min_degree: number | undefined
    min_exp_years: number | undefined
    keywords: string[]
    description: string
    validDays: number
  }

  const formData = ref<JobFormData>({
    title: '',
    city: '',
    province: '',
    industry: '',
    min_salary: undefined,
    max_salary: undefined,
    min_degree: undefined,
    min_exp_years: undefined,
    keywords: [],
    description: '',
    validDays: 30
  })

  const salaryRangeDisplay = computed(() => {
    const min = formData.value.min_salary
    const max = formData.value.max_salary
    if (!min && !max) return '面议'
    return `${min || 0}-${max || 0}元/月`
  })

  const formRules: FormRules = {
    title: [{ required: true, message: '请输入岗位名称', trigger: 'blur' }],
    city: [{ required: true, message: '请输入工作城市', trigger: 'blur' }],
    industry: [{ required: true, message: '请选择行业', trigger: 'change' }],
    min_salary: [{ required: true, message: '请输入最低薪资', trigger: 'blur' }],
    max_salary: [{ required: true, message: '请输入最高薪资', trigger: 'blur' }]
  }

  const INDUSTRY_OPTIONS = [
    { label: '互联网/IT', value: 'internet' },
    { label: '金融', value: 'finance' },
    { label: '教育', value: 'education' },
    { label: '制造业', value: 'manufacturing' },
    { label: '房地产', value: 'real_estate' },
    { label: '医疗健康', value: 'healthcare' },
    { label: '政府/事业单位', value: 'government' },
    { label: '其他', value: 'other' }
  ]

  const DEGREE_OPTIONS = [
    { label: '不限', value: 0 },
    { label: '高中/中专', value: 1 },
    { label: '大专', value: 2 },
    { label: '本科', value: 3 },
    { label: '硕士', value: 4 },
    { label: '博士', value: 5 }
  ]

  const EXP_OPTIONS = [
    { label: '不限', value: 0 },
    { label: '1年以下', value: 1 },
    { label: '1-3年', value: 3 },
    { label: '3-5年', value: 5 },
    { label: '5年以上', value: 10 }
  ]

  const skillOptions = [
    { label: 'JavaScript', value: 'JavaScript' },
    { label: 'TypeScript', value: 'TypeScript' },
    { label: 'Vue', value: 'Vue' },
    { label: 'React', value: 'React' },
    { label: 'Node.js', value: 'Node.js' },
    { label: 'Python', value: 'Python' },
    { label: 'Java', value: 'Java' },
    { label: 'Go', value: 'Go' },
    { label: 'SQL', value: 'SQL' },
    { label: 'MongoDB', value: 'MongoDB' },
    { label: 'Redis', value: 'Redis' },
    { label: 'Docker', value: 'Docker' },
    { label: 'Kubernetes', value: 'Kubernetes' },
    { label: 'AWS', value: 'AWS' },
    { label: 'Git', value: 'Git' }
  ]

  const VALID_DAYS_OPTIONS = [
    { label: '7天', value: 7 },
    { label: '14天', value: 14 },
    { label: '30天', value: 30 },
    { label: '60天', value: 60 },
    { label: '90天', value: 90 }
  ]

  const formItems = computed(() => [
    {
      key: 'title',
      label: '岗位名称',
      type: 'input' as const,
      span: 12,
      props: { placeholder: '请输入岗位名称', maxlength: 50, showWordLimit: true }
    },
    {
      key: 'city',
      label: '工作城市',
      type: 'input' as const,
      span: 12,
      props: { placeholder: '请输入工作城市' }
    },
    {
      key: 'province',
      label: '省份',
      type: 'input' as const,
      span: 12,
      props: { placeholder: '请输入省份' }
    },
    {
      key: 'industry',
      label: '行业',
      type: 'select' as const,
      span: 12,
      props: { placeholder: '请选择行业', options: INDUSTRY_OPTIONS }
    },
    {
      key: 'salary',
      label: '薪资范围',
      span: 24,
      render: () => h('span', { class: 'text-gray-600' }, salaryRangeDisplay.value)
    },
    {
      key: 'min_salary',
      label: '最低薪资(元/月)',
      type: 'number' as const,
      span: 12,
      props: { placeholder: '最低薪资', min: 0, step: 1000 }
    },
    {
      key: 'max_salary',
      label: '最高薪资(元/月)',
      type: 'number' as const,
      span: 12,
      props: { placeholder: '最高薪资', min: 0, step: 1000 }
    },
    {
      key: 'min_degree',
      label: '学历要求',
      type: 'select' as const,
      span: 12,
      props: { placeholder: '请选择学历要求', options: DEGREE_OPTIONS }
    },
    {
      key: 'min_exp_years',
      label: '工作经验',
      type: 'select' as const,
      span: 12,
      props: { placeholder: '请选择工作经验要求', options: EXP_OPTIONS }
    },
    {
      key: 'keywords',
      label: '技能关键词',
      span: 24,
      render: () => null
    },
    {
      key: 'description',
      label: '岗位描述',
      span: 24,
      render: () => null
    },
    {
      key: 'validDays',
      label: '有效期',
      type: 'select' as const,
      span: 12,
      props: { placeholder: '请选择有效期', options: VALID_DAYS_OPTIONS }
    }
  ])

  const handleSubmit = async () => {
    await handlePublish()
  }

  const handleSaveDraft = async () => {
    draftLoading.value = true
    try {
      await formRef.value?.validate()
      const params: JobCreateParams = {
        title: formData.value.title,
        city: formData.value.city,
        province: formData.value.province,
        industry: formData.value.industry,
        min_salary: formData.value.min_salary,
        max_salary: formData.value.max_salary,
        min_degree: formData.value.min_degree,
        min_exp_years: formData.value.min_exp_years,
        keywords: formData.value.keywords,
        description: formData.value.description
      }
      if (isEdit.value) {
        await updateJob(jobId.value!, params)
      } else {
        await createJob(params)
      }
      ElMessage.success('保存草稿成功')
      router.push('/company/jobs')
    } catch (error) {
      console.error('保存草稿失败:', error)
    } finally {
      draftLoading.value = false
    }
  }

  const handlePublish = async () => {
    try {
      await formRef.value?.validate()
      submitLoading.value = true
      const params: JobCreateParams = {
        title: formData.value.title,
        city: formData.value.city,
        province: formData.value.province,
        industry: formData.value.industry,
        min_salary: formData.value.min_salary,
        max_salary: formData.value.max_salary,
        min_degree: formData.value.min_degree,
        min_exp_years: formData.value.min_exp_years,
        keywords: formData.value.keywords,
        description: formData.value.description
      }
      // http utility returns res.data directly, so res is the response body
      // If it throws, error is caught below
      if (isEdit.value) {
        await updateJob(jobId.value!, params)
      } else {
        await createJob(params)
      }
      ElMessage.success(isEdit.value ? '修改成功' : '发布成功')
      router.push('/company/jobs')
    } catch (error) {
      // Error is already shown by http interceptor's showError
      console.error('操作失败:', error)
    } finally {
      submitLoading.value = false
    }
  }

  const handleReset = () => {
    formRef.value?.resetFields()
  }

  // 如果是编辑模式，加载岗位数据
  onMounted(async () => {
    if (isEdit.value && jobId.value) {
      try {
        const job = await getJob(jobId.value)
        formData.value = {
          title: job.title || '',
          city: job.city || '',
          province: job.province || '',
          industry: job.industry || '',
          min_salary: job.min_salary,
          max_salary: job.max_salary,
          min_degree: job.min_degree,
          min_exp_years: job.min_exp_years,
          keywords: job.keywords || [],
          description: job.description || '',
          validDays: 30
        }
      } catch {
        ElMessage.error('加载岗位详情失败')
        router.push('/company/jobs')
      }
    }
  })
</script>

<style scoped>
  .page-post-job {
    padding: 20px;
  }

  .skill-keywords-wrapper {
    width: 100%;
  }
</style>
