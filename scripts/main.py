#!/usr/bin/env python3
import os
import re
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime

from bilibili import BilibiliClient, format_duration
from blog_generator import BlogGenerator, format_blog_markdown


POSTS_DIR = Path(__file__).parent.parent / "posts"


def extract_bilibili_url(text: str) -> str | None:
    patterns = [
        r'https?://(?:www\.)?bilibili\.com/video/(BV[a-zA-Z0-9]+)',
        r'https?://b23\.tv/([a-zA-Z0-9]+)',
        r'(BV[a-zA-Z0-9]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            bvid = match.group(1)
            if bvid.startswith("BV"):
                return f"https://www.bilibili.com/video/{bvid}"
            return f"https://b23.tv/{bvid}"
    
    return None


def slugify(text: str, max_length: int = 50) -> str:
    slug = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', text)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:max_length]


def generate_blog(
    message: str,
    bilibili_sessdata: str | None = None,
    minimax_api_key: str | None = None
) -> dict:
    minimax_api_key = minimax_api_key or os.environ.get("MINIMAX_API_KEY")
    if not minimax_api_key:
        raise ValueError("MINIMAX_API_KEY 未设置")
    
    bilibili_sessdata = bilibili_sessdata or os.environ.get("BILIBILI_SESSDATA")
    
    video_url = extract_bilibili_url(message)
    if not video_url:
        raise ValueError(f"未找到有效的 B站链接: {message}")
    
    user_note = re.sub(
        r'https?://[^\s]+',
        '',
        message
    ).strip()
    
    bili_client = BilibiliClient(sessdata=bilibili_sessdata)
    video_info = bili_client.get_full_video_info(video_url)
    
    print(f"视频标题: {video_info.title}")
    print(f"UP主: {video_info.author}")
    print(f"字幕: {'有' if video_info.subtitle_content else '无'}")
    
    generator = BlogGenerator(minimax_api_key)
    blog = generator.generate(
        video_title=video_info.title,
        video_author=video_info.author,
        video_description=video_info.description,
        user_note=user_note,
        subtitle_content=video_info.subtitle_content
    )
    
    markdown_content = format_blog_markdown(
        blog=blog,
        video_url=video_url,
        video_author=video_info.author,
        video_duration=format_duration(video_info.duration)
    )
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(video_info.title)
    filename = f"{date_str}-{slug}.md"
    filepath = POSTS_DIR / filename
    
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(markdown_content, encoding="utf-8")
    
    print(f"博客已生成: {filepath}")
    
    return {
        "filepath": str(filepath),
        "filename": filename,
        "title": video_info.title,
        "tags": blog.tags,
        "url": video_url
    }


def notify_dingtalk(webhook_url: str | None, result: dict) -> None:
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

**来源**: [B站视频]({result['url']})
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
