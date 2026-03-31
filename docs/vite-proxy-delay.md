# Vite 开发服务器代理延迟问题

## 问题描述

前端通过 Vite 代理访问后端 API 时，每次请求耗时约 **4 秒**。

## 环境信息

- 前端：`http://localhost:5173` (Vite 开发服务器)
- 后端：`http://localhost:5174` (FastAPI)
- 操作系统：Windows

## 测试数据

| 测试方式 | 耗时 |
|---------|------|
| 直接访问后端 `http://localhost:5174/api/v1/admin/companies/pending` | ~3ms |
| 通过 Vite 代理 `http://localhost:5173/api/v1/admin/companies/pending` | ~4100ms |

## 初步分析

1. **后端正常** - 直接访问后端 API 响应很快（3ms）
2. **Vite 代理异常** - 通过代理时延迟约 4 秒
3. **网络链路问题** - 延迟稳定在 4 秒，非随机波动

## 已尝试的解决方案

1. 修改 `vite.config.ts` 代理配置（添加 cache: false、timeout 等）
2. 改用 `127.0.0.1` 替代 `localhost`
3. 清除 Vite 缓存 (`node_modules/.vite`)
4. 绕过 Vite 代理（直接连接后端）

## 可能的根因

1. **Windows 防火墙/杀毒软件** 干扰 localhost 连接
2. **Vite 代理 http-proxy 问题**
3. **Windows Hyper-V 或 WSL 网络配置** 冲突
4. **Node.js 版本** 兼容性问题

## 建议排查方向

1. 暂时关闭杀毒软件/防火墙测试
2. 检查 Windows 事件查看器是否有网络相关错误
3. 尝试在其他设备（Linux/Mac）上复现问题
4. 尝试禁用/卸载某些网络相关软件（VPN、科学上网工具等）
5. 使用 Wireshark 抓包分析 TCP 连接耗时分布
6. 检查 `C:\Windows\System32\drivers\etc\hosts` 文件是否有异常配置

## 相关文件

- `vite.config.ts` - Vite 代理配置
- `.env.development` - 环境变量（VITE_API_PROXY_URL）

## 临时解决方案

如果问题无法解决，可暂时绕过 Vite 代理：

1. 修改 `.env.development`：
```env
VITE_API_BASE_URL = http://localhost:5174
```

2. 修改 `vite.config.ts`：
```ts
server: {
  port: Number(VITE_PORT),
  proxy: undefined,
}
```

3. 缺点：跨域问题需要后端配置 CORS

---

*文档创建时间：2026-03-30*
