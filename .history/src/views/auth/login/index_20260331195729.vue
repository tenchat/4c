<template>
  <div class="flex w-full h-screen">
    <LoginLeftView />

    <div class="relative flex-1">
      <AuthTopBar />

      <div class="auth-right-wrap">
        <div class="form">
          <h3 class="title">大学生就业信息智能分析平台</h3>
          <p class="sub-title">登录您的账号</p>
          <ElForm
            ref="formRef"
            :model="formData"
            :rules="rules"
            :key="formKey"
            @keyup.enter="handleSubmit"
            style="margin-top: 25px"
          >
            <ElFormItem prop="role">
              <ElSelect v-model="formData.role" @change="setupAccount" placeholder="选择角色" class="w-full">
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
            <ElFormItem prop="username">
              <ElInput
                class="custom-height"
                placeholder="请输入用户名"
                v-model.trim="formData.username"
              />
            </ElFormItem>
            <ElFormItem prop="password">
              <ElInput
                class="custom-height"
                placeholder="请输入密码"
                v-model.trim="formData.password"
                type="password"
                autocomplete="off"
                show-password
              />
            </ElFormItem>

            <!-- 推拽验证 -->
            <div class="relative pb-5 mt-6">
              <div
                class="relative z-[2] overflow-hidden select-none rounded-lg border border-transparent tad-300"
                :class="{ '!border-[#FF4E4F]': !isPassing && isClickPass }"
              >
                <ArtDragVerify
                  ref="dragVerify"
                  v-model:value="isPassing"
                  text="请拖动滑块验证"
                  textColor="var(--art-gray-700)"
                  successText="验证成功"
                  progressBarBg="var(--main-color)"
                  :background="isDark ? '#26272F' : '#F1F1F4'"
                  handlerBg="var(--default-box-color)"
                />
              </div>
              <p
                class="absolute top-0 z-[1] px-px mt-2 text-xs text-[#f56c6c] tad-300"
                :class="{ 'translate-y-10': !isPassing && isClickPass }"
              >
                请完成滑块验证
              </p>
            </div>

            <div class="flex-cb mt-2 text-sm">
              <ElCheckbox v-model="formData.rememberPassword">记住密码</ElCheckbox>
            </div>

            <div style="margin-top: 30px">
              <ElButton
                class="w-full custom-height"
                type="primary"
                @click="handleSubmit"
                :loading="loading"
                v-ripple
              >
                登录
              </ElButton>
            </div>

            <div class="mt-5 text-sm text-gray-600">
              <span>还没有账号？</span>
              <RouterLink class="text-theme" :to="{ name: 'Register' }">立即注册</RouterLink>
            </div>
          </ElForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { useUserStore } from '@/store/modules/user'
  import { fetchLogin } from '@/api/auth'
  import { ElNotification, type FormInstance, type FormRules } from 'element-plus'
  import { useSettingStore } from '@/store/modules/setting'

  defineOptions({ name: 'Login' })

  const settingStore = useSettingStore()
  const { isDark } = storeToRefs(settingStore)

  const formKey = ref(0)

  interface RoleOption {
    value: 'student' | 'school_admin' | 'company_admin' | 'system_admin'
    label: string
    username: string
    password: string
  }

  const roleOptions: RoleOption[] = [
    { value: 'student', label: '学生', username: 'student', password: '123456' },
    { value: 'school_admin', label: '学校管理员', username: 'school', password: '123456' },
    { value: 'company_admin', label: '企业', username: 'company', password: '123456' },
    { value: 'system_admin', label: '系统管理员', username: 'admin', password: 'Admin123!' }
  ]

  const dragVerify = ref()

  const userStore = useUserStore()
  const router = useRouter()
  const route = useRoute()
  const isPassing = ref(false)
  const isClickPass = ref(false)

  const formRef = ref<FormInstance>()

  const formData = reactive({
    role: 'student' as 'student' | 'school_admin' | 'company_admin' | 'system_admin',
    username: '',
    password: '',
    rememberPassword: true
  })

  const rules = computed<FormRules>(() => ({
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
  }))

  const loading = ref(false)

  onMounted(() => {
    setupAccount('student')
  })

  // 设置账号
  const setupAccount = (key: 'student' | 'school_admin' | 'company_admin' | 'system_admin') => {
    const selected = roleOptions.find(r => r.value === key)
    if (selected) {
      formData.username = selected.username
      formData.password = selected.password
    }
  }

  // 角色跳转映射
  const roleRedirectMap = {
    'student': '/student/dashboard',
    'school_admin': '/school/dashboard',
    'company_admin': '/company/dashboard',
    'system_admin': '/admin/dashboard'
  }

  // 登录
  const handleSubmit = async () => {
    if (!formRef.value) return

    try {
      const valid = await formRef.value.validate()
      if (!valid) return

      if (!isPassing.value) {
        isClickPass.value = true
        return
      }

      loading.value = true

      const { role, username, password } = formData

      const res: any = await fetchLogin({ role, username, password })

      if (!res.access_token) {
        throw new Error('登录失败')
      }

      const { access_token, refresh_token, user } = res

      // 存储 token 和用户信息
      userStore.setToken(access_token, refresh_token)
      userStore.setLoginStatus(true)
      userStore.setUserInfo(user)

      // 跳转到对应角色的 dashboard
      const redirect = roleRedirectMap[role as keyof typeof roleRedirectMap] || '/'
      router.push(redirect)

      ElNotification({
        title: '登录成功',
        type: 'success',
        duration: 2500,
        zIndex: 10000,
        message: `欢迎回来，${user.real_name || user.username}！`
      })
    } catch (error: any) {
      ElNotification({
        title: '登录失败',
        type: 'error',
        duration: 3000,
        zIndex: 10000,
        message: error.message || '请稍后重试'
      })
    } finally {
      loading.value = false
      resetDragVerify()
    }
  }

  // 重置拖拽验证
  const resetDragVerify = () => {
    dragVerify.value?.reset()
  }
</script>

<style scoped>
  @import './style.css';
</style>

<style lang="scss" scoped>
  :deep(.el-select__wrapper) {
    height: 40px !important;
  }
</style>
