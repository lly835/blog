"""
B站视频信息和字幕获取模块

功能：
1. 从链接提取 BV 号
2. 获取视频基本信息（标题、简介、UP主等）
3. 获取视频字幕（如果有）
"""

import re
import json
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class VideoInfo:
    """视频信息数据类"""
    bvid: str
    title: str
    description: str
    author: str
    duration: int  # 秒
    view_count: int
    like_count: int
    cover_url: str
    subtitle_content: Optional[str] = None


class BilibiliClient:
    """B站 API 客户端"""
    
    # API 端点
    VIDEO_INFO_API = "https://api.bilibili.com/x/web-interface/view"
    PLAYER_API = "https://api.bilibili.com/x/player/v2"
    
    def __init__(self, sessdata: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            sessdata: B站登录 Cookie 中的 SESSDATA，用于获取字幕
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com",
        })
        
        if sessdata:
            self.session.cookies.set("SESSDATA", sessdata, domain=".bilibili.com")
    
    @staticmethod
    def extract_bvid(url: str) -> Optional[str]:
        """
        从 URL 中提取 BV 号
        
        支持的格式：
        - https://www.bilibili.com/video/BV1zyiiBRE32
        - https://www.bilibili.com/video/BV1zyiiBRE32?xxx=xxx
        - https://b23.tv/xxxxx (短链接需要先重定向)
        - BV1zyiiBRE32 (纯 BV 号)
        """
        # 直接匹配 BV 号
        bv_pattern = r"(BV[a-zA-Z0-9]+)"
        match = re.search(bv_pattern, url)
        if match:
            return match.group(1)
        return None
    
    def get_video_info(self, bvid: str) -> VideoInfo:
        """
        获取视频基本信息
        
        Args:
            bvid: 视频 BV 号
            
        Returns:
            VideoInfo 对象
        """
        resp = self.session.get(self.VIDEO_INFO_API, params={"bvid": bvid})
        resp.raise_for_status()
        data = resp.json()
        
        if data["code"] != 0:
            raise ValueError(f"获取视频信息失败: {data.get('message', '未知错误')}")
        
        video_data = data["data"]
        
        return VideoInfo(
            bvid=bvid,
            title=video_data["title"],
            description=video_data.get("desc", ""),
            author=video_data["owner"]["name"],
            duration=video_data["duration"],
            view_count=video_data["stat"]["view"],
            like_count=video_data["stat"]["like"],
            cover_url=video_data["pic"],
        )
    
    def get_cid(self, bvid: str) -> int:
        """获取视频的 cid（用于获取字幕）"""
        resp = self.session.get(self.VIDEO_INFO_API, params={"bvid": bvid})
        resp.raise_for_status()
        data = resp.json()
        
        if data["code"] != 0:
            raise ValueError(f"获取视频信息失败: {data.get('message', '未知错误')}")
        
        # 获取第一个分P的 cid
        pages = data["data"].get("pages", [])
        if not pages:
            raise ValueError("无法获取视频分P信息")
        
        return pages[0]["cid"]
    
    def get_subtitle(self, bvid: str) -> Optional[str]:
        """
        获取视频字幕内容
        
        Args:
            bvid: 视频 BV 号
            
        Returns:
            字幕文本内容，如果没有字幕则返回 None
        """
        try:
            cid = self.get_cid(bvid)
            
            # 获取字幕列表
            resp = self.session.get(
                self.PLAYER_API,
                params={"bvid": bvid, "cid": cid}
            )
            resp.raise_for_status()
            data = resp.json()
            
            if data["code"] != 0:
                return None
            
            # 查找字幕信息
            subtitle_info = data.get("data", {}).get("subtitle", {})
            subtitles = subtitle_info.get("subtitles", [])
            
            if not subtitles:
                return None
            
            # 优先选择中文字幕
            subtitle_url = None
            for sub in subtitles:
                if "zh" in sub.get("lan", "").lower() or "cn" in sub.get("lan", "").lower():
                    subtitle_url = sub.get("subtitle_url")
                    break
            
            # 如果没有中文字幕，使用第一个字幕
            if not subtitle_url and subtitles:
                subtitle_url = subtitles[0].get("subtitle_url")
            
            if not subtitle_url:
                return None
            
            # 确保 URL 有协议头
            if subtitle_url.startswith("//"):
                subtitle_url = "https:" + subtitle_url
            
            # 获取字幕内容
            sub_resp = self.session.get(subtitle_url)
            sub_resp.raise_for_status()
            sub_data = sub_resp.json()
            
            # 提取字幕文本
            body = sub_data.get("body", [])
            if not body:
                return None
            
            # 合并所有字幕文本
            texts = [item.get("content", "") for item in body]
            return "\n".join(texts)
            
        except Exception as e:
            print(f"获取字幕失败: {e}")
            return None
    
    def get_full_video_info(self, url: str) -> VideoInfo:
        """
        获取完整的视频信息（包括字幕）
        
        Args:
            url: B站视频链接或 BV 号
            
        Returns:
            VideoInfo 对象，包含字幕内容
        """
        bvid = self.extract_bvid(url)
        if not bvid:
            raise ValueError(f"无法从 URL 中提取 BV 号: {url}")
        
        # 获取基本信息
        video_info = self.get_video_info(bvid)
        
        # 尝试获取字幕
        video_info.subtitle_content = self.get_subtitle(bvid)
        
        return video_info


def format_duration(seconds: int) -> str:
    """格式化时长为 HH:MM:SS 或 MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


# 模块测试
if __name__ == "__main__":
    import os
    
    # 从环境变量获取 SESSDATA
    sessdata = os.environ.get("BILIBILI_SESSDATA")
    
    client = BilibiliClient(sessdata=sessdata)
    
    # 测试链接
    test_url = "https://www.bilibili.com/video/BV1zyiiBRE32"
    
    try:
        info = client.get_full_video_info(test_url)
        print(f"标题: {info.title}")
        print(f"UP主: {info.author}")
        print(f"简介: {info.description[:100]}..." if len(info.description) > 100 else f"简介: {info.description}")
        print(f"时长: {format_duration(info.duration)}")
        print(f"播放: {info.view_count}")
        print(f"点赞: {info.like_count}")
        print(f"字幕: {'有' if info.subtitle_content else '无'}")
        if info.subtitle_content:
            print(f"字幕预览: {info.subtitle_content[:200]}...")
    except Exception as e:
        print(f"错误: {e}")
