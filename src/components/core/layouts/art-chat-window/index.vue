<!-- 系统聊天窗口 -->
<template>
  <div>
    <ElDrawer v-model="isDrawerVisible" :size="isMobile ? '100%' : '480px'" :with-header="false">
      <div class="mb-5 flex-cb">
        <div>
          <span class="text-base font-medium">Art Bot</span>
          <div class="mt-1.5 flex-c gap-1">
            <div
              class="h-2 w-2 rounded-full"
              :class="isOnline ? 'bg-success/100' : 'bg-danger/100'"
            ></div>
            <span class="text-xs text-g-600">{{ isOnline ? '在线' : '离线' }}</span>
          </div>
        </div>
        <div>
          <ElIcon class="c-p" :size="20" @click="closeChat">
            <Close />
          </ElIcon>
        </div>
      </div>
      <div class="flex h-[calc(100%-70px)] flex-col">
        <!-- 聊天消息区域 -->
        <div
          class="flex-1 overflow-y-auto border-t-d px-4 py-7.5 [&::-webkit-scrollbar]:!w-1"
          ref="messageContainer"
        >
          <template v-for="(message, index) in messages" :key="index">
            <!-- 时间分隔线 -->
            <div
              v-if="message.timeSeparator"
              class="my-4 flex items-center gap-2"
            >
              <div class="h-px flex-1 bg-g-200"></div>
              <span class="text-xs text-g-500">{{ message.timeSeparator }}</span>
              <div class="h-px flex-1 bg-g-200"></div>
            </div>
            <div
              :class="[
                'mb-7.5 flex w-full items-start gap-2',
                message.isMe ? 'flex-row-reverse' : 'flex-row'
              ]"
            >
              <ElAvatar :size="32" :src="message.avatar" class="shrink-0" />
              <div
                :class="['flex max-w-[70%] flex-col', message.isMe ? 'items-end' : 'items-start']"
              >
                <div
                  :class="[
                    'mb-1 flex gap-2 text-xs',
                    message.isMe ? 'flex-row-reverse' : 'flex-row'
                  ]"
                >
                  <span class="font-medium">{{ message.sender }}</span>
                  <span class="text-g-600">{{ message.time }}</span>
                </div>
                <div
                  :class="[
                    'rounded-md px-3.5 py-2.5 text-sm leading-[1.4] text-g-900',
                    message.isMe ? 'message-right bg-theme/15' : 'message-left bg-g-300/50'
                  ]"
                  >{{ message.content }}</div
                >
              </div>
            </div>
          </template>
        </div>

        <!-- 聊天输入区域 -->
        <div class="px-4 pt-4">
          <ElInput
            v-model="messageText"
            type="textarea"
            :rows="3"
            placeholder="输入消息"
            resize="none"
            :disabled="isLoading"
            @keyup.enter.prevent="sendMessage"
          >
            <template #append>
              <div class="flex gap-2 py-2">
                <ElUpload
                  :auto-upload="false"
                  :show-file-list="false"
                  accept=".txt,.pdf,.docx,.doc"
                  @change="handleFileUpload"
                >
                  <template #trigger>
                    <ElButton :icon="Paperclip" circle plain :loading="uploadLoading" />
                  </template>
                </ElUpload>
                <ElButton :icon="Picture" circle plain />
                <ElButton type="primary" @click="sendMessage" :disabled="isLoading" v-ripple
                  >发送</ElButton
                >
              </div>
            </template>
          </ElInput>
          <div class="mt-3 flex-cb">
            <div class="flex-c">
              <ArtSvgIcon icon="ri:image-line" class="mr-5 c-p text-g-600 text-lg" />
              <ArtSvgIcon icon="ri:emotion-happy-line" class="mr-5 c-p text-g-600 text-lg" />
            </div>
            <ElButton
              type="primary"
              @click="sendMessage"
              :disabled="isLoading"
              v-ripple
              class="min-w-20"
              >发送</ElButton
            >
          </div>
        </div>
      </div>
    </ElDrawer>
  </div>
</template>

