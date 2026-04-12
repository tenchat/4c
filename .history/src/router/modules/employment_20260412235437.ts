import { AppRouteRecord } from '@/types/router'

// 管理端路由（system_admin 和 school_admin）
const adminRoutes: AppRouteRecord[] = [
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: '/school/dashboard',
    meta: { title: '管理首页', icon: 'ri:home-line', keepAlive: false, roles: ['system_admin', 'school_admin'] }
  },
  {
    path: '/admin/colleges',
    name: 'AdminColleges',
    component: '/admin/colleges',
    meta: { title: '学院管理', icon: 'ri:government-line', keepAlive: true, roles: ['system_admin'] }
  },
  {
    path: '/school/colleges',
    name: 'SchoolColleges',
    component: '/admin/colleges',
    meta: { title: '学院管理', icon: 'ri:government-line', keepAlive: true, roles: ['school_admin'] }
  },
  {
    path: '/admin/companies',
    name: 'AdminCompanies',
    component: '/admin/companies',
    meta: { title: '企业管理', icon: 'ri:briefcase-line', keepAlive: true, roles: ['system_admin', 'school_admin'] }
  },
  {
    path: '/admin/students',
    name: 'AdminStudents',
    component: '/school/students',
    meta: { title: '学生管理', icon: 'ri:user-settings-line', keepAlive: true, roles: ['system_admin', 'school_admin'] }
  },
  {
    path: '/admin/warnings',
    name: 'AdminWarnings',
    component: '/school/warnings',
    meta: { title: '就业预警', icon: 'ri:alert-line', keepAlive: true, roles: ['system_admin', 'school_admin'] }
  },
  {
    path: '/admin/company-announcements',
    name: 'AdminCompanyAnnouncements',
    component: '/school/company-announcements',
    meta: { title: '企业公告', icon: 'ri:megaphone-line', keepAlive: true, roles: ['school_admin'] }
  },
  {
    path: '/school/company-announcements',
    name: 'SchoolCompanyAnnouncements',
    component: '/school/company-announcements',
    meta: { title: '企业公告', icon: 'ri:megaphone-line', keepAlive: true, roles: ['school_admin'] }
  },
  {
    path: '/admin/company-activities',
    name: 'AdminCompanyActivities',
    component: '/school/company-activities',
    meta: { title: '企业宣讲会', icon: 'ri:calendar-event-line', keepAlive: true, roles: ['system_admin', 'school_admin'] }
  },
  {
    path: '/school/company-activities',
    name: 'SchoolCompanyActivities',
    component: '/school/company-activities',
    meta: { title: '企业宣讲会', icon: 'ri:calendar-event-line', keepAlive: true, roles: ['school_admin'] }
  },
  {
    path: '/admin/settings',
    name: 'AdminSettings',
    component: '/admin/settings',
    meta: { title: '系统设置', icon: 'ri:settings-line', keepAlive: false, roles: ['system_admin'] }
  },
  {
    path: '/admin/password',
    name: 'AdminPassword',
    component: '/common/password',
    meta: { title: '修改密码', icon: 'ri:lock-password-line', keepAlive: false, roles: ['system_admin', 'school_admin'] }
  },
  {
    path: '/admin/changelog',
    name: 'AdminChangelog',
    component: '/change/log',
    meta: { title: '更新日志', icon: 'ri:history-line', keepAlive: false, roles: ['system_admin', 'school_admin'] }
  }
]

