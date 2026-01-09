import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'AI 技术博客',
  description: '从 B站视频自动生成的技术博客',
  lang: 'zh-CN',
  base: '/blog/',
  ignoreDeadLinks: true,
  
  head: [
    ['link', { rel: 'icon', href: '/blog/favicon.ico' }]
  ],

  themeConfig: {
    logo: '/logo.svg',
    
    nav: [
      { text: '首页', link: '/' },
      { text: '博客', link: '/posts/' },
      { text: 'GitHub', link: 'https://github.com/lly835/blog' }
    ],

    sidebar: {
      '/posts/': [
        {
          text: '博客文章',
          items: []
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/lly835/blog' }
    ],

    footer: {
      message: '由 AI 自动生成的技术博客',
      copyright: 'Copyright © 2026'
    },

    search: {
      provider: 'local'
    },

    outline: {
      level: [2, 3],
      label: '目录'
    },

    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    },

    lastUpdated: {
      text: '最后更新',
      formatOptions: {
        dateStyle: 'short',
        timeStyle: 'short'
      }
    }
  },

  markdown: {
    lineNumbers: true
  },

  lastUpdated: true
})
