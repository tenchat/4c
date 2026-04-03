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
          @scroll="handleScroll"
        >
          <!-- 加载更多指示器 -->
          <div v-if="isLoadingMore" class="text-center py-2 text-xs text-g-400">
            加载更多...
          </div>

          <template v-for="(message, index) in messages" :key="index">
            <!-- 时间分隔符 -->
            <div
              v-if="message.timeSeparator && (index === 0 || messages[index - 1].timeSeparator !== message.timeSeparator)"
              class="flex items-center justify-center my-4 text-xs text-g-400"
            >
              <span class="px-2">{{ message.timeSeparator }}</span>
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
                <div class="mb-1 text-xs text-g-400">{{ message.time }}</div>
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
    time: string          // 显示用：当天 "HH:mm"，更早显示 ""
    fullTime: string       // ISO 时间戳，用于日期比较
    timeSeparator: string  // 时间分隔符文本，如 "昨天"、"4月2日"
    isMe: boolean
    avatar: string
  }

  // 常量定义
  const MOBILE_BREAKPOINT = 640
  const SCROLL_DELAY = 100
  const BOT_NAME = 'Art Bot'
  const SESSION_KEY = 'art_chat_session_id'
  const HISTORY_LIMIT = 30

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

  // 分页状态
  const historyOffset = ref(0)
  const hasMoreHistory = ref(true)
  const isLoadingMore = ref(false)

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

  // 工具函数
  const isSameDay = (d1: Date, d2: Date): boolean => {
    return (
      d1.getFullYear() === d2.getFullYear() &&
      d1.getMonth() === d2.getMonth() &&
      d1.getDate() === d2.getDate()
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

  const formatTimeSeparator = (dateStr: string): string => {
    const date = new Date(dateStr)
    if (isToday(date)) return ''
    if (isYesterday(date)) return '昨天'
    return `${date.getMonth() + 1}月${date.getDate()}日`
  }

  const formatMessageTime = (dateStr: string): string => {
    const date = new Date(dateStr)
    if (isToday(date)) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const formatCurrentTime = (): string => {
    return new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 初始化聊天消息数据
  const initializeMessages = (): ChatMessage[] => {
    const now = new Date()
    return [
      {
        id: 1,
        sender: BOT_NAME,
        content: '你好！我是你的AI助手，有什么我可以帮你的吗？',
        time: formatMessageTime(now.toISOString()),
        fullTime: now.toISOString(),
        timeSeparator: '',
        isMe: false,
        avatar: aiAvatar
      }
    ]
  }

  const messages = ref<ChatMessage[]>(initializeMessages())

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
  const loadChatHistory = async (append: boolean = false): Promise<void> => {
    try {
      const res = await getChatHistory(sessionId.value, undefined, append ? historyOffset.value : 0, HISTORY_LIMIT)
      if (res && res.messages) {
        const historyMessages: ChatMessage[] = res.messages.map((msg: any) => ({
          id: messageId.value++,
          sender: msg.type === 'user' ? currentUserId.value : BOT_NAME,
          content: msg.content,
          time: formatMessageTime(msg.created_at),
          fullTime: msg.created_at,
          timeSeparator: formatTimeSeparator(msg.created_at),
          isMe: msg.type === 'user',
          avatar: msg.type === 'user' ? meAvatar : aiAvatar
        }))

        if (append) {
          // 预加载更多 - 保留滚动位置
          const oldScrollHeight = messageContainer.value?.scrollHeight || 0
          messages.value = [...historyMessages, ...messages.value]
          historyOffset.value += historyMessages.length
          // 恢复滚动位置
          nextTick(() => {
            if (messageContainer.value) {
              messageContainer.value.scrollTop = messageContainer.value.scrollHeight - oldScrollHeight
            }
          })
        } else {
          messages.value = historyMessages
          scrollToBottom()
          historyOffset.value = historyMessages.length
        }

        hasMoreHistory.value = res.has_more ?? false
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
    const now = new Date()
    const userMessage: ChatMessage = {
      id: messageId.value++,
      sender: currentUserId.value,
      content: text,
      time: formatCurrentTime(),
      fullTime: now.toISOString(),
      timeSeparator: formatTimeSeparator(now.toISOString()),
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
      fullTime: now.toISOString(),
      timeSeparator: formatTimeSeparator(now.toISOString()),
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
  const openChat = (): void => {
    isDrawerVisible.value = true
    // 重置分页状态
    historyOffset.value = 0
    hasMoreHistory.value = true
    if (sessionId.value) {
      loadChatHistory()
    }
    scrollToBottom()
  }

  // 滚动加载更多历史
  const handleScroll = async (): Promise<void> => {
    if (!messageContainer.value || isLoadingMore.value || !hasMoreHistory.value) return

    const { scrollTop } = messageContainer.value

    // 当滚动到顶部附近时加载更多
    if (scrollTop < 100 && hasMoreHistory.value) {
      isLoadingMore.value = true
      await loadChatHistory(true)
      isLoadingMore.value = false
    }
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
