<!-- 通用密码修改页面 -->
<template>
  <div class="page-password art-full-height">
    <ElCard class="art-card-xs">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="text-lg font-medium">修改密码</span>
        </div>
      </template>

      <ElForm
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        style="max-width: 500px"
      >
        <ElFormItem label="旧密码" prop="old_password">
          <ElInput
            v-model="formData.old_password"
            type="password"
            placeholder="请输入旧密码"
            show-password
            clearable
          />
        </ElFormItem>

        <ElFormItem label="新密码" prop="new_password">
          <ElInput
            v-model="formData.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
            clearable
          />
        </ElFormItem>

        <ElFormItem label="确认密码" prop="confirm_password">
          <ElInput
            v-model="formData.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
            clearable
          />
        </ElFormItem>

        <ElFormItem>
          <ElSpace>
            <ElButton @click="handleReset">重置</ElButton>
            <ElButton type="primary" :loading="loading" @click="handleSubmit">
              确认修改
            </ElButton>
          </ElSpace>
        </ElFormItem>
      </ElForm>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchChangePassword } from '@/api/auth'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'

  defineOptions({ name: 'PasswordChange' })

  const router = useRouter()
  const formRef = ref<FormInstance>()
  const loading = ref(false)

  const formData = reactive({
    old_password: '',
    new_password: '',
    confirm_password: ''
  })

  // 密码复杂度验证
  const validatePassword = (_rule: any, value: string, callback: any) => {
    if (value.length < 6) {
      callback(new Error('密码长度不能少于6位'))
    } else if (!/[a-zA-Z]/.test(value) || !/[0-9]/.test(value)) {
      callback(new Error('密码必须包含字母和数字'))
    } else {
      callback()
    }
  }

  // 确认密码验证
  const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
    if (value !== formData.new_password) {
      callback(new Error('两次输入的密码不一致'))
    } else {
      callback()
    }
  }

  const formRules: FormRules = {
    old_password: [
      { required: true, message: '请输入旧密码', trigger: 'blur' }
    ],
    new_password: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { validator: validatePassword, trigger: 'blur' }
    ],
    confirm_password: [
      { required: true, message: '请再次输入新密码', trigger: 'blur' },
      { validator: validateConfirmPassword, trigger: 'blur' }
    ]
  }

  // 重置表单
  const handleReset = () => {
    formRef.value?.resetFields()
  }

  // 提交修改
  const handleSubmit = async () => {
    if (!formRef.value) return

    try {
      const valid = await formRef.value.validate()
      if (!valid) return

      loading.value = true

      await fetchChangePassword({
        old_password: formData.old_password,
        new_password: formData.new_password
      })

      ElMessage.success('密码修改成功')

      // 清除登录状态，跳转到登录页
      handleReset()

      setTimeout(() => {
        router.push('/auth/login')
      }, 1500)
    } catch (error: any) {
      ElMessage.error(error.message || '密码修改失败')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .page-password {
    padding: 16px;
  }
</style>
