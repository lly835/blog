import os
import re
import requests
from typing import Optional
from dataclasses import dataclass

MINIMAX_API_URL = "https://api.minimaxi.com/v1/chat/completions"
MINIMAX_MODEL = "MiniMax-M2.1"

SYSTEM_PROMPT = """你是一位专业的技术博客作者。你的任务是根据提供的素材（视频字幕或文章内容）撰写一篇**精炼简洁**的技术博客/笔记。

⚠️ 核心要求：文章总字数控制在 800-1500 字以内，重点在于提炼精华，而非全面覆盖。

写作要求：
1. 使用 Markdown 格式，结构清晰（## 和 ### 标题）
2. 只保留最核心的 3-5 个要点，舍弃次要内容
3. 每个要点用 2-3 句话概括，避免冗余展开
4. 保持专业、客观的语气
5. 如有代码示例，只保留关键片段
6. 结尾一句话总结即可，不需要大段感想

注意：
- 不要生成一级标题（# 标题），系统会自动添加
- 直接从正文内容开始
- 宁可精简，不要啰嗦"""

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
        content = self._clean_thinking_tags(content)
        
        tags = self._extract_tags(video_title, video_description)
        
        return BlogContent(
            title=video_title,
            content=content,
            tags=tags
        )
    
    def _build_user_prompt(
        self,
        title: str,
        author: str,
        description: str,
        user_note: str,
        content: Optional[str]
    ) -> str:
        parts = [
            f"## 素材信息",
            f"- 标题：{title}",
            f"- 作者/UP主：{author}",
            f"- 简介：{description or '无'}",
            "",
            f"## 用户备注",
            user_note or "无特别备注",
        ]
        
        if content:
            truncated = content[:6000] if len(content) > 6000 else content
            parts.extend([
                "",
                "## 内容详情",
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
    
    def _clean_thinking_tags(self, content: str) -> str:
        cleaned = re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL)
        return cleaned.strip()

def format_blog_markdown(
    blog: BlogContent,
    video_url: str,
    video_author: str,
    video_duration: str
) -> str:
    source_label = "链接"
    if "bilibili" in video_url or "b23.tv" in video_url:
        source_label = "B站视频"
    
    frontmatter = f"""---
title: "{blog.title}"
date: "{_get_current_date()}"
tags: {blog.tags}
source: "{video_url}"
author: "{video_author}"
duration: "{video_duration}"
---

"""
    
    body = f"""> 本文基于 {source_label} [{blog.title}]({video_url}) 整理
> 作者：{video_author} | 时长/类型：{video_duration}

{blog.content}

---

*本文由 AI 辅助生成，内容基于原素材整理。*
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
