<!-- 系统设置页面 -->
<template>
  <div class="page-admin-settings art-full-height">
    <ElCard class="art-card-xs">
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
        </div>
      </template>

      <ElForm
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="200px"
        class="settings-form"
      >
        <ElFormItem label="学校管理员注册码" prop="school_admin_code">
          <ElInput
            v-model="formData.school_admin_code"
            placeholder="请输入学校管理员注册码"
            class="settings-input"
          />
          <div class="form-tip">
            用于学校管理员注册时的校验，请妥善保管
          </div>
        </ElFormItem>

        <ElFormItem>
          <ElButton type="primary" @click="handleSave" :loading="saving">
            保存设置
          </ElButton>
        </ElFormItem>
      </ElForm>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchConfigs, updateConfig } from '@/api/admin'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'

  defineOptions({ name: 'AdminSettings' })

  interface ConfigItem {
    config_key: string
    config_value: string
    description?: string
    updated_at?: string
  }

  const formRef = ref<FormInstance>()
  const saving = ref(false)

  const formData = reactive({
    school_admin_code: ''
  })

  const rules = computed<FormRules>(() => ({
    school_admin_code: [
      { required: true, message: '请输入学校管理员注册码', trigger: 'blur' },
      { min: 6, message: '注册码至少6位', trigger: 'blur' }
    ]
  }))

  // 加载配置
  const loadConfigs = async () => {
    try {
      const res: any = await fetchConfigs()
      const configs: ConfigItem[] = res.data ?? res ?? []
      const schoolAdminConfig = configs.find(
        (c: ConfigItem) => c.config_key === 'SCHOOL_ADMIN_REGISTRATION_CODE'
      )
      if (schoolAdminConfig) {
        formData.school_admin_code = schoolAdminConfig.config_value
      }
    } catch (e: any) {
      ElMessage.error(e.message || '加载配置失败')
    }
  }

  // 保存配置
  const handleSave = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      saving.value = true
      await updateConfig('SCHOOL_ADMIN_REGISTRATION_CODE', formData.school_admin_code, '学校管理员注册码')
      ElMessage.success('保存成功')
    } catch (e: any) {
      if (e !== false) {
        // validate 返回 false 时不弹错误提示
        ElMessage.error(e.message || '保存失败')
      }
    } finally {
      saving.value = false
    }
  }

  onMounted(() => {
    loadConfigs()
  })
</script>

<style scoped>
  .page-admin-settings {
    padding: 20px;
  }

  .card-header {
    font-size: 16px;
    font-weight: 500;
  }

  .settings-form {
    max-width: 600px;
  }

  .settings-input {
    max-width: 400px;
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.4;
  }
</style>