// 企业端路由（仅限 company_admin）
const companyRoutes: AppRouteRecord[] = [
  {
    path: '/company/dashboard',
    name: 'CompanyDashboard',
    component: '/company/dashboard',
    meta: { title: '企业首页', icon: 'ri:home-line', keepAlive: true, roles: ['company_admin'] }
  },
  {
    path: '/company/databoard',
    name: 'CompanyDataboard',
    component: '/company/databoard',
    meta: { title: '数据大屏', icon: 'ri:bar-chart-box-line', keepAlive: false, roles: ['company_admin'] }
  },
  {
    path: '/company/profile',
    name: 'CompanyProfile',
    component: '/company/profile',
    meta: { title: '企业信息', icon: 'ri:building-line', keepAlive: false, roles: ['company_admin'] }
  },
  {
    path: '/company/jobs',
    name: 'CompanyJobs',
    component: '/company/jobs',
    meta: { title: '岗位管理', icon: 'ri:briefcase-line', keepAlive: true, roles: ['company_admin'] }
  },
  {
    path: '/company/post-job',
    name: 'CompanyPostJob',
    component: '/company/post-job',
    meta: { title: '发布岗位', icon: 'ri:add-circle-line', keepAlive: false, roles: ['company_admin'] }
  },
  {
    path: '/company/activities',
    name: 'CompanyActivities',
    component: '/company/activities/index',
    meta: { title: '活动管理', icon: 'ri:calendar-event-line', keepAlive: true, roles: ['company_admin'] }
  },
  {
    path: '/company/announcements',
    name: 'CompanyAnnouncements',
    component: '/company/announcements/index',
    meta: { title: '招聘公告', icon: 'ri:megaphone-line', keepAlive: true, roles: ['company_admin'] }
  },
  {
    path: '/company/resumes',
    name: 'CompanyResumes',
    component: '/company/resumes/index',
    meta: { title: '简历管理', icon: 'ri:file-text-line', keepAlive: true, roles: ['company_admin'] }
  },
  {
    path: '/company/password',
    name: 'CompanyPassword',
    component: '/common/password',
    meta: { title: '修改密码', icon: 'ri:lock-password-line', keepAlive: false, roles: ['company_admin'] }
  },
  {
    path: '/company/changelog',
    name: 'CompanyChangelog',
    component: '/change/log',
    meta: { title: '更新日志', icon: 'ri:history-line', keepAlive: false, roles: ['company_admin'] }
  }
]

// 学生端路由（仅限 student）
const studentRoutes: AppRouteRecord[] = [
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: '/student/dashboard',
    meta: { title: '个人首页', icon: 'ri:home-line', keepAlive: true, roles: ['student'] }
  },
  {
    path: '/student/databoard',
    name: 'StudentDataboard',
    component: '/student/databoard',
    meta: { title: '就业数据大屏', icon: 'ri:bar-chart-box-line', keepAlive: false, roles: ['student'] }
  },
  {
    path: '/student/profile',
    name: 'StudentProfile',
    component: '/student/profile',
    meta: { title: '档案管理', icon: 'ri:file-user-line', keepAlive: false, roles: ['student'] }
  },
  {
    path: '/student/jobs',
    name: 'StudentJobs',
    component: '/student/jobs',
    meta: { title: '岗位推荐', icon: 'ri:briefcase-line', keepAlive: true, roles: ['student'] }
  },
  {
    path: '/student/announcements',
    name: 'StudentAnnouncements',
    component: '/student/announcements',
    meta: { title: '招聘公告', icon: 'ri:megaphone-line', keepAlive: true, roles: ['student'] }
  },
  {
    path: '/student/activities',
    name: 'StudentActivities',
    component: '/student/activities',
    meta: { title: '宣讲会/活动', icon: 'ri:calendar-event-line', keepAlive: true, roles: ['student'] }
  },
  {
    path: '/student/ai-profile',
    name: 'AiProfile',
    component: '/student/ai-profile',
    meta: { title: 'AI就业画像', icon: 'ri:ai-generate', keepAlive: false, roles: ['student'] }
  },
  {
    path: '/student/ai-resume',
    name: 'AiResume',
    component: '/student/ai-resume',
    meta: { title: 'AI简历优化', icon: 'ri:file-edit-line', keepAlive: false, roles: ['student'] }
  },
  {
    path: '/student/interview-prep',
    name: 'InterviewPrep',
    component: '/student/interview-prep',
    meta: { title: '面试准备助手', icon: 'ri:message-3-line', keepAlive: false, roles: ['student'] }
  },
  {
    path: '/student/password',
    name: 'StudentPassword',
    component: '/common/password',
    meta: { title: '修改密码', icon: 'ri:lock-password-line', keepAlive: false, roles: ['student'] }
  },
  {
    path: '/student/changelog',
    name: 'StudentChangelog',
    component: '/change/log',
    meta: { title: '更新日志', icon: 'ri:history-line', keepAlive: false, roles: ['student'] }
  }
]

export { studentRoutes, adminRoutes, companyRoutes }

export const employmentRoutes: AppRouteRecord[] = [
  ...adminRoutes,
  ...companyRoutes,
  ...studentRoutes
]