<!-- 学生档案管理页面 -->
<template>
  <div class="page-student-profile art-full-height">
    <ElRow :gutter="16">
      <!-- 左侧：个人信息表单 -->
      <ElCol :xs="24" :sm="24" :md="resumeText ? 12 : 24" class="mb-4">
        <ElCard class="art-card-xs">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="text-lg font-medium">个人信息</span>
              <ElProgress
                v-if="profileCompleteness > 0"
                :percentage="profileCompleteness"
                :color="progressColor"
                style="width: 200px"
              />
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
          >
            <template #skillTags>
              <div class="skill-tags-wrapper">
                <ElTag
                  v-for="tag in formData.skillTags"
                  :key="tag"
                  closable
                  :disableTransitions="false"
                  @close="handleCloseTag(tag)"
                >
                  {{ tag }}
                </ElTag>
                <ElInput
                  v-if="tagInputVisible"
                  ref="tagInputRef"
                  v-model="tagInputValue"
                  class="input-new-tag"
                  size="small"
                  @keyup.enter="handleInputConfirm"
                  @blur="handleInputConfirm"
                  placeholder="输入技能后回车"
                />
                <ElButton v-else class="button-new-tag" size="small" @click="showTagInput">
                  + 添加技能
                </ElButton>
              </div>
            </template>

            <template #resumeUpload>
              <ElUpload
                ref="uploadRef"
                class="resume-upload"
                :auto-upload="false"
                :limit="1"
                :file-list="resumeFileList"
                :on-change="handleResumeChange"
                :on-remove="handleResumeRemove"
                accept=".pdf,.doc,.docx,.txt"
              >
                <ElButton type="primary" :loading="resumeUploading">上传并解析</ElButton>
                <template #tip>
                  <div class="el-upload__tip">支持 PDF、Word、TXT 格式，大小不超过 10MB</div>
                </template>
              </ElUpload>
            </template>
          </ArtForm>
        </ElCard>

        <div class="mt-4 text-right">
          <ElSpace>
            <ElButton @click="handleReset">重置</ElButton>
            <ElButton type="primary" :loading="submitLoading" @click="handleSave">
              保存档案
            </ElButton>
          </ElSpace>
        </div>
      </ElCol>

      <!-- 右侧：简历文本预览（有内容时才显示） -->
      <ElCol v-if="resumeText" :xs="24" :sm="24" :md="12" class="mb-4">
        <ElCard class="art-card-xs resume-preview-card">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="text-lg font-medium">简历内容预览</span>
              <ElSpace>
                <ElButton size="small" @click="downloadResume">下载</ElButton>
                <ElButton size="small" @click="resumeText = ''">清空</ElButton>
              </ElSpace>
            </div>
          </template>
          <ElScrollbar height="500px">
            <ElInput
              v-model="resumeText"
              type="textarea"
              :rows="20"
              placeholder="简历文本将显示在这里..."
              readonly
            />
          </ElScrollbar>
        </ElCard>
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
  import { fetchStudentProfile, updateStudentProfile, uploadResume, getResumeText, deleteResume } from '@/api/student'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules, UploadFile, UploadRawFile } from 'element-plus'

  defineOptions({ name: 'StudentProfile' })

  interface StudentProfile {
    name: string
    studentId: string
    college: string
    major: string
    degree: number
    hometown: string
    gpa: number
    expectedCity: string
    expectedIndustry: string
    minSalary: number
    maxSalary: number
    skillTags: string[]
    resumeUrl?: string
  }

  const formRef = ref<FormInstance>()
  const submitLoading = ref(false)
  const profileCompleteness = ref(0)
  const tagInputVisible = ref(false)
  const tagInputValue = ref('')
  const tagInputRef = ref<HTMLInputElement>()
  const resumeFileList = ref<UploadFile[]>([])
  const resumeText = ref('')
  const resumeUploading = ref(false)
  const uploadRef = ref()

  const labelWidth = '120px'
  const span = 12

  const formData = ref<StudentProfile>({
    name: '',
    studentId: '',
    college: '',
    major: '',
    degree: 0,
    hometown: '',
    gpa: 0,
    expectedCity: '',
    expectedIndustry: '',
    minSalary: 0,
    maxSalary: 0,
    skillTags: []
  })

  const formRules: FormRules = {
    name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
    studentId: [{ required: true, message: '请输入学号', trigger: 'blur' }],
    college: [{ required: true, message: '请输入学院', trigger: 'blur' }],
    major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
    degree: [{ required: true, message: '请选择学历', trigger: 'change' }]
  }

  const DEGREE_OPTIONS = [
    { label: '高中/中专', value: 1 },
    { label: '大专', value: 2 },
    { label: '本科', value: 3 },
    { label: '硕士', value: 4 },
    { label: '博士', value: 5 }
  ]

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

  const formItems = computed(() => [
    {
      key: 'name',
      label: '姓名',
      type: 'input' as const,
      props: { placeholder: '请输入姓名', clearable: true }
    },
    {
      key: 'studentId',
      label: '学号',
      type: 'input' as const,
      props: { placeholder: '请输入学号', clearable: true }
    },
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
      key: 'degree',
      label: '学历',
      type: 'select' as const,
      props: { placeholder: '请选择学历', options: DEGREE_OPTIONS }
    },
    {
      key: 'hometown',
      label: '生源省份',
      type: 'input' as const,
      props: { placeholder: '请输入生源省份', clearable: true }
    },
    {
      key: 'gpa',
      label: 'GPA',
      type: 'number' as const,
      props: { placeholder: '请输入GPA', min: 0, max: 4, step: 0.1 }
    },
    {
      key: 'expectedCity',
      label: '期望城市',
      type: 'input' as const,
      span: 12,
      props: { placeholder: '请输入期望工作城市', clearable: true }
    },
    {
      key: 'minSalary',
      label: '期望薪资范围',
      type: 'number' as const,
      props: { placeholder: '最低薪资(元/月)', min: 0, step: 1000 }
    },
    {
      key: 'maxSalary',
      label: '~',
      type: 'number' as const,
      props: { placeholder: '最高薪资(元/月)', min: 0, step: 1000 }
    },
    {
      key: 'expectedIndustry',
      label: '期望行业',
      type: 'select' as const,
      span: 12,
      props: { placeholder: '请选择期望行业', options: INDUSTRY_OPTIONS }
    },
    {
      key: 'skillTags',
      label: '技能标签',
      span: 24,
      render: () => null
    },
    {
      key: 'resumeUpload',
      label: '简历上传',
      span: 24,
      render: () => null
    }
  ])

  const progressColor = computed(() => {
    if (profileCompleteness.value < 30) return '#F56C6C'
    if (profileCompleteness.value < 70) return '#E6A23C'
    return '#67C23A'
  })

  const showTagInput = () => {
    tagInputVisible.value = true
    nextTick(() => {
      tagInputRef.value?.focus()
    })
  }

  const handleInputConfirm = () => {
    if (tagInputValue.value) {
      if (!formData.value.skillTags.includes(tagInputValue.value)) {
        formData.value.skillTags.push(tagInputValue.value)
      }
    }
    tagInputVisible.value = false
    tagInputValue.value = ''
  }

  const handleCloseTag = (tag: string) => {
    formData.value.skillTags.splice(formData.value.skillTags.indexOf(tag), 1)
  }

  const handleResumeChange = async (file: UploadFile, fileList: UploadFile[]) => {
    resumeFileList.value = fileList.slice(-1)

    // 如果有文件，自动上传并解析
    const rawFile = file.raw
    if (rawFile) {
      await handleResumeUpload(rawFile)
    }
  }

  const handleResumeUpload = async (file: UploadRawFile) => {
    // 验证文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.error('文件超过 10MB 限制')
      resumeFileList.value = []
      return
    }

    // 验证文件类型
    const allowedTypes = ['.pdf', '.docx', '.doc', '.txt']
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!allowedTypes.includes(ext)) {
      ElMessage.error(`不支持的文件格式: ${ext}。支持的格式: ${allowedTypes.join(', ')}`)
      resumeFileList.value = []
      return
    }

    try {
      resumeUploading.value = true
      const res: any = await uploadResume(file)

      // uploadResume 返回的是 {file_path, file_name, text, char_count}
      if (res && res.text !== undefined) {
        resumeText.value = res.text || ''
        formData.value.resumeUrl = res.file_path
        ElMessage.success('简历上传并解析成功')
      } else {
        ElMessage.error('上传失败，未获取到解析结果')
        resumeFileList.value = []
      }
    } catch (error: any) {
      console.error('简历上传失败:', error)
      ElMessage.error(error?.message || '上传失败，请重试')
      resumeFileList.value = []
    } finally {
      resumeUploading.value = false
    }
  }

  const downloadResume = async () => {
    if (!formData.value.resumeUrl) return
    const baseUrl = import.meta.env.VITE_API_BASE_URL
    const { useUserStore } = await import('@/store/modules/user')
    const token = useUserStore().accessToken
    if (!token) return ElMessage.error('未登录')

    const fullUrl = `${baseUrl}/api/v1/student/resume/download?file_path=${encodeURIComponent(formData.value.resumeUrl)}`

    try {
      const res = await fetch(fullUrl, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('下载失败')
      const blob = await res.blob()
      const filename = formData.value.resumeUrl.split('/').pop() || 'resume'
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      URL.revokeObjectURL(url)
    } catch (e: any) {
      ElMessage.error(e.message || '下载失败')
    }
  }

  const handleResumeRemove = async () => {
    const filePath = formData.value.resumeUrl
    // 调用后端删除本地文件
    if (filePath) {
      try {
        await deleteResume(filePath)
      } catch (e) {
        console.error('删除简历文件失败:', e)
      }
    }
    resumeFileList.value = []
    resumeText.value = ''
    formData.value.resumeUrl = undefined
  }

  const fetchProfile = async () => {
    try {
      const res: any = await fetchStudentProfile()
      // HTTP 工具返回的是 res.data.data，所以直接检查 res 是否有数据
      if (res) {
        // 后端字段映射到前端字段
        formData.value = {
          name: res.real_name || res.name || '',
          studentId: res.student_no || '',
          college: res.college || '',
          major: res.major || '',
          degree: res.degree || 0,
          hometown: res.province_origin || '',
          gpa: res.gpa || 0,
          expectedCity: res.desire_city || '',
          expectedIndustry: res.desire_industry || '',
          minSalary: res.desire_salary_min || 0,
          maxSalary: res.desire_salary_max || 0,
          skillTags: res.skills || []
        }
        // 使用后端动态计算的完整度
        profileCompleteness.value = res.profile_complete || 0
        if (res.resume_url) {
          formData.value.resumeUrl = res.resume_url
          resumeFileList.value = [{ name: '简历', url: res.resume_url } as UploadFile]
          // 加载已保存简历的文本内容
          try {
            const textRes: any = await getResumeText(res.resume_url)
            if (textRes && textRes.text) {
              resumeText.value = textRes.text
            }
          } catch (e) {
            console.error('加载简历内容失败:', e)
          }
        }
      }
    } catch (error) {
      console.error('获取学生档案失败:', error)
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
      // 前端字段映射到后端字段
      const submitData = {
        real_name: formData.value.name,
        student_no: formData.value.studentId,
        college: formData.value.college,
        major: formData.value.major,
        degree: formData.value.degree,
        province_origin: formData.value.hometown,
        gpa: formData.value.gpa,
        desire_city: formData.value.expectedCity,
        desire_industry: formData.value.expectedIndustry,
        desire_salary_min: formData.value.minSalary,
        desire_salary_max: formData.value.maxSalary,
        skills: formData.value.skillTags,
        resume_url: formData.value.resumeUrl
      }
      await updateStudentProfile(submitData)
      // HTTP 拦截器已处理错误，如果执行到这里说明请求成功
      ElMessage.success('保存成功')
      // 保存成功后重新获取档案以获取最新的完整度
      fetchProfile()
    } catch (error) {
      console.error('保存失败:', error)
    } finally {
      submitLoading.value = false
    }
  }

  const handleReset = () => {
    formRef.value?.resetFields()
    resumeFileList.value = []
    resumeText.value = ''
  }

  onMounted(() => {
    fetchProfile()
  })
</script>

<style scoped>
  .page-student-profile {
    padding: 20px;
  }

  .skill-tags-wrapper {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }

  .input-new-tag {
    width: 120px;
  }

  .button-new-tag {
    height: 24px;
    line-height: 22px;
    padding-top: 0;
    padding-bottom: 0;
  }

  .resume-upload {
    text-align: left;
  }

  .resume-preview-card :deep(.el-card__body) {
    padding: 12px 16px;
  }
</style>
