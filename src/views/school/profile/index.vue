<!-- 学校档案管理页面 -->
<template>
  <div class="page-school-profile art-full-height">
    <ElCard class="art-card-xs">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="text-lg font-medium">学校信息</span>
        </div>
      </template>

      <ArtForm
        ref="formRef"
        v-model="formData"
        :items="formItems"
        :rules="formRules"
        :labelWidth="labelWidth"
        :span="span"
        @submit="handleSubmit"
        @reset="handleReset"
      />
    </ElCard>

    <div class="mt-4 text-right">
      <ElSpace>
        <ElButton @click="handleReset">重置</ElButton>
        <ElButton type="primary" :loading="submitLoading" @click="handleSave">
          保存信息
        </ElButton>
      </ElSpace>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { fetchSchoolProfile, updateSchoolProfile } from '@/api/school'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'

  defineOptions({ name: 'SchoolProfile' })

  interface SchoolProfile {
    name: string
    province: string
    city: string
    type: string
  }

  const formRef = ref<FormInstance>()
  const submitLoading = ref(false)

  const labelWidth = '120px'
  const span = 12

  const formData = ref<SchoolProfile>({
    name: '',
    province: '',
    city: '',
    type: ''
  })

  const formRules: FormRules = {
    name: [{ required: true, message: '请输入学校名称', trigger: 'blur' }]
  }

  const UNIVERSITY_TYPE_OPTIONS = [
    { label: '综合', value: '综合' },
    { label: '理工', value: '理工' },
    { label: '师范', value: '师范' },
    { label: '农林', value: '农林' },
    { label: '医药', value: '医药' },
    { label: '财经', value: '财经' },
    { label: '政法', value: '政法' },
    { label: '体育', value: '体育' },
    { label: '艺术', value: '艺术' },
    { label: '民族', value: '民族' },
    { label: '军事', value: '军事' },
    { label: '其他', value: '其他' }
  ]

  const formItems = computed(() => [
    {
      key: 'name',
      label: '学校名称',
      type: 'input' as const,
      props: { placeholder: '请输入学校名称', clearable: true }
    },
    {
      key: 'province',
      label: '所在省份',
      type: 'input' as const,
      props: { placeholder: '请输入所在省份', clearable: true }
    },
    {
      key: 'city',
      label: '所在城市',
      type: 'input' as const,
      props: { placeholder: '请输入所在城市', clearable: true }
    },
    {
      key: 'type',
      label: '学校类型',
      type: 'select' as const,
      props: { placeholder: '请选择学校类型', options: UNIVERSITY_TYPE_OPTIONS }
    }
  ])

  const fetchProfile = async () => {
    try {
      const res: any = await fetchSchoolProfile()
      if (res) {
        Object.assign(formData.value, res)
      }
    } catch (error) {
      console.error('获取学校信息失败:', error)
    }
  }

  const handleSubmit = async (params: Record<string, unknown>) => {
    await formRef.value?.validate()
    await handleSave()
  }

  const handleSave = async () => {
    try {
      await formRef.value?.validate()
      submitLoading.value = true
      await updateSchoolProfile(formData.value)
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
  .page-school-profile {
    padding: 20px;
  }
</style>
