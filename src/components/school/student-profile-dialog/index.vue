<!-- 学生档案弹窗 -->
<template>
  <ElDialog
    :model-value="visible"
    title="学生档案详情"
    width="700px"
    @close="handleClose"
  >
    <div v-if="profileData" class="profile-content">
      <ElDescriptions :column="2" border>
        <ElDescriptionsItem label="学号">{{ profileData.student_no }}</ElDescriptionsItem>
        <ElDescriptionsItem label="姓名">{{ profileData.student_name || profileData.name }}</ElDescriptionsItem>
        <ElDescriptionsItem label="学院">{{ profileData.college }}</ElDescriptionsItem>
        <ElDescriptionsItem label="专业">{{ profileData.major }}</ElDescriptionsItem>
        <ElDescriptionsItem label="学历">
          {{ DEGREE_MAP[profileData.degree] || '未知' }}
        </ElDescriptionsItem>
        <ElDescriptionsItem label="生源省份">{{ profileData.province_origin || '-' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="GPA">{{ profileData.gpa || '-' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="期望城市">{{ profileData.desire_city || '-' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="期望薪资" :span="2">
          {{ profileData.desire_salary_min || '-' }} ~ {{ profileData.desire_salary_max || '-' }} 元/月
        </ElDescriptionsItem>
        <ElDescriptionsItem label="期望行业" :span="2">{{ profileData.desire_industry || '-' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="技能特长" :span="2">
          <ElTag v-for="skill in (profileData.skills || [])" :key="skill" size="small" class="mr-1">
            {{ skill }}
          </ElTag>
          <span v-if="!profileData.skills?.length" class="text-gray-400">暂无</span>
        </ElDescriptionsItem>
        <ElDescriptionsItem label="简历状态" :span="2">
          <ElTag :type="profileData.resume_url ? 'success' : 'info'" size="small">
            {{ profileData.resume_url ? '已上传' : '未上传' }}
          </ElTag>
        </ElDescriptionsItem>
        <ElDescriptionsItem label="档案完整度" :span="2">
          <ElProgress
            :percentage="profileData.profile_complete || 0"
            :color="progressColor"
            style="width: 200px"
          />
        </ElDescriptionsItem>
      </ElDescriptions>
    </div>
    <template #footer>
      <ElButton @click="handleClose">关闭</ElButton>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { fetchStudentProfileById } from '@/api/school'
  import { ElMessage } from 'element-plus'

  defineOptions({ name: 'StudentProfileDialog' })

  interface Props {
    modelValue: boolean
    profileId: string
  }

  const props = defineProps<Props>()
  const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
  }>()

  const visible = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  const profileData = ref<any>(null)

  const DEGREE_MAP: Record<number, string> = {
    1: '高中/中专',
    2: '大专',
    3: '本科',
    4: '硕士',
    5: '博士'
  }

  const progressColor = computed(() => {
    const pct = profileData.value?.profile_complete || 0
    if (pct < 30) return '#F56C6C'
    if (pct < 70) return '#E6A23C'
    return '#67C23A'
  })

  const handleClose = () => {
    visible.value = false
  }

  const loadProfile = async () => {
    if (!props.profileId) return
    try {
      const res: any = await fetchStudentProfileById(props.profileId)
      if (res?.data) {
        profileData.value = res.data
      } else if (res) {
        profileData.value = res
      }
    } catch (error) {
      console.error('获取学生档案失败:', error)
      ElMessage.error('获取学生档案失败')
    }
  }

  watch(
    () => [props.modelValue, props.profileId],
    ([isVisible, profileId]) => {
      if (isVisible && profileId) {
        loadProfile()
      }
    },
    { immediate: true }
  )
</script>

<style scoped>
  .profile-content {
    padding: 10px 0;
  }
</style>
