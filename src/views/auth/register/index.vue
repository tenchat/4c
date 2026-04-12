<template>
  <div class="flex w-full h-screen">
    <LoginLeftView />

    <div class="relative flex-1">
      <AuthTopBar />

      <div class="auth-right-wrap">
        <div class="form">
          <h3 class="title">大学生就业信息智能分析平台</h3>
          <p class="sub-title">注册您的账号</p>
          <ElForm
            class="mt-7.5"
            ref="formRef"
            :model="formData"
            :rules="rules"
            label-position="top"
            :key="formKey"
          >
            <ElFormItem prop="role">
              <ElSelect
                v-model="formData.role"
                placeholder="选择注册角色"
                class="w-full"
                @change="handleRoleChange"
              >
                <ElOption
                  v-for="item in roleOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                  <span>{{ item.label }}</span>
                </ElOption>
              </ElSelect>
            </ElFormItem>

            <!-- 学生专属：学号 -->
            <ElFormItem v-if="formData.role === 'student'" prop="student_no">
              <ElInput
                class="custom-height"
                v-model.trim="formData.student_no"
                placeholder="请输入学号"
              />
            </ElFormItem>

            <!-- 学生专属：姓名 -->
            <ElFormItem v-if="formData.role === 'student'" prop="real_name">
              <ElInput
                class="custom-height"
                v-model.trim="formData.real_name"
                placeholder="请输入真实姓名"
              />
            </ElFormItem>

            <!-- 企业专属：企业名称 -->
            <ElFormItem v-if="formData.role === 'company_admin'" prop="enterprise_name">
              <ElInput
                class="custom-height"
                v-model.trim="formData.enterprise_name"
                placeholder="请输入企业名称"
              />
            </ElFormItem>

            <!-- 学校管理员专属：注册码 -->
            <ElFormItem v-if="formData.role === 'school_admin'" prop="registration_code">
              <ElInput
                class="custom-height"
                v-model.trim="formData.registration_code"
                placeholder="请输入管理员注册码"
              />
            </ElFormItem>

            <!-- 共用：用户名 -->
            <ElFormItem prop="username">
              <ElInput
                class="custom-height"
                v-model.trim="formData.username"
                placeholder="请输入用户名（3-20位）"
              />
            </ElFormItem>

            <!-- 共用：密码 -->
            <ElFormItem prop="password">
              <ElInput
                class="custom-height"
                v-model.trim="formData.password"
                placeholder="请输入密码（至少6位）"
                type="password"
                autocomplete="off"
                show-password
              />
            </ElFormItem>

            <!-- 共用：确认密码 -->
            <ElFormItem prop="confirmPassword">
              <ElInput
                class="custom-height"
                v-model.trim="formData.confirmPassword"
                placeholder="请确认密码"
                type="password"
                autocomplete="off"
                @keyup.enter="handleRegister"
                show-password
              />
            </ElFormItem>

            <!-- 协议 -->
            <ElFormItem prop="agreement">
              <ElCheckbox v-model="formData.agreement">
                我已阅读并同意
                <a href="#" style="color: var(--theme-color)">《用户协议》</a>
                和
                <a href="#" style="color: var(--theme-color)">《隐私政策》</a>
              </ElCheckbox>
            </ElFormItem>

            <div style="margin-top: 15px">
              <ElButton
                class="w-full custom-height"
                type="primary"
                @click="handleRegister"
                :loading="loading"
                v-ripple
              >
                注册
              </ElButton>
            </div>

            <div class="mt-5 text-sm text-g-600">
              <span>已有账号？</span>
              <RouterLink class="text-theme" :to="{ name: 'Login' }">立即登录</RouterLink>
            </div>
          </ElForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { fetchRegister } from '@/api/auth'
  import { ElMessage, ElCheckbox, type FormInstance, type FormRules } from 'element-plus'

  defineOptions({ name: 'Register' })

  interface RegisterForm {
    role: 'student' | 'school_admin' | 'company_admin'
    student_no?: string
    real_name?: string
    enterprise_name?: string
    registration_code?: string
    username: string
    password: string
    confirmPassword: string
    agreement: boolean
  }

  const roleOptions = [
    { value: 'student', label: '学生' },
    { value: 'school_admin', label: '学校管理员' },
    { value: 'company_admin', label: '企业' }
  ]

  const router = useRouter()
  const formRef = ref<FormInstance>()

  const loading = ref(false)
  const formKey = ref(0)

  const formData = reactive<RegisterForm>({
    role: 'student',
    student_no: '',
    real_name: '',
    enterprise_name: '',
    registration_code: '',
    username: '',
    password: '',
    confirmPassword: '',
    agreement: false
  })

  const validateConfirmPassword = (
    _rule: any,
    value: string,
    callback: (error?: Error) => void
  ) => {
    if (!value) {
      callback(new Error('请确认密码'))
      return
    }
    if (value !== formData.password) {
      callback(new Error('两次输入的密码不一致'))
      return
    }
    callback()
  }

  const validateAgreement = (_rule: any, value: boolean, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error('请阅读并同意用户协议'))
      return
    }
    callback()
  }

  const rules = computed<FormRules<RegisterForm>>(() => {
    const r: FormRules<RegisterForm> = {
      role: [{ required: true, message: '请选择角色', trigger: 'change' }],
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度为3-20位', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码至少6位', trigger: 'blur' }
      ],
      confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
      agreement: [{ validator: validateAgreement, trigger: 'change' }]
    }

    // 学生：必填学号和姓名
    if (formData.role === 'student') {
      r.student_no = [{ required: true, message: '请输入学号', trigger: 'blur' }]
      r.real_name = [{ required: true, message: '请输入真实姓名', trigger: 'blur' }]
    }
    // 企业：必填企业名称
    if (formData.role === 'company_admin') {
      r.enterprise_name = [{ required: true, message: '请输入企业名称', trigger: 'blur' }]
    }
    // 学校管理员：必填注册码
    if (formData.role === 'school_admin') {
      r.registration_code = [{ required: true, message: '请输入注册码', trigger: 'blur' }]
    }

    return r
  })

  const handleRoleChange = () => {
    // 角色切换时清空相关字段
    formData.student_no = ''
    formData.real_name = ''
    formData.enterprise_name = ''
    formData.registration_code = ''
    formKey.value++
    nextTick(() => formRef.value?.clearValidate())
  }

  const handleRegister = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      loading.value = true

      const params: any = {
        username: formData.username,
        password: formData.password,
        role: formData.role
      }

      if (formData.role === 'student') {
        params.student_no = formData.student_no
        params.real_name = formData.real_name
      } else if (formData.role === 'company_admin') {
        params.enterprise_name = formData.enterprise_name
      } else if (formData.role === 'school_admin') {
        params.registration_code = formData.registration_code
      }

      const res: any = await fetchRegister(params)

      if (res && res.account_id) {
        ElMessage.success('注册成功！')
        if (formData.role === 'company_admin') {
          ElMessage.info('企业账号需要管理员审核，审核通过后可登录')
        } else if (formData.role === 'school_admin') {
          ElMessage.info('学校管理员账号需要审核，审核通过后可登录')
        }
        router.push({ name: 'Login' })
      } else {
        ElMessage.error('注册失败')
      }
    } catch (error: any) {
      ElMessage.error(error.message || '注册失败')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  @import '../login/style.css';
</style>
