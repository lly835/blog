#!/usr/bin/env python3
import os
import re
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional

from bilibili import BilibiliClient, format_duration
from blog_generator import BlogGenerator, format_blog_markdown


from content_extractor import ContentExtractor

POSTS_DIR = Path(__file__).parent.parent / "posts"


def extract_url(text: str) -> Optional[str]:
    patterns = [
        r'https?://(?:www\.)?bilibili\.com/video/(BV[a-zA-Z0-9]+)',
        r'https?://b23\.tv/([a-zA-Z0-9]+)',
        r'(BV[a-zA-Z0-9]+)',
        r'https?://mp\.weixin\.qq\.com/s/[\w-]+',
        r'https?://mp\.weixin\.qq\.com/s\?__biz=[\w=&-]+',
        r'https?://[^\s]+'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            url = match.group(0)
            if "bilibili.com" in url or "b23.tv" in url or url.startswith("BV"):
                 if url.startswith("BV"):
                     return f"https://www.bilibili.com/video/{url}"
                 return url
            return url
    
    return None

def is_bilibili_url(url: str) -> bool:
    return "bilibili.com" in url or "b23.tv" in url


def slugify(text: str, max_length: int = 50) -> str:
    slug = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', text)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:max_length]


def generate_blog(
    message: str,
    bilibili_sessdata: Optional[str] = None,
    minimax_api_key: Optional[str] = None
) -> dict:
    minimax_api_key = minimax_api_key or os.environ.get("MINIMAX_API_KEY")
    if not minimax_api_key:
        raise ValueError("MINIMAX_API_KEY 未设置")
    
    bilibili_sessdata = bilibili_sessdata or os.environ.get("BILIBILI_SESSDATA")
    
    video_url = extract_url(message)
    if not video_url:
        raise ValueError(f"未找到有效的链接: {message}")
    
    user_note = re.sub(
        r'https?://[^\s]+',
        '',
        message
    ).strip()
    
    if is_bilibili_url(video_url):
        bili_client = BilibiliClient(sessdata=bilibili_sessdata)
        video_info = bili_client.get_full_video_info(video_url)
        
        title = video_info.title
        author = video_info.author
        description = video_info.description
        content = video_info.subtitle_content
        duration = format_duration(video_info.duration)
        source_type = "B站视频"
        
        print(f"视频标题: {title}")
        print(f"UP主: {author}")
        print(f"字幕: {'有' if content else '无'}")
        
    else:
        extractor = ContentExtractor()
        article_info = extractor.extract(video_url)
        
        title = article_info.title
        author = article_info.author
        description = article_info.description or "无简介"
        content = article_info.content
        duration = "阅读"
        source_type = "文章"
        
        print(f"文章标题: {title}")
        print(f"作者: {author}")
    
    generator = BlogGenerator(minimax_api_key)
    blog = generator.generate(
        video_title=title,
        video_author=author,
        video_description=description,
        user_note=user_note,
        subtitle_content=content
    )
    
    markdown_content = format_blog_markdown(
        blog=blog,
        video_url=video_url,
        video_author=author,
        video_duration=duration
    )
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    filepath = POSTS_DIR / filename
    
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(markdown_content, encoding="utf-8")
    
    print(f"博客已生成: {filepath}")
    
    return {
        "filepath": str(filepath),
        "filename": filename,
        "title": title,
        "tags": blog.tags,
        "url": video_url,
        "source_type": source_type
    }


def notify_dingtalk(webhook_url: Optional[str], result: dict) -> None:
    if not webhook_url:
        print("未配置钉钉通知 Webhook，跳过通知")
        return

    github_repo = os.environ.get("GITHUB_REPOSITORY", "lly835/blog")
    file_url = f"https://github.com/{github_repo}/blob/main/{result['filepath']}"
    
    message = {
        "msgtype": "markdown",
        "markdown": {
            "title": "博客生成完成",
            "text": f"""### ✅ 博客已生成

**标题**: {result['title']}

**文件**: [{result['filename']}]({file_url})

**标签**: {', '.join(result['tags']) if result['tags'] else '无'}

**来源**: [{result.get('source_type', '来源')}]({result['url']})
"""
        }
    }
    
    try:
        resp = requests.post(webhook_url, json=message, timeout=10)
        resp.raise_for_status()
        print("钉钉通知发送成功")
    except Exception as e:
        print(f"钉钉通知发送失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="从 B站视频生成博客")
    parser.add_argument("--message", "-m", required=True, help="用户消息（包含 B站链接）")
    parser.add_argument("--notify", "-n", action="store_true", help="发送钉钉通知")
    
    args = parser.parse_args()
    
    try:
        result = generate_blog(args.message)
        
        if args.notify:
            webhook_url = os.environ.get("DINGTALK_WEBHOOK")
            notify_dingtalk(webhook_url, result)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
