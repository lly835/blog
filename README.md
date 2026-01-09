# B站视频自动博客生成器

通过 GitHub Issue 发送 B站视频链接，自动生成技术博客并提交到仓库。

## 功能特性

- 📺 自动获取 B站视频信息和字幕
- 🤖 使用 MiniMax AI 生成技术博客
- 📝 自动提交 Markdown 文件到仓库
- 💬 Issue 自动关闭 + 钉钉通知（可选）

## 架构

```
创建 GitHub Issue (添加 generate-blog 标签)
    ↓
GitHub Actions 自动触发
    ↓
获取 B站视频信息 + 字幕
    ↓
MiniMax AI 生成博客
    ↓
自动提交到仓库 + 关闭 Issue
```

## 使用方法

### 1. 创建 Issue

在仓库中 [创建新 Issue](../../issues/new)

### 2. 填写内容

**标题**: 随意，比如"分享一个视频"

**内容**: 
```
今天看了个不错的 Go 教程
https://www.bilibili.com/video/BV1xxxxxx
```

### 3. 添加标签

给 Issue 添加 `generate-blog` 标签

### 4. 等待生成

- GitHub Actions 会自动触发
- 生成完成后 Issue 会被自动关闭
- Issue 评论中会包含生成的博客链接

## 部署指南

### 1. Fork 仓库

### 2. 创建 Issue 标签

在仓库 **Issues** → **Labels** 中创建标签：
- 名称：`generate-blog`
- 颜色：随意

### 3. 配置 GitHub Secrets

进入仓库 **Settings** → **Secrets and variables** → **Actions**：

| Secret | 必填 | 说明 |
|--------|------|------|
| `MINIMAX_API_KEY` | ✅ | MiniMax API Key |
| `BILIBILI_SESSDATA` | ❌ | B站登录 Cookie（获取字幕用） |
| `DINGTALK_WEBHOOK` | ❌ | 钉钉通知 Webhook URL |

## 获取 B站 SESSDATA（可选）

有 SESSDATA 才能获取视频字幕，没有的话只能用标题和简介生成。

1. 登录 B站
2. 打开浏览器开发者工具 (F12)
3. 进入 **Application** → **Cookies** → `https://www.bilibili.com`
4. 复制 `SESSDATA` 的值

## 获取 MiniMax API Key

1. 注册 [MiniMax 开放平台](https://www.minimaxi.com/)
2. 进入 **用户中心** → **接口密钥**
3. 创建新的 API Key

## 目录结构

```
blog/
├── .github/workflows/
│   └── generate-blog.yml    # GitHub Actions 工作流
├── scripts/
│   ├── bilibili.py          # B站 API 客户端
│   ├── blog_generator.py    # MiniMax 博客生成
│   ├── main.py              # 主入口
│   └── requirements.txt     # 依赖
├── posts/                   # 生成的博客文章
└── README.md
```

## 本地测试

```bash
cd scripts
pip install -r requirements.txt

export MINIMAX_API_KEY="your-key"
export BILIBILI_SESSDATA="your-sessdata"  # 可选

python main.py --message "测试 https://www.bilibili.com/video/BV1xxxxxx"
```

## 钉钉通知（可选）

如需在博客生成后收到钉钉通知：

1. 在钉钉群创建自定义机器人（Incoming Webhook）
2. 复制 Webhook URL
3. 添加到 GitHub Secrets：`DINGTALK_WEBHOOK`

## License

MIT
