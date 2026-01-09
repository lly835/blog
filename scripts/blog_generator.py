import os
import re
import requests
from typing import Optional
from dataclasses import dataclass

MINIMAX_API_URL = "https://api.minimax.io/v1/chat/completions"
MINIMAX_MODEL = "MiniMax-M1"

SYSTEM_PROMPT = """你是一位专业的技术博客作者。你的任务是根据视频内容撰写一篇高质量的技术博客/笔记。

写作要求：
1. 使用 Markdown 格式
2. 包含清晰的标题结构（使用 ## 和 ### 等）
3. 提炼视频中的核心观点和技术要点
4. 保持专业、客观的语气
5. 适当添加个人见解和思考
6. 如果是教程类视频，整理出关键步骤
7. 如果有代码示例，使用代码块格式化

博客结构建议：
- 开头简要介绍视频主题和来源
- 主体部分按逻辑组织内容要点
- 结尾可以添加总结或个人思考

注意：
- 不要生成文章的一级标题（# 标题），因为会由系统自动添加
- 直接从正文内容开始"""


@dataclass
class BlogContent:
    title: str
    content: str
    tags: list[str]


class BlogGenerator:
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def generate(
        self,
        video_title: str,
        video_author: str,
        video_description: str,
        user_note: str,
        subtitle_content: Optional[str] = None
    ) -> BlogContent:
        user_prompt = self._build_user_prompt(
            video_title, video_author, video_description, user_note, subtitle_content
        )
        
        payload = {
            "model": MINIMAX_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        
        resp = self.session.post(MINIMAX_API_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        
        if "choices" not in data or not data["choices"]:
            raise ValueError(f"API 返回格式异常: {data}")
        
        content = data["choices"][0]["message"]["content"]
        
        tags = self._extract_tags(video_title, video_description)
        
        return BlogContent(
            title=video_title,
            content=content,
            tags=tags
        )
    
    def _build_user_prompt(
        self,
        video_title: str,
        video_author: str,
        video_description: str,
        user_note: str,
        subtitle_content: Optional[str]
    ) -> str:
        parts = [
            f"## 视频信息",
            f"- 标题：{video_title}",
            f"- UP主：{video_author}",
            f"- 简介：{video_description or '无'}",
            "",
            f"## 用户备注",
            user_note or "无特别备注",
        ]
        
        if subtitle_content:
            truncated = subtitle_content[:8000] if len(subtitle_content) > 8000 else subtitle_content
            parts.extend([
                "",
                "## 视频字幕内容",
                truncated
            ])
        
        parts.extend([
            "",
            "---",
            "请根据以上信息撰写一篇技术博客/笔记。"
        ])
        
        return "\n".join(parts)
    
    def _extract_tags(self, title: str, description: str) -> list[str]:
        tech_keywords = [
            "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
            "React", "Vue", "Angular", "Node.js", "Django", "Flask", "Spring",
            "Docker", "Kubernetes", "K8s", "AWS", "Azure", "GCP",
            "MySQL", "PostgreSQL", "MongoDB", "Redis",
            "Linux", "Git", "DevOps", "CI/CD",
            "机器学习", "深度学习", "AI", "人工智能", "算法", "数据结构",
            "前端", "后端", "全栈", "微服务", "架构",
        ]
        
        combined = f"{title} {description}".lower()
        tags = []
        
        for keyword in tech_keywords:
            if keyword.lower() in combined:
                tags.append(keyword)
        
        return tags[:5]


def format_blog_markdown(
    blog: BlogContent,
    video_url: str,
    video_author: str,
    video_duration: str
) -> str:
    frontmatter = f"""---
title: "{blog.title}"
date: "{_get_current_date()}"
tags: {blog.tags}
source: "{video_url}"
author: "{video_author}"
duration: "{video_duration}"
---

"""
    
    body = f"""> 本文基于 B站视频 [{blog.title}]({video_url}) 整理
> UP主：{video_author} | 时长：{video_duration}

{blog.content}

---

*本文由 AI 辅助生成，内容基于视频字幕和简介整理。*
"""
    
    return frontmatter + body


def _get_current_date() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


if __name__ == "__main__":
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print("请设置 MINIMAX_API_KEY 环境变量")
        exit(1)
    
    generator = BlogGenerator(api_key)
    
    blog = generator.generate(
        video_title="测试视频标题",
        video_author="测试UP主",
        video_description="这是一个测试视频的简介",
        user_note="这是我的测试备注",
        subtitle_content="这是测试的字幕内容..."
    )
    
    print(f"标题: {blog.title}")
    print(f"标签: {blog.tags}")
    print(f"内容预览:\n{blog.content[:500]}...")
