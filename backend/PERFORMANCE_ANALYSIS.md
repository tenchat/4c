# 前端接口加载慢 - 情况说明

## 问题描述

前端调用 `/api/v1/admin/companies/pending` 接口，从点击到展示数据耗时约 4.1s。

## 后端性能测试结果

直接调用后端接口（绕过前端），响应时间仅 **3ms**：

```bash
[TIMING] auth=0.000s db=0.003s total=0.003s
```

- `auth`: 0ms - Token 验证
- `db`: 3ms - 数据库查询
- `total`: 3ms - 端到端后端耗时

## 结论

**后端 API 已优化完成，响应正常（3ms）。4.1s 延迟发生在前端或网络层。**

## 排查方向

### 1. 前端重试机制
Callstack 显示 `retryRequest` 被调用，可能存在重试逻辑导致延迟。

### 2. Vite 开发服务器代理
前端 dev server（通常 5173/5174）可能通过代理转发请求，需检查 `vite.config` 中的代理配置。

### 3. 浏览器网络耗时
在浏览器开发者工具 Network 面板查看请求详情：
- `Waiting (TTFB)` - 后端处理时间
- `Content Download` - 响应下载时间
- `Initial connection` - DNS/TCP 连接时间

### 4. 前端组件渲染
可能存在 Vue 组件首次渲染开销或不必要的重复渲染。

## 已验证正常的后端代码

- `app/core/redis_client.py` - 使用 `redis.asyncio` 异步 Redis
- `app/core/security.py` - 异步 token 验证
- `app/core/dependencies.py` - async/await 正确使用
- `app/models/base.py` - `TimestampMixin` 使用 `datetime.utcnow`

## 下一步

请前端同事检查：
1. Network 面板请求的实际耗时分布
2. `retryRequest` 的重试条件和次数
3. Vite 代理配置
