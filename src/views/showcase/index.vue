<template>
  <div class="showcase-page">
    <!-- Navigation -->
    <nav class="nav">
      <div class="nav-brand">
        <img src="/icon2.svg" alt="logo" class="nav-logo" />
        <span class="nav-title">大学生就业信息智能分析平台</span>
      </div>
      <div class="nav-links">
        <a class="nav-link" @click="scrollTo('roles')">目标用户</a>
        <a class="nav-link" @click="scrollTo('features')">核心功能</a>
        <a class="nav-link" @click="scrollTo('architecture')">技术架构</a>
        <a class="nav-link" @click="scrollTo('team')">关于我们</a>
      </div>
    </nav>

    <!-- Hero + Roles Background (shared) -->
    <div class="hero-bg">
      <div
        v-for="(img, index) in bgImages"
        :key="img"
        class="hero-bg-slide"
        :class="{ active: index === currentBgIndex }"
        :style="{ backgroundImage: `url(${img})` }"
      ></div>
      <div class="hero-bg-overlay-base"></div>
    </div>

    <!-- Hero Section -->
    <section class="hero">
      <!-- Content -->
      <div class="hero-content">
        <div class="hero-badge">
          <el-icon><Box /></el-icon>
          以数据驱动就业决策，用 AI 赋能职业规划
        </div>
        <h1>
          <img src="/icon.svg" alt="职引未来" class="hero-title-img" />大学生就业信息智能分析平台
        </h1>
        <p
          >整合校内毕业生数据、社会招聘数据与国家宏观就业数据，构建面向高校的就业全链路智能分析系统，为学生、辅导员/就业办、企业三类用户提供差异化服务。</p
        >
        <div class="hero-buttons">
          <el-button type="primary" @click="goLogin">
            <el-icon><ArrowRight /></el-icon>
            开始使用
          </el-button>
          <el-button @click="scrollTo('features')">
            <el-icon><VideoPlay /></el-icon>
            了解更多
          </el-button>
        </div>
      </div>
    </section>

    <!-- User Roles Section -->
    <section class="section roles-section" id="roles">
      <div class="container">
        <div class="section-header">
          <div class="section-title">
            <el-icon><User /></el-icon>
            <h2>目标用户</h2>
          </div>
          <p class="section-subtitle">为三类核心用户提供差异化服务</p>
        </div>

        <div class="roles-grid">
          <div class="role-card">
            <div class="role-icon blue">
              <el-icon><Reading /></el-icon>
            </div>
            <h4>在校学生</h4>
            <p>了解自己的就业竞争力，获取个性化职业发展建议和精准岗位推荐</p>
          </div>

          <div class="role-card">
            <div class="role-icon cyan">
              <el-icon><UserFilled /></el-icon>
            </div>
            <h4>辅导员 / 就业办</h4>
            <p>掌握全院学生就业动态，提前识别就业困难群体，生成定向辅导建议</p>
          </div>

          <div class="role-card">
            <div class="role-icon green">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <h4>企业</h4>
            <p>发布招聘信息，对接高校人才，精准匹配合适的毕业生候选人</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="section bg-light" id="features">
      <div class="container">
        <div class="section-header">
          <div class="section-title">
            <el-icon><Grid /></el-icon>
            <h2>核心功能模块</h2>
          </div>
          <p class="section-subtitle">覆盖就业全链路的智能化功能</p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon blue">
              <el-icon><Plus /></el-icon>
            </div>
            <h4>学生信息管理与统计</h4>
            <span class="tag">
              <el-icon><Top /></el-icon>
              基础层
            </span>
            <p
              >结构化录入学生档案，支持 Excel/CSV
              批量导入，多维度筛选检索，实时统计就业状态分布。</p
            >
          </div>

          <div class="feature-card">
            <div class="feature-icon cyan">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <h4>数据可视化分析</h4>
            <span class="tag">
              <el-icon><Top /></el-icon>
              展示层
            </span>
            <p
              >就业去向分布图、生源地热力地图、行业流向图、薪资分布直方图，支持一键导出
              PNG/PDF/Excel。</p
            >
          </div>

          <div class="feature-card">
            <div class="feature-icon green">
              <el-icon><DataBoard /></el-icon>
            </div>
            <h4>社会岗位需求分析</h4>
            <span class="tag">
              <el-icon><Top /></el-icon>
              供给侧
            </span>
            <p>技能词云、岗位地域热力图，专业-岗位匹配矩阵、学历要求分析，掌握市场需求动态。</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon purple">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <h4>AI 就业画像</h4>
            <span class="tag primary">
              <el-icon><Cpu /></el-icon>
              核心亮点
            </span>
            <p
              >基于 DeepSeek
              大语言模型，生成就业竞争力评分(0-100)，雷达图展示专业匹配度、技能契合度等维度。</p
            >
          </div>

          <div class="feature-card">
            <div class="feature-icon blue">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <h4>智能岗位匹配推荐</h4>
            <span class="tag">
              <el-icon><Connection /></el-icon>
              RAG 检索
            </span>
            <p
              >结合向量数据库和 RAG 技术，根据学生档案推荐 Top-N
              匹配岗位，给出匹配度说明和差距分析。</p
            >
          </div>

          <div class="feature-card">
            <div class="feature-icon cyan">
              <el-icon><Lock /></el-icon>
            </div>
            <h4>就业困难预警</h4>
            <span class="tag">
              <el-icon><Top /></el-icon>
              主动干预
            </span>
            <p
              >AI
              自动生成预警标签（技能不足/期望过高/地区限制），批量生成定向辅导建议，推送给辅导员。</p
            >
          </div>

          <div class="feature-card">
            <div class="feature-icon green">
              <el-icon><Document /></el-icon>
            </div>
            <h4>AI 简历优化</h4>
            <span class="tag">
              <el-icon><Top /></el-icon>
              ATS 模拟
            </span>
            <p
              >对比目标岗位 JD 关键词，AI
              指出简历与岗位的语义差距，给出具体措辞优化建议，提升通过率。</p
            >
          </div>

          <div class="feature-card">
            <div class="feature-icon purple">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <h4>稀缺人才数据分析</h4>
            <span class="tag">
              <el-icon><Top /></el-icon>
              数据洞察
            </span>
            <p>展示各省稀缺岗位地图、行业紧缺度排名，为院校专业设置和学生就业方向提供参考。</p>
          </div>
        </div>
      </div>
    </section>

    <!-- AI Technical Path Section -->
    <section class="section">
      <div class="container">
        <div class="section-header">
          <div class="section-title">
            <el-icon><Cpu /></el-icon>
            <h2>AI 技术实现路径</h2>
          </div>
          <p class="section-subtitle">大语言模型在就业服务场景的完整调用链路</p>
        </div>

        <div class="tech-path">
          <div class="path-step">
            <div class="step-number blue">1</div>
            <div class="step-content">
              <h4>用户数据采集层</h4>
              <p
                >学生端采集简历信息、技能标签、职业兴趣；企业端采集岗位要求、薪资范围；院校端采集专业设置、毕业生数据</p
              >
            </div>
          </div>

          <div class="path-step">
            <div class="step-number cyan">2</div>
            <div class="step-content">
              <h4>RAG 向量检索增强</h4>
              <p
                >将简历文本、企业 JD、稀缺人才数据通过文本嵌入模型向量化，存储至 ChromaDB
                向量数据库，支持语义相似度检索</p
              >
            </div>
          </div>

          <div class="path-step">
            <div class="step-number purple">3</div>
            <div class="step-content">
              <h4>System Prompt 注入</h4>
              <p
                >构建结构化系统提示词，注入就业评估规则（专业技能权重、设计作品集评估维度）、JSON
                输出格式约束</p
              >
            </div>
          </div>

          <div class="path-step">
            <div class="step-number orange">4</div>
            <div class="step-content">
              <h4>LLM 推理层</h4>
              <p
                >调用 DeepSeek API (OpenAI Compatible Mode)，temperature=0.2
                保证输出稳定性，response_format=json_object 强制 JSON 输出</p
              >
            </div>
          </div>

          <div class="path-step">
            <div class="step-number red">5</div>
            <div class="step-content">
              <h4>降级兜底策略</h4>
              <p
                >API
                不可用时启用本地规则引擎（基于关键词匹配、技能标签比对），确保系统在无网络环境下仍能完成基础匹配</p
              >
            </div>
          </div>

          <div class="path-step">
            <div class="step-number green">6</div>
            <div class="step-content">
              <h4>结果渲染与反馈</h4>
              <p
                >将 AI
                分析结果映射为可视化卡片（匹配度、技能差距、预警级别），收集用户反馈持续优化模型效果</p
              >
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- System Architecture Section -->
    <section class="section bg-light" id="architecture">
      <div class="container">
        <div class="section-header">
          <div class="section-title">
            <el-icon><Box /></el-icon>
            <h2>系统架构总览</h2>
          </div>
          <p class="section-subtitle">前后端分离、模块化设计、高可用性保障</p>
        </div>

        <div class="arch-grid">
          <div class="arch-card">
            <h4>
              <el-icon><Monitor /></el-icon>
              前端技术栈
            </h4>
            <ul>
              <li>Vue 3 + TypeScript 类型安全</li>
              <li>Vite 构建工具极速响应</li>
              <li>Pinia 状态管理</li>
              <li>TailwindCSS 响应式样式</li>
              <li>ECharts 数据可视化图表</li>
              <li>Element Plus 企业级组件</li>
            </ul>
          </div>

          <div class="arch-card cyan">
            <h4>
              <el-icon><Cpu /></el-icon>
              后端技术栈
            </h4>
            <ul>
              <li>FastAPI Python 高性能框架</li>
              <li>SQLAlchemy ORM 持久化</li>
              <li>JWT 三级角色权限控制</li>
              <li>Pydantic 数据验证</li>
              <li>SQLite 轻量级数据库</li>
              <li>Uvicorn ASGI 高性能服务</li>
            </ul>
          </div>

          <div class="arch-card green">
            <h4>
              <el-icon><MagicStick /></el-icon>
              AI 服务层
            </h4>
            <ul>
              <li>DeepSeek API 中文理解强</li>
              <li>ChromaDB 向量数据库</li>
              <li>文本嵌入模型 (Embedding)</li>
              <li>RAG 检索增强生成</li>
              <li>JSON 结构化输出解析</li>
              <li>降级规则引擎兜底</li>
            </ul>
          </div>

          <div class="arch-card orange">
            <h4>
              <el-icon><Lock /></el-icon>
              安全与合规
            </h4>
            <ul>
              <li>JWT Token 身份认证</li>
              <li>BCrypt 密码哈希加密</li>
              <li>CORS 跨域安全策略</li>
              <li>输入数据严格校验</li>
              <li>敏感信息脱敏处理</li>
              <li>操作日志审计追踪</li>
            </ul>
          </div>

          <div class="arch-card purple">
            <h4>
              <el-icon><Folder /></el-icon>
              数据层设计
            </h4>
            <ul>
              <li>SQLite 轻量级嵌入式存储</li>
              <li>ChromaDB 向量相似度检索</li>
              <li>FileSystem 简历文件管理</li>
              <li>数据索引与全文搜索</li>
              <li>scarce_talent 稀缺人才表</li>
              <li>定期数据备份机制</li>
            </ul>
          </div>

          <div class="arch-card">
            <h4>
              <el-icon><Tools /></el-icon>
              DevOps 部署
            </h4>
            <ul>
              <li>前后端分离独立部署</li>
              <li>Nginx 反向代理配置</li>
              <li>环境变量配置管理</li>
              <li>日志收集与监控</li>
              <li>Graceful 优雅重启</li>
              <li>CORS 生产环境配置</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Stack Section -->
    <section class="section">
      <div class="container">
        <div class="section-header">
          <div class="section-title">
            <el-icon><Code /></el-icon>
            <h2>核心技术栈</h2>
          </div>
          <p class="section-subtitle">全栈自研，选用成熟稳定的技术方案</p>
        </div>

        <div class="tech-stack">
          <span class="tech-tag">Vue 3</span>
          <span class="tech-tag">TypeScript</span>
          <span class="tech-tag">Vite</span>
          <span class="tech-tag">Pinia</span>
          <span class="tech-tag">TailwindCSS</span>
          <span class="tech-tag">Element Plus</span>
          <span class="tech-tag">ECharts</span>
          <span class="tech-tag">FastAPI</span>
          <span class="tech-tag">SQLAlchemy</span>
          <span class="tech-tag">JWT</span>
          <span class="tech-tag">Pydantic</span>
          <span class="tech-tag">ChromaDB</span>
          <span class="tech-tag">DeepSeek</span>
          <span class="tech-tag">Python</span>
          <span class="tech-tag">SQLite</span>
        </div>
      </div>
    </section>

    <!-- Team Section -->
    <section class="section bg-light" id="team">
      <div class="container">
        <div class="section-header">
          <div class="section-title">
            <el-icon><User /></el-icon>
            <h2>开发团队</h2>
          </div>
          <p class="section-subtitle">大学生就业信息智能分析平台</p>
        </div>

        <div class="team-card">
          <a href="https://github.com/tenchat/4c" target="_blank" class="team-member">
            <img src="/icon2.svg" alt="logo" class="team-logo" />
          </a>
          <h3>大学生就业信息智能分析平台</h3>
          <p class="team-desc">以数据驱动就业决策，用 AI 赋能职业规划</p>

          <div class="divider"></div>

          <div class="team-roles">
            <a href="https://github.com/tenchat" target="_blank" class="team-member">
              <img src="/u1.png" alt="tenchat" class="team-avatar" />
              <p class="team-name">tenchat</p>
            </a>
            <a href="https://github.com/LEO_Jackwei" target="_blank" class="team-member">
              <img src="/u2.jpg" alt="LEO_Jackwei" class="team-avatar" />
              <p class="team-name">LEO_Jackwei</p>
            </a>
          </div>

          <div class="divider"></div>

          <p class="note"
            >本项目由参赛团队独立设计与开发，所有核心功能、架构设计与界面实现均为原创。AI
            工具仅用于辅助开发与特定业务场景（详见上方功能清单），不涉及作品核心创意的生成。</p
          >
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <p>大学生就业信息智能分析平台 · 产教融合就业解决方案 · 4C 2026</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
  import { useRouter } from 'vue-router'
  import { ref, onMounted, onUnmounted } from 'vue'
  import {
    Box,
    ArrowRight,
    VideoPlay,
    User,
    UserFilled,
    Plus,
    Reading,
    OfficeBuilding,
    Grid,
    TrendCharts,
    DataBoard,
    WarningFilled,
    Cpu,
    ChatDotRound,
    Connection,
    Lock,
    Document,
    Monitor,
    MagicStick,
    Folder,
    Tools,
    Top
  } from '@element-plus/icons-vue'

  defineOptions({ name: 'Showcase' })

  const router = useRouter()

  // Background image slider
  const bgImages = [
    '/bg/1.jpg',
    '/bg/2.jpg',
    '/bg/3.jpg',
    '/bg/4.jpg',
    '/bg/5.jpg',
    '/bg/6.jpg',
    '/bg/7.jpg',
    '/bg/8.jpg',
    '/bg/9.jpg'
  ]
  const currentBgIndex = ref(0)
  let bgTimer: ReturnType<typeof setInterval> | null = null

  const startBgTimer = () => {
    bgTimer = setInterval(() => {
      currentBgIndex.value = (currentBgIndex.value + 1) % bgImages.length
    }, 5000)
  }

  onMounted(() => {
    startBgTimer()
  })

  onUnmounted(() => {
    if (bgTimer) clearInterval(bgTimer)
  })

  const goLogin = () => {
    router.push('/auth/login')
  }

  const scrollTo = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }
