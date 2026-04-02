import { AppRouteRecord } from '@/types/router'

// 学生端路由
const studentRoutes: AppRouteRecord = {
  name: 'Student',
  path: '/student',
  component: '/index/index',
  meta: {
    title: '学生中心',
    icon: 'ri:user-line',
    roles: ['student']
  },
  children: [
    {
      path: 'dashboard',
      name: 'StudentDashboard',
      component: '/student/dashboard',
      meta: {
        title: '个人首页',
        keepAlive: true
      }
    },
    {
      path: 'profile',
      name: 'StudentProfile',
      component: '/student/profile',
      meta: {
        title: '档案管理',
        keepAlive: false
      }
    },
    {
      path: 'jobs',
      name: 'StudentJobs',
      component: '/student/jobs',
      meta: {
        title: '岗位推荐',
        keepAlive: true
      }
    },
    {
      path: 'ai-profile',
      name: 'AiProfile',
      component: '/student/ai-profile',
      meta: {
        title: 'AI就业画像',
        keepAlive: false
      }
    },
    {
      path: 'ai-resume',
      name: 'AiResume',
      component: '/student/ai-resume',
      meta: {
        title: 'AI简历优化',
        keepAlive: false
      }
    },
    {
      path: 'ai-decision',
      name: 'AiDecision',
      component: '/student/ai-decision',
      meta: {
        title: '考研vs就业',
        keepAlive: false
      }
    }
  ]
}

// 学校端路由
const schoolRoutes: AppRouteRecord = {
  name: 'School',
  path: '/school',
  component: '/index/index',
  meta: {
    title: '学校管理',
    icon: 'ri:government-line',
    roles: ['school_admin', 'system_admin']
  },
  children: [
    {
      path: 'dashboard',
      name: 'SchoolDashboard',
      component: '/school/dashboard',
      meta: {
        title: '学校首页',
        keepAlive: true
      }
    },
    {
      path: 'profile',
      name: 'SchoolProfile',
      component: '/school/profile',
      meta: {
        title: '学校信息',
        keepAlive: false
      }
    },
    {
      path: 'students',
      name: 'SchoolStudents',
      component: '/school/students',
      meta: {
        title: '学生管理',
        keepAlive: true
      }
    },
    {
      path: 'warnings',
      name: 'SchoolWarnings',
      component: '/school/warnings',
      meta: {
        title: '就业预警',
        keepAlive: true
      }
    },
    {
      path: 'databoard',
      name: 'SchoolDataboard',
      component: '/school/databoard',
      meta: {
        title: '数据大屏',
        keepAlive: false
      }
    },
    {
      path: 'profile-review',
      name: 'SchoolProfileReview',
      component: '/admin/profile-review',
      meta: {
        title: '信息审核',
        keepAlive: true,
        roles: ['school_admin', 'system_admin']
      }
    }
  ]
}

// 管理端路由
const adminRoutes: AppRouteRecord = {
  name: 'Admin',
  path: '/admin',
  component: '/index/index',
  meta: {
    title: '系统管理',
    icon: 'ri:settings-line',
    roles: ['system_admin']
  },
  children: [
    {
      path: 'dashboard',
      name: 'AdminDashboard',
      component: '/admin/dashboard',
      meta: {
        title: '管理首页',
        keepAlive: true
      }
    },
    {
      path: 'colleges',
      name: 'AdminColleges',
      component: '/admin/colleges',
      meta: {
        title: '学院管理',
        keepAlive: true
      }
    },
    {
      path: 'companies',
      name: 'AdminCompanies',
      component: '/admin/companies',
      meta: {
        title: '企业管理',
        keepAlive: true
      }
    },
    {
      path: 'profile-review',
      name: 'AdminProfileReview',
      component: '/admin/profile-review',
      meta: {
        title: '信息审核',
        keepAlive: true,
        roles: ['system_admin', 'school_admin']
      }
    },
    {
      path: 'databoard',
      name: 'AdminDataboard',
      component: '/admin/databoard',
      meta: {
        title: '数据大屏',
        keepAlive: false
      }
    }
  ]
}

// 企业端路由
const companyRoutes: AppRouteRecord = {
  name: 'Company',
  path: '/company',
  component: '/index/index',
  meta: {
    title: '企业管理',
    icon: 'ri:briefcase-line',
    roles: ['company_admin']
  },
  children: [
    {
      path: 'dashboard',
      name: 'CompanyDashboard',
      component: '/company/dashboard',
      meta: {
        title: '企业首页',
        keepAlive: true
      }
    },
    {
      path: 'profile',
      name: 'CompanyProfile',
      component: '/company/profile',
      meta: {
        title: '企业信息',
        keepAlive: false
      }
    },
    {
      path: 'jobs',
      name: 'CompanyJobs',
      component: '/company/jobs',
      meta: {
        title: '岗位管理',
        keepAlive: true
      }
    },
    {
      path: 'post-job',
      name: 'CompanyPostJob',
      component: '/company/post-job',
      meta: {
        title: '发布岗位',
        keepAlive: false
      }
    },
    {
      path: 'activities',
      name: 'CompanyActivities',
      component: '/company/activities/index',
      meta: {
        title: '活动管理',
        icon: 'ri:calendar-event-line',
        keepAlive: true,
        roles: ['company_admin']
      }
    },
    {
      path: 'announcements',
      name: 'CompanyAnnouncements',
      component: '/company/announcements/index',
      meta: {
        title: '招聘公告',
        icon: 'ri:megaphone-line',
        keepAlive: true,
        roles: ['company_admin']
      }
    }
  ]
}

export { studentRoutes, schoolRoutes, adminRoutes, companyRoutes }

export const employmentRoutes: AppRouteRecord[] = [
  studentRoutes,
  schoolRoutes,
  adminRoutes,
  companyRoutes
]