<script setup lang="ts">
  import { Picture, Paperclip, Close } from '@element-plus/icons-vue'
  import { ElMessage } from 'element-plus'
  import { UploadFile } from 'element-plus'
  import { mittBus } from '@/utils/sys'
  import meAvatar from '@/assets/images/avatar/avatar5.webp'
  import aiAvatar from '@/assets/images/avatar/avatar10.webp'
  import { aiQAStream, getChatHistory, uploadKnowledge } from '@/api/ai'
  import { useUserStore } from '@/store/modules/user'

  defineOptions({ name: 'ArtChatWindow' })

  // 类型定义
  interface ChatMessage {
    id: number
    sender: string
    content: string
    time: string
    fullTime?: string
    timeSeparator?: string
    isMe: boolean
    avatar: string
  }

  // 常量定义
  const MOBILE_BREAKPOINT = 640
  const SCROLL_DELAY = 100
  const BOT_NAME = 'Art Bot'
  const SESSION_KEY = 'art_chat_session_id'

  // 响应式布局
  const { width } = useWindowSize()
  const isMobile = computed(() => width.value < MOBILE_BREAKPOINT)

  // 组件状态
  const isDrawerVisible = ref(false)
  const isOnline = ref(true)

  // 消息相关状态
  const messageText = ref('')
  const messageId = ref(10)
  const messageContainer = ref<HTMLElement | null>(null)
  const isLoading = ref(false)
  const uploadLoading = ref(false)

  // AI 相关状态
  const sessionId = ref<string>(localStorage.getItem(SESSION_KEY) || '')
  const userStore = useUserStore()

  // 将后端角色映射到 RAG 角色
  const roleMap: Record<string, string> = {
    student: 'student',
    school_admin: 'school',
    company_admin: 'company',
    system_admin: 'school'
  }

  const roleType = computed(() => {
    const roles = userStore.info.roles || []
    const backendRole = roles[0] || 'student'
    return roleMap[backendRole] || 'student'
  })

  // 用户ID（用于区分不同用户的聊天历史）
  const currentUserId = computed(() => String(userStore.info.userId || 'anonymous'))

  // 初始化聊天消息数据
  const initializeMessages = (): ChatMessage[] => [
    {
      id: 1,
      sender: BOT_NAME,
      content: '你好！我是你的AI助手，有什么我可以帮你的吗？',
      time: '10:00',
      isMe: false,
      avatar: aiAvatar
    }
  ]

  const messages = ref<ChatMessage[]>(initializeMessages())

  // 工具函数
  const formatCurrentTime = (): string => {
    return new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 日期判断工具函数
  const isSameDay = (date1: Date, date2: Date): boolean => {
    return (
      date1.getFullYear() === date2.getFullYear() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getDate() === date2.getDate()
    )
  }

  const isToday = (date: Date): boolean => {
    return isSameDay(date, new Date())
  }

  const isYesterday = (date: Date): boolean => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    return isSameDay(date, yesterday)
  }

  // 格式化时间分隔符
  const formatTimeSeparator = (dateStr: string): string => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    if (isToday(date)) return ''
    if (isYesterday(date)) return '昨天'
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}月${day}日`
  }

  // 格式化消息时间
  const formatMessageTime = (dateStr: string): string => {
    if (!dateStr) return formatCurrentTime()
    const date = new Date(dateStr)
    if (isToday(date)) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    const month = date.getMonth() + 1
    const day = date.getDate()
    const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    return `${month}月${day}日 ${time}`
  }

  const scrollToBottom = (): void => {
    nextTick(() => {
      setTimeout(() => {
        if (messageContainer.value) {
          messageContainer.value.scrollTop = messageContainer.value.scrollHeight
        }
      }, SCROLL_DELAY)
    })
  }

  // 加载聊天历史
  const loadChatHistory = async (): Promise<void> => {
    try {
      const res = await getChatHistory(sessionId.value)
      // HTTP 工具已解包，res 格式为 {session_id, messages, has_more}
      if (res && res.messages && res.messages.length > 0) {
        // 将历史消息转换为 UI 格式
        let lastDate = ''
        const historyMessages: ChatMessage[] = res.messages.map((msg: any) => {
          const separator = formatTimeSeparator(msg.created_at)
          const time = formatMessageTime(msg.created_at)
          lastDate = separator || lastDate
          return {
            id: messageId.value++,
            sender: msg.type === 'user' ? currentUserId.value : BOT_NAME,
            content: msg.content,
            time: time,
            fullTime: msg.created_at,
            timeSeparator: separator !== lastDate ? separator : '',
            isMe: msg.type === 'user',
            avatar: msg.type === 'user' ? meAvatar : aiAvatar
          }
        })
        messages.value = historyMessages
        scrollToBottom()
      }
    } catch (_error) {
      console.error('Failed to load chat history:', _error)
    }
  }

  // 发送消息
  const sendMessage = async (): Promise<void> => {
    const text = messageText.value.trim()
    if (!text || isLoading.value) return

    // 添加用户消息
    const userMessage: ChatMessage = {
      id: messageId.value++,
      sender: currentUserId.value,
      content: text,
      time: formatCurrentTime(),
      isMe: true,
      avatar: meAvatar
    }
    messages.value.push(userMessage)
    messageText.value = ''
    scrollToBottom()

    // 开始 AI 流式响应
    isLoading.value = true

    // 添加 AI 消息占位
    const aiMessage: ChatMessage = {
      id: messageId.value++,
      sender: BOT_NAME,
      content: '',
      time: formatCurrentTime(),
      isMe: false,
      avatar: aiAvatar
    }
    messages.value.push(aiMessage)
    const aiMessageIndex = messages.value.length - 1

    try {
      await aiQAStream(
        {
          question: text,
          user_id: currentUserId.value,
          role_type: roleType.value,
          session_id: sessionId.value || undefined
        },
        (content) => {
          // 更新 AI 消息内容（流式）
          messages.value[aiMessageIndex].content += content
          scrollToBottom()
        },
        (error) => {
          messages.value[aiMessageIndex].content = `抱歉，发生了错误: ${error}`
          scrollToBottom()
        },
        (newSessionId) => {
          // 保存 session_id 到本地
          sessionId.value = newSessionId
          localStorage.setItem(SESSION_KEY, newSessionId)
        }
      )
    } finally {
      isLoading.value = false
      scrollToBottom()
    }
  }

  // 文件上传处理
  const handleFileUpload = async (uploadFile: UploadFile): Promise<void> => {
    if (!uploadFile.raw) return

    const title = prompt('请输入文档标题：', uploadFile.name || '未命名文档')
    if (!title) return

    try {
      uploadLoading.value = true
      await uploadKnowledge(uploadFile.raw, title, roleType.value)
      ElMessage.success('上传成功，AI 已可以基于此文档回答问题')
    } catch {
      ElMessage.error('上传失败，请重试')
    } finally {
      uploadLoading.value = false
    }
  }

  // 聊天窗口控制方法
  const LAST_CHAT_DATE_KEY = 'art_chat_last_date'

  const checkAndGreetIfNewDay = (): void => {
    const today = new Date()
    const todayStr = today.toDateString()

    // 检查最后一条消息是否是今天的
    const lastMessage = messages.value[messages.value.length - 1]
    let lastMessageDate: Date | null = null

    if (lastMessage?.fullTime) {
      lastMessageDate = new Date(lastMessage.fullTime)
    }

    // 如果有最后消息且是今天的，不需要打招呼
    if (lastMessageDate && isToday(lastMessageDate)) {
      localStorage.setItem(LAST_CHAT_DATE_KEY, todayStr)
      return
    }

    // 如果没有消息，或者最后消息不是今天的，且是跨天了
    const lastDate = localStorage.getItem(LAST_CHAT_DATE_KEY)
    if (lastDate && lastDate !== todayStr) {
      // 新的一天，打开聊天框时 AI 主动打招呼
      const hour = today.getHours()
      let greeting = ''
      if (hour < 12) {
        greeting = '早上好！新的一天开始了，有什么我可以帮你的吗？'
      } else if (hour < 18) {
        greeting = '下午好！有什么我可以帮你的吗？'
      } else {
        greeting = '晚上好！新的一天有什么我可以帮你的吗？'
      }

      const greetingMessage: ChatMessage = {
        id: messageId.value++,
        sender: BOT_NAME,
        content: greeting,
        time: formatCurrentTime(),
        isMe: false,
        avatar: aiAvatar
      }
      messages.value.unshift(greetingMessage)
      nextTick(() => scrollToBottom())
    }

    // 更新最后聊天日期
    localStorage.setItem(LAST_CHAT_DATE_KEY, todayStr)
  }

  const openChat = async (): Promise<void> => {
    isDrawerVisible.value = true
    if (sessionId.value) {
      await loadChatHistory()
      checkAndGreetIfNewDay()
    } else {
      // 没有 sessionId 时也检查是否新的一天
      checkAndGreetIfNewDay()
    }
    scrollToBottom()
  }

  const closeChat = (): void => {
    isDrawerVisible.value = false
  }

  // 生命周期
  onMounted(() => {
    scrollToBottom()
    mittBus.on('openChat', openChat)
  })

  onUnmounted(() => {
    mittBus.off('openChat', openChat)
  })
</script>