</script>

<style scoped>
  /* CSS Variables */
  .showcase-page {
    --primary: #1e40af;
    --primary-light: #3b82f6;
    --primary-lighter: #60a5fa;
    --secondary: #0ea5e9;
    --cta: #22c55e;
    --cta-light: #4ade80;
    --bg: #eff6ff;
    --bg-white: #fff;
    --bg-light: #f8fafc;
    --text: #1e3a8a;
    --text-muted: #64748b;
    --text-light: #94a3b8;
    --border: #e2e8f0;
    --shadow: rgb(30 64 175 / 8%);
    --shadow-lg: rgb(30 64 175 / 12%);
    --gradient-primary: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    --gradient-cta: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);

    font-family:
      'Noto Sans',
      Figtree,
      -apple-system,
      BlinkMacSystemFont,
      sans-serif;
    line-height: 1.6;
    color: var(--text);
    background: var(--bg);
  }

  .showcase-page h1,
  .showcase-page h2,
  .showcase-page h3,
  .showcase-page h4 {
    font-family: Figtree, 'Noto Sans', sans-serif;
    font-weight: 700;
  }

  /* Navigation */
  .nav {
    position: sticky;
    top: 0;
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    padding: 0 32px;
    background: rgb(255 255 255 / 85%);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgb(255 255 255 / 60%);
    box-shadow: 0 4px 24px var(--shadow);
  }

  .nav-brand {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .nav-logo {
    width: 32px;
    height: 32px;
    object-fit: contain;
    border-radius: 8px;
  }

  .nav-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
  }

  .nav-links {
    display: flex;
    gap: 24px;
  }

  .nav-link {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    text-decoration: none;
    cursor: pointer;
    transition: color 0.2s;
  }

  .nav-link:hover {
    color: var(--primary);
  }

  /* Container */
  .container {
    max-width: 1200px;
    padding: 0 32px;
    margin: 0 auto;
  }

  /* Hero Section */
  .hero {
    position: relative;
    z-index: 1;
    padding: 80px 24px 64px;
    overflow: hidden;
    text-align: center;
  }

  /* Roles Section - continues background */
  .roles-section {
    position: relative;
    z-index: 1;
    padding-top: 0;
  }

  /* Background Slider - shared for hero + roles */
  .hero-bg {
    position: absolute;
    inset: 0;
    z-index: 0;
  }

  .hero-bg-slide {
    position: absolute;
    inset: 0;
    background-repeat: no-repeat;
    background-position: center;
    background-size: cover;
    opacity: 0;
    transition: opacity 1.5s ease-in-out;
  }

  .hero-bg-slide.active {
    opacity: 1;
  }

  /* Single gradient overlay - center 50% opacity, edges 20% */
  .hero-bg-overlay-base {
    position: absolute;
    inset: 0;
    pointer-events: none;
    background: linear-gradient(
      to right,
      rgb(150 200 255 / 30%) 0%,
      rgb(150 200 255 / 60%) 25%,
      rgb(150 200 255 / 60%) 75%,
      rgb(150 200 255 / 30%) 100%
    );
  }

  .hero-content {
    position: relative;
    z-index: 1;
    max-width: 900px;
    margin: 0 auto;
  }

  .hero-badge {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    padding: 8px 20px;
    margin-bottom: 24px;
    font-size: 12px;
    font-weight: 700;
    color: var(--text-muted);

    /* 文字阴影版毛玻璃 */
    text-shadow:
      0 0 20px rgb(255 255 255 / 90%),
      0 0 40px rgb(255 255 255 / 60%);
    background: rgb(255 255 255 / 25%);
    border-radius: 20px;
  }

  .hero-badge .el-icon {
    color: var(--primary);
  }

  .hero h1 {
    margin-bottom: 20px;
    font-size: 48px;
    font-weight: 800;
    line-height: 1.2;
    color: var(--text);

    /* 文字阴影版毛玻璃 */
    text-shadow:
      0 0 20px rgb(255 255 255 / 95%),
      0 0 40px rgb(255 255 255 / 70%),
      0 2px 8px rgb(255 255 255 / 50%);
    letter-spacing: -1px;
  }

  .hero h1 .hero-title-img {
    display: block;
    height: 3.6em;
    margin: 0 auto 8px;

    /* 毛玻璃效果 */
    filter: drop-shadow(0 0 10px rgb(255 255 255 / 80%))
      drop-shadow(0 0 20px rgb(255 255 255 / 50%));
    animation: float 3s ease-in-out infinite;
  }

  @keyframes float {
    0%,
    100% {
      transform: translateY(0);
    }

    50% {
      transform: translateY(-12px);
    }
  }

  .hero p {
    max-width: 720px;
    margin: 0 auto;
    font-size: 18px;
    line-height: 1.8;
    color: var(--text);

    /* 文字阴影版毛玻璃 */
    text-shadow:
      0 0 15px rgb(255 255 255 / 90%),
      0 0 30px rgb(255 255 255 / 50%);
  }

  .hero-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-top: 32px;
  }

  .hero-buttons .el-button {
    display: inline-flex;
    gap: 10px;
    align-items: center;
    padding: 18px 36px;
    font-size: 15px;
    font-weight: 700;
    border-radius: 14px;
  }

  /* Section */
  .section {
    padding: 64px 32px;
  }

  .section.bg-light {
    background: var(--bg-light);
  }

  .section-header {
    margin-bottom: 48px;
    text-align: center;
  }

  .section-header .section-title h2 {
    font-size: 32px;
    font-weight: 800;
    color: var(--text);

    /* 文字阴影版毛玻璃 */
    text-shadow:
      0 0 20px rgb(255 255 255 / 95%),
      0 0 40px rgb(255 255 255 / 70%);
    letter-spacing: -0.5px;
  }

  .section-header .section-subtitle {
    display: block;
    margin-top: 12px;
    font-size: 15px;
    font-weight: 500;
    color: var(--text-muted);

    /* 文字阴影版毛玻璃 */
    text-shadow:
      0 0 15px rgb(255 255 255 / 90%),
      0 0 30px rgb(255 255 255 / 50%);
  }

  .section-title {
    display: flex;
    gap: 12px;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
  }

  .section-title .el-icon {
    font-size: 28px;
    color: var(--primary);
  }

  /* User Roles */
  .roles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
  }

  .role-card {
    padding: 28px;
    text-align: center;
    background: var(--bg-white);
    border: 1px solid rgb(0 0 0 / 4%);
    border-radius: 20px;
    box-shadow: 0 4px 24px var(--shadow);
    transition:
      transform 0.2s,
      box-shadow 0.2s;
  }

  .role-card:hover {
    box-shadow: 0 8px 32px var(--shadow-lg);
    transform: translateY(-4px);
  }

  .role-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    margin: 0 auto 16px;
    border-radius: 16px;
  }

  .role-icon.blue {
    background: var(--gradient-primary);
  }

  .role-icon.cyan {
    background: linear-gradient(135deg, #0891b2 0%, #0ea5e9 100%);
  }

  .role-icon.green {
    background: linear-gradient(135deg, #059669 0%, #22c55e 100%);
  }

  .role-icon .el-icon {
    font-size: 28px;
    color: white;
  }

  .role-card h4 {
    margin-bottom: 8px;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
  }

  .role-card p {
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-muted);
  }

  /* Features Grid */
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
  }

  .feature-card {
    position: relative;
    padding: 28px;
    overflow: hidden;
    background: var(--bg-white);
    border: 1px solid rgb(0 0 0 / 4%);
    border-radius: 20px;
    box-shadow: 0 4px 24px var(--shadow);
    transition:
      transform 0.2s,
      box-shadow 0.2s;
  }

  .feature-card:hover {
    box-shadow: 0 8px 32px var(--shadow-lg);
    transform: translateY(-4px);
  }

  .feature-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    margin-bottom: 16px;
    border-radius: 14px;
  }

  .feature-icon.blue {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  }

  .feature-icon.cyan {
    background: linear-gradient(135deg, #0891b2 0%, var(--secondary) 100%);
  }

  .feature-icon.green {
    background: linear-gradient(135deg, #059669 0%, var(--cta) 100%);
  }

  .feature-icon.purple {
    background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
  }

  .feature-icon .el-icon {
    font-size: 24px;
    color: white;
  }

  .feature-card h4 {
    margin-bottom: 6px;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
  }

  .feature-card .tag {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    padding: 4px 12px;
    margin-bottom: 12px;
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
    background: var(--bg);
    border-radius: 6px;
  }

  .feature-card .tag.primary {
    color: var(--primary);
    background: rgb(30 64 175 / 10%);
  }

  .feature-card .tag .el-icon {
    font-size: 10px;
  }

  .feature-card p {
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-muted);
  }

  /* Tech Path */
  .tech-path {
    padding: 40px;
    background: var(--bg-white);
    border: 1px solid rgb(0 0 0 / 4%);
    border-radius: 24px;
    box-shadow: 0 4px 24px var(--shadow);
  }

  .path-step {
    position: relative;
    display: flex;
    gap: 20px;
  }

  .path-step:not(:last-child) {
    padding-bottom: 32px;
  }

  .path-step:not(:last-child)::after {
    position: absolute;
    top: 44px;
    left: 19px;
    width: 2px;
    height: calc(100% - 24px);
    content: '';
    background: linear-gradient(to bottom, var(--primary-lighter), var(--border));
    border-radius: 1px;
  }

  .step-number {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    font-family: Figtree, monospace;
    font-size: 13px;
    font-weight: 800;
    border-radius: 50%;
  }

  .step-number.blue {
    color: white;
    background: var(--primary);
    box-shadow: 0 4px 12px rgb(30 64 175 / 20%);
  }

  .step-number.cyan {
    color: white;
    background: var(--secondary);
    box-shadow: 0 4px 12px rgb(14 165 233 / 20%);
  }

  .step-number.purple {
    color: white;
    background: #7c3aed;
    box-shadow: 0 4px 12px rgb(124 58 237 / 20%);
  }

  .step-number.orange {
    color: white;
    background: #ea580c;
    box-shadow: 0 4px 12px rgb(234 88 12 / 20%);
  }

  .step-number.red {
    color: white;
    background: #dc2626;
    box-shadow: 0 4px 12px rgb(220 38 38 / 20%);
  }

  .step-number.green {
    color: white;
    background: var(--cta);
    box-shadow: 0 4px 12px rgb(34 197 94 / 20%);
  }

  .step-content {
    flex: 1;
    padding-bottom: 8px;
  }

  .step-content h4 {
    margin-bottom: 6px;
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
  }

  .step-content p {
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-muted);
  }

  /* Architecture Grid */
  .arch-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
  }

  .arch-card {
    padding: 24px;
    background: var(--bg-white);
    border-top: 3px solid var(--primary);
    border-radius: 16px;
    box-shadow: 0 2px 16px var(--shadow);
    transition: transform 0.2s;
  }

  .arch-card:hover {
    transform: translateY(-2px);
  }

  .arch-card.cyan {
    border-top-color: var(--secondary);
  }

  .arch-card.green {
    border-top-color: var(--cta);
  }

  .arch-card.orange {
    border-top-color: #ea580c;
  }

  .arch-card.purple {
    border-top-color: #7c3aed;
  }

  .arch-card h4 {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 14px;
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
  }

  .arch-card h4 .el-icon {
    color: var(--primary);
  }

  .arch-card.cyan h4 .el-icon {
    color: var(--secondary);
  }

  .arch-card.green h4 .el-icon {
    color: var(--cta);
  }

  .arch-card.orange h4 .el-icon {
    color: #ea580c;
  }

  .arch-card.purple h4 .el-icon {
    color: #7c3aed;
  }

  .arch-card ul {
    padding: 0;
    margin: 0;
    list-style: none;
  }

  .arch-card li {
    position: relative;
    padding-left: 14px;
    font-size: 13px;
    line-height: 2;
    color: var(--text-muted);
  }

  .arch-card li::before {
    position: absolute;
    top: 50%;
    left: 0;
    width: 5px;
    height: 5px;
    content: '';
    background: var(--primary-lighter);
    border-radius: 50%;
    opacity: 0.5;
    transform: translateY(-50%);
  }

  /* Tech Stack */
  .tech-stack {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
  }

  .tech-tag {
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--bg-white);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: 0 2px 8px var(--shadow);
    transition: all 0.2s;
  }

  .tech-tag:hover {
    color: var(--primary);
    border-color: var(--primary-light);
  }

  /* Team Section */
  .team-card {
    padding: 40px;
    text-align: center;
    background: var(--bg-white);
    border-radius: 20px;
    box-shadow: 0 4px 24px var(--shadow);
  }

  .team-logo {
    width: 72px;
    height: 72px;
    margin: 0 auto 16px;
    object-fit: contain;
    border-radius: 16px;
  }

  .team-card h3 {
    margin-bottom: 8px;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
  }

  .team-desc {
    font-size: 14px;
    color: var(--text-muted);
  }

  .divider {
    height: 1px;
    margin: 24px 40px;
    background: var(--border);
  }

  .team-roles {
    display: flex;
    gap: 48px;
    justify-content: center;
    margin-bottom: 24px;
  }

  .team-member {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: center;
    text-decoration: none;
    transition: transform 0.2s;
  }

  .team-member:hover {
    transform: translateY(-4px);
  }

  .team-avatar {
    width: 80px;
    height: 80px;
    object-fit: cover;
    border: 3px solid var(--border);
    border-radius: 50%;
    box-shadow: 0 4px 12px var(--shadow);
  }

  .team-name {
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
  }

  .note {
    font-size: 13px;
    line-height: 1.8;
    color: var(--text-light);
  }

  /* Footer */
  .footer {
    padding: 32px;
    text-align: center;
    background: var(--bg-white);
    border-top: 1px solid var(--border);
  }

  .footer p {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-light);
  }

  /* Responsive */
  @media (width <= 768px) {
    .hero h1 {
      font-size: 32px;
    }

    .hero-buttons {
      flex-direction: column;
      align-items: center;
    }

    .section {
      padding: 48px 16px;
    }

    .nav-links {
      display: none;
    }

    .team-roles {
      flex-direction: column;
      gap: 24px;
    }
  }
</style>
