---
layout: doc
---

# 博客文章

这里收录了从 B站视频自动生成的技术博客。

## 文章列表

<script setup>
import { data } from './posts.data.mjs'
import { withBase } from 'vitepress'
</script>

<div class="posts-list">
  <div v-for="post in data" :key="post.url" class="post-item">
    <h3><a :href="withBase(post.url)">{{ post.title }}</a></h3>
    <p class="post-meta">
      <span>📅 {{ post.date }}</span>
      <span v-if="post.author"> · 👤 {{ post.author }}</span>
      <span v-if="post.duration"> · ⏱️ {{ post.duration }}</span>
    </p>
    <p class="post-tags" v-if="post.tags && post.tags.length">
      <span v-for="tag in post.tags" :key="tag" class="tag">{{ tag }}</span>
    </p>
  </div>
</div>

<style>
.posts-list {
  margin-top: 2rem;
}
.post-item {
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--vp-c-divider);
}
.post-item:last-child {
  border-bottom: none;
}
.post-item h3 {
  margin: 0 0 0.5rem 0;
}
.post-item h3 a {
  color: var(--vp-c-brand-1);
  text-decoration: none;
}
.post-item h3 a:hover {
  text-decoration: underline;
}
.post-meta {
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
  margin: 0.5rem 0;
}
.post-tags {
  margin: 0.5rem 0 0 0;
}
.tag {
  display: inline-block;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-right: 0.5rem;
}
</style>
