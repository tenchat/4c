<!-- 企业档案管理页面 -->
<template>
  <div class="page-company-profile art-full-height">
    <ElCard class="art-card-xs">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="text-lg font-medium">企业信息</span>
          <ElTag v-if="formData.verified" type="success">已认证</ElTag>
          <ElTag v-else type="warning">未认证</ElTag>
        </div>
      </template>

      <ArtForm
        ref="formRef"
        v-model="formData"
        :items="formItems"
        :rules="formRules"
        :labelWidth="labelWidth"
        :span="span"
        :showReset="false"
        :showSubmit="false"
        @submit="handleSubmit"
        @reset="handleReset"
      />
    </ElCard>

    <div class="mt-4 text-right">
      <ElSpace>
        <ElButton @click="handleReset">重置</ElButton>
        <ElButton type="primary" :loading="submitLoading" @click="handleSave">保存信息</ElButton>
      </ElSpace>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { fetchCompanyProfile, updateCompanyProfile } from '@/api/company'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'

  defineOptions({ name: 'CompanyProfile' })

  interface CompanyProfile {
    company_name: string
    industry: string
    city: string
    size: string
    description: string
    verified: boolean
  }

  const formRef = ref<FormInstance>()
  const submitLoading = ref(false)

  const labelWidth = '120px'
  const span = 12

  const formData = ref<CompanyProfile>({
    company_name: '',
    industry: '',
    city: '',
    size: '',
    description: '',
    verified: false
  })

  const formRules: FormRules = {
    company_name: [{ required: true, message: '请输入企业名称', trigger: 'blur' }]
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

  const COMPANY_SIZE_OPTIONS = [
    { label: '50人以下', value: '50人以下' },
    { label: '50-200人', value: '50-200人' },
    { label: '200-500人', value: '200-500人' },
    { label: '500-1000人', value: '500-1000人' },
    { label: '1000-5000人', value: '1000-5000人' },
    { label: '5000人以上', value: '5000人以上' }
  ]

  const formItems = computed(() => [
    {
      key: 'company_name',
      label: '企业名称',
      type: 'input' as const,
      props: { placeholder: '请输入企业名称', clearable: true }
    },
    {
      key: 'industry',
      label: '所属行业',
      type: 'select' as const,
      props: { placeholder: '请选择所属行业', options: INDUSTRY_OPTIONS }
    },
    {
      key: 'city',
      label: '所在城市',
      type: 'input' as const,
      props: { placeholder: '请输入所在城市', clearable: true }
    },
    {
      key: 'size',
      label: '企业规模',
      type: 'select' as const,
      props: { placeholder: '请选择企业规模', options: COMPANY_SIZE_OPTIONS }
    },
    {
      key: 'description',
      label: '企业简介',
      type: 'textarea' as const,
      span: 24,
      props: {
        placeholder: '请输入企业简介',
        rows: 4,
        maxlength: 500,
        showWordLimit: true
      }
    }
  ])

  const fetchProfile = async () => {
    try {
      const res: any = await fetchCompanyProfile()
      if (res) {
        Object.assign(formData.value, res)
      }
    } catch (error) {
      console.error('获取企业信息失败:', error)
    }
  }

  const handleSubmit = async () => {
    await formRef.value?.validate()
    await handleSave()
  }

  const handleSave = async () => {
    try {
      await formRef.value?.validate()
      submitLoading.value = true
      // 不提交 verified 字段（只读）
      await updateCompanyProfile({
        company_name: formData.value.company_name,
        industry: formData.value.industry,
        city: formData.value.city,
        size: formData.value.size,
        description: formData.value.description
      })
      ElMessage.success('保存成功')
    } catch (error) {
      console.error('保存失败:', error)
    } finally {
      submitLoading.value = false
    }
  }

  const handleReset = () => {
    formRef.value?.resetFields()
    fetchProfile()
  }

  onMounted(() => {
    fetchProfile()
  })
</script>

<style scoped>
  .page-company-profile {
    padding: 20px;
  }
</style>
