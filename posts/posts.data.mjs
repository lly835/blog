import { createContentLoader } from 'vitepress'

export default createContentLoader('posts/*.md', {
  includeSrc: false,
  transform(rawData) {
    return rawData
      .filter(page => !page.url.endsWith('/posts/'))
      .sort((a, b) => {
        return new Date(b.frontmatter.date) - new Date(a.frontmatter.date)
      })
      .map(page => ({
        title: page.frontmatter.title || 'Untitled',
        url: page.url,
        date: page.frontmatter.date || '',
        tags: page.frontmatter.tags || [],
        author: page.frontmatter.author || '',
        duration: page.frontmatter.duration || '',
        source: page.frontmatter.source || ''
      }))
  }
})
