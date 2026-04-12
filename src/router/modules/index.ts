import { AppRouteRecord } from '@/types/router'
import { employmentRoutes } from './employment'

/**
 * 导出所有模块化路由（仅就业系统相关路由）
 */
export const routeModules: AppRouteRecord[] = [
  ...employmentRoutes
]
