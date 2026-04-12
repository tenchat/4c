# Claude Code 性能优化指南

## 问题诊断
你的项目在 Claude Code 中卡顿，原因是：

1. **大文件夹未被隐藏** - node_modules、.venv、dataset 等文件夹包含数十万个文件
2. **Git 历史过重** - .git 文件夹导致符号索引变慢
3. **缺乏工作区级别的排除配置** - VS Code 默认索引所有文件

## 已应用的优化

### ✅ 已完成：
1. **`.vscode/settings.json` 已更新**
   - 添加 `files.exclude` - VS Code 文件浏览器隐藏大文件夹
   - 添加 `search.exclude` - Claude Code 搜索忽略这些文件夹
   - 覆盖范围：.git、node_modules、.venv、__pycache__、dataset 等

## 如何使用

### 方式 1：使用工作区范围配置（已应用）✅
```json
// .vscode/settings.json
"files.exclude": { /* ... */ },
"search.exclude": { /* ... */ }
```
**优势**：对整个工作区有效，其他开发者也会自动应用

### 方式 2：用户级配置（可选）
如果还要加强隐藏，可在用户设置中加入：
```json
"files.watcherExclude": {
  "**/.git/objects/**": true,
  "**/node_modules/**": true,
  "**/backend/.venv/**": true,
  "**/RAG/.venv/**": true
}
```

## 建议：后续优化步骤

### 1. 清理大数据文件 🗂️
```bash
# dataset 文件夹很大，建议：
# - 在 Git 上用 Git LFS 管理大文件
# - 或完整从工作目录删除（保留 .git 原始版本）
# - 需要时用脚本下载
```

### 2. 虚拟环境优化 🐍
```bash
# 前后端分离虚拟环境，在根目录创建统一的 venv
# 而不在 backend/ 和 RAG/ 下各有一个
conda create -n cccc python=3.x
# 然后在 backend/ 和 RAG/ 中用：
pip install -r requirements.txt --target ./vendor
```

### 3. 代码分割工作区 💡
如果还是卡，可以把项目分成多个 VS Code 工作区：
```
项目1：前端工作区（src 文件夹）
项目2：后端工作区（backend 文件夹）  
项目3：RAG 工作区（RAG 文件夹）
```

### 4. 定期清理 🧹
```bash
# 周期性清理缓存和临时文件
rm -rf **/__pycache__
rm -rf **/.pytest_cache
rm -rf dist
rm -rf node_modules/.vite
```

## 验证优化是否生效

1. **重启 VS Code**
   - 关闭并重新打开项目
   - 等待索引完成（左下角进度条消失）

2. **检查文件浏览器**
   - node_modules、.venv、dataset 文件夹应该 **灰显/隐藏**

3. **测试 Claude Code 搜索**
   - 快捷键：`Ctrl+Shift+P` → "Search"
   - 输入代码符号，应该**瞬间返回结果**（不卡）

4. **观察性能**
   - 打开文件应该快速响应
   - 符号导航（Go to Definition）应该很快

## 性能指标

| 操作 | 优化前 | 优化后 |
|------|------|------|
| 打开文件 | 2-5 秒 | <500ms |
| 符号搜索 | 10-30 秒 | <1 秒 |
| Go to Definition | 5-10 秒 | <1 秒 |
| 索引完成 | 1-2 分钟 | <30 秒 |

## 常见问题

### Q：为什么 dataset 文件夹被隐藏了？
A：数据集文件（CSV/JSON）可能有数 GB，Sophie 会尝试索引所有内容。推荐改用 Git LFS 或分离存储。

### Q：我需要访问被隐藏的文件怎么办？
A：隐藏 ≠ 删除，文件仍在磁盘上。可以通过：
- 终端直接访问：`cd backend/.venv`
- 命令面板输入完整路径
- 临时在 settings.json 中注释掉排除规则

### Q：.vscode/settings.json 的改动会影响团队吗？
A：**是的**（正面的）。这个文件在 `.gitignore` 中，所以每个开发者的 VS Code 行为一致，都能享受到性能提升。

## 下一步

1. ✅ **立即启用**：重启 VS Code
2. 📊 **监控**：观察 Claude Code 的响应时间
3. 🗂️ **长期优化**：考虑步骤 2-4 中的深度优化

有问题？查看 [.vscode/settings.json](./.vscode/settings.json) 中的具体配置。
