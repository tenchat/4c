<!-- 学生档案管理页面 -->
<template>
  <div class="page-student-profile art-full-height">
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
          <div class="resume-section">
            <div class="resume-upload-row">
              <ElUpload
                ref="uploadRef"
                class="resume-upload"
                :auto-upload="false"
                :limit="1"
                :file-list="resumeFileList"
                :on-change="handleResumeChange"
                :on-remove="handleResumeRemove"
                accept=".pdf,.doc,.docx"
              >
                <ElButton type="primary">上传简历</ElButton>
                <template #tip>
                  <div class="el-upload__tip">支持 PDF、Word 格式文件，大小不超过 5MB</div>
                </template>
              </ElUpload>
              <ElButton v-if="resumeUrl" type="success" plain @click="handleDownloadResume">
                <ElIcon><Download /></ElIcon>
                下载简历
              </ElButton>
            </div>
            <!-- 简历文本预览 -->
            <div v-if="resumeText" class="resume-text-preview">
              <div class="resume-text-header">
                <ElIcon><Document /></ElIcon>
                <span>简历文本预览</span>
              </div>
              <div class="resume-text-content">{{ resumeText }}</div>
            </div>
          </div>
        </template>
      </ArtForm>
    </ElCard>

    <div class="mt-4 text-right">
      <ElSpace>
        <ElButton @click="handleReset">重置</ElButton>
        <ElButton type="primary" :loading="submitLoading" @click="handleSave">保存档案</ElButton>
      </ElSpace>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { fetchStudentProfile, updateStudentProfile, uploadResume, downloadResume } from '@/api/student'

  import { ElMessage } from 'element-plus'
  import { Download, Document } from '@element-plus/icons-vue'
  import type { FormInstance, FormRules, UploadFile } from 'element-plus'

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
  const uploadLoading = ref(false)
  const profileCompleteness = ref(0)
  const tagInputVisible = ref(false)
  const tagInputValue = ref('')
  const tagInputRef = ref<HTMLInputElement>()
  const resumeFileList = ref<UploadFile[]>([])
  const resumeUrl = ref('')
  const resumeText = ref('')

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
      props: { placeholder: '请输入期望工作城市', clearable: true }
    },
    {
      key: 'expectedIndustry',
      label: '期望行业',
      type: 'select' as const,
      span: 12,
      props: { placeholder: '请选择期望行业', options: INDUSTRY_OPTIONS }
    },
    {
      key: 'salaryRange',
      label: '期望薪资范围',
      span: 24
    },
    {
      key: 'minSalary',
      label: '最低薪资',
      type: 'number' as const,
      span: 6,
      props: { placeholder: '最低薪资(元/月)', min: 0 }
    },
    {
      key: 'maxSalary',
      label: '最高薪资',
      type: 'number' as const,
      span: 6,
      props: { placeholder: '最高薪资(元/月)', min: 0 }
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

    // Auto upload when file is selected
    if (file.raw) {
      await handleUploadResume(file.raw)
    }
  }

  const handleResumeRemove = () => {
    resumeFileList.value = []
    resumeUrl.value = ''
    resumeText.value = ''
  }

  const handleUploadResume = async (file: File) => {
    try {
      uploadLoading.value = true
      const res: any = await uploadResume(file)
      if (res.code === 200) {
        resumeUrl.value = res.data.resume_url
        resumeText.value = res.data.resume_text
        ElMessage.success('简历上传成功')
      }
    } catch (error) {
      console.error('上传简历失败:', error)
      ElMessage.error('上传简历失败')
    } finally {
      uploadLoading.value = false
    }
  }

  const handleDownloadResume = () => {
    if (resumeUrl.value) {
      window.open(downloadResume(resumeUrl.value), '_blank')
    }
  }

  const calculateCompleteness = (data: StudentProfile): number => {
    let filled = 0
    const total = 11

    if (data.name) filled++
    if (data.studentId) filled++
    if (data.college) filled++
    if (data.major) filled++
    if (data.degree !== undefined) filled++
    if (data.hometown) filled++
    if (data.gpa !== undefined) filled++
    if (data.expectedCity) filled++
    if (data.expectedIndustry) filled++
    if (data.minSalary !== undefined && data.maxSalary !== undefined) filled++
    if (data.skillTags.length > 0) filled++

    return Math.round((filled / total) * 100)
  }

  const fetchProfile = async () => {
    try {
      const res: any = await fetchStudentProfile()
      if (res) {
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
        profileCompleteness.value = calculateCompleteness(formData.value)
        if (res.resume_url) {
          resumeUrl.value = res.resume_url
          resumeText.value = res.resume_text || ''
          resumeFileList.value = [{ name: '简历', url: res.resume_url } as UploadFile]
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
        skills: formData.value.skillTags
      }
      await updateStudentProfile(submitData)
      ElMessage.success('保存成功')
      profileCompleteness.value = calculateCompleteness(formData.value)
    } catch (error) {
      console.error('保存失败:', error)
    } finally {
      submitLoading.value = false
    }
  }

  const handleReset = () => {
    formRef.value?.resetFields()
    resumeFileList.value = []
    resumeUrl.value = ''
    resumeText.value = ''
  }

  onMounted(() => {
    fetchProfile()
  })
</script>

<style scoped>
  .page-student-profile {
    padding: 20px;
    height: 100%;
    box-sizing: border-box;
    overflow-y: auto;
  }

  :deep(.el-card) {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  :deep(.el-card__body) {
    flex: 1;
    overflow-y: auto;
    max-height: none;
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

  .resume-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
    box-sizing: border-box;
  }

  .resume-upload-row {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .resume-text-preview {
    background: var(--el-fill-color-lighter);
    border: 1px solid var(--el-border-color-extra-light);
    border-radius: 8px;
    padding: 12px;
    width: 100%;
    box-sizing: border-box;
  }

  .resume-text-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-secondary);
  }

  .resume-text-content {
    font-size: 13px;
    line-height: 1.8;
    color: var(--el-text-color-regular);
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 500px;
    overflow-y: auto;
  }
</style>
