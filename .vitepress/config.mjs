import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'AI 技术博客',
  description: '从 B站视频自动生成的技术博客',
  lang: 'zh-CN',
  base: '/',
  ignoreDeadLinks: true,
  
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ],

  sitemap: {
    hostname: 'https://lly835.github.io'
  },

  themeConfig: {
    logo: '/logo.svg',
    
    nav: [
      { text: '首页', link: '/' },
      { text: 'GitHub', link: 'https://github.com/lly835/lly835.github.io' }
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
      { icon: 'github', link: 'https://github.com/lly835/lly835.github.io' }
    ],

    footer: {
      message: '由 AI 自动生成的技术博客',
      copyright: 'Copyright © 2026'
    },

    search: {
      provider: 'local',
      options: {
        detailedView: true
      }
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
