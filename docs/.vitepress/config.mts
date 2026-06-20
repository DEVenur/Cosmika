import { readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { defineConfig, type HeadConfig } from 'vitepress'
import llmstxt from 'vitepress-plugin-llms'

const SITE_ORIGIN = 'https://zhiro-labs.github.io'
const BASE = '/dango/'
const SITE_DESCRIPTION =
  'Dango is a free, open-source, self-hosted Discord AI bot and agent — connect Gemini, GPT-4o, Claude, Llama, or Ollama and run your own Discord AI on your server in minutes. Web UI setup, slash commands, tools, no restarts.'
const OG_IMAGE = `${SITE_ORIGIN}${BASE}og-image.png`

// Site-wide target keywords, emitted on every page (merged with each page's
// own `tags`). Leads with the "Discord AI" phrasing we want to rank for.
const BASE_KEYWORDS = [
  'Discord AI',
  'Discord AI bot',
  'Discord AI agent',
  'Discord AI chatbot',
  'self-hosted Discord AI bot',
  'free Discord AI bot',
  'Discord bot',
  'AI chatbot',
  'Dango',
]

// Absolute canonical URL for a page from its source path, honouring cleanUrls
// (`features/models.md` → `…/dango/features/models`, `index.md` → `…/dango/`).
function pageUrl(relativePath: string): string {
  const clean = relativePath.replace(/(^|\/)index\.md$/, '$1').replace(/\.md$/, '')
  return `${SITE_ORIGIN}${BASE}${clean}`
}

// vitepress-plugin-llms injects a `url`/`description` front-matter block into
// every generated Markdown twin. Strip it so the human-facing "View / Copy
// Markdown" output is clean prose — the front matter only ever existed to feed
// llms.txt generation, and should never surface to a reader.
const FRONT_MATTER = /^---\r?\n[\s\S]*?\r?\n---\r?\n+/

function stripTwinFrontMatter(outDir: string): void {
  for (const entry of readdirSync(outDir, { recursive: true }) as string[]) {
    if (!entry.endsWith('.md')) continue
    const file = join(outDir, entry)
    const text = readFileSync(file, 'utf-8')
    if (FRONT_MATTER.test(text)) {
      writeFileSync(file, text.replace(FRONT_MATTER, ''), 'utf-8')
    }
  }
}

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: 'Dango',
  description: SITE_DESCRIPTION,
  lang: 'en-US',

  // Published at https://zhiro-labs.github.io/dango
  base: '/dango/',
  cleanUrls: true,
  lastUpdated: true,

  // Favicons (head hrefs are not base-prefixed automatically, so include it).
  // Per-page Open Graph / Twitter / canonical tags are added in transformHead.
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/dango/favicon.svg' }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/dango/favicon-32.png' }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/dango/favicon-16.png' }],
    ['link', { rel: 'apple-touch-icon', href: '/dango/apple-touch-icon.png' }],
    ['meta', { name: 'theme-color', content: '#7c4dff' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:site_name', content: 'Dango' }],
    ['meta', { property: 'og:image', content: OG_IMAGE }],
    ['meta', { property: 'og:image:width', content: '1200' }],
    ['meta', { property: 'og:image:height', content: '630' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:image', content: OG_IMAGE }],
  ],
  // Markdown source still carries the legacy `tags`/`summary` front matter from
  // the MkDocs era — keep it, just don't fail the build on unknown keys.
  ignoreDeadLinks: false,

  sitemap: {
    hostname: 'https://zhiro-labs.github.io/dango/',
  },

  markdown: {
    // `.env` code fences highlight as ini (Shiki has no dedicated `env` grammar).
    languageAlias: { env: 'ini' },

    // Drop an anchor right after the page's intro paragraph (the lede that
    // follows the H1), before the first `##` section. CopyForLLM.vue teleports
    // the "Copy page" control onto it, so the button sits below the title and
    // opening text rather than above the heading.
    config(md) {
      md.core.ruler.push('llm_copy_anchor', (state) => {
        const tokens = state.tokens
        const firstH2 = tokens.findIndex(
          (t) => t.type === 'heading_open' && t.tag === 'h2',
        )
        const firstParaClose = tokens.findIndex(
          (t) => t.type === 'paragraph_close',
        )

        let at: number
        if (firstParaClose !== -1 && (firstH2 === -1 || firstParaClose < firstH2)) {
          at = firstParaClose + 1 // after the intro lede paragraph
        } else if (firstH2 !== -1) {
          at = firstH2 // page jumps straight to a section — sit under the H1
        } else {
          return // no headings/paragraphs (e.g. the home page body) — skip
        }

        const anchor = new state.Token('html_block', '', 0)
        anchor.content = '<div class="vp-llm-copy-anchor"></div>\n'
        anchor.block = true
        tokens.splice(at, 0, anchor)
      })
    },
  },

  // Runs after the SSG build (and after vitepress-plugin-llms has written the
  // Markdown twins), so it can clean up their generated front matter.
  buildEnd(siteConfig) {
    stripTwinFrontMatter(siteConfig.outDir)
  },

  // Per-page SEO: canonical URL, Open Graph / Twitter title+description,
  // keywords (from the legacy `tags` front matter), and structured data.
  transformHead({ pageData }) {
    const fm = pageData.frontmatter
    const isHome = fm.layout === 'home'
    const url = pageUrl(pageData.relativePath)
    const title = isHome ? 'Dango — Discord AI Bot & Agent' : `${pageData.title} | Dango`
    const description = pageData.description || SITE_DESCRIPTION

    const head: HeadConfig[] = [
      ['link', { rel: 'canonical', href: url }],
      ['meta', { property: 'og:title', content: title }],
      ['meta', { property: 'og:description', content: description }],
      ['meta', { property: 'og:url', content: url }],
      ['meta', { name: 'twitter:title', content: title }],
      ['meta', { name: 'twitter:description', content: description }],
    ]

    const tags = (fm.tags as string[] | undefined) ?? []
    const keywords = [...new Set([...BASE_KEYWORDS, ...tags])].join(', ')
    head.push(['meta', { name: 'keywords', content: keywords }])

    if (isHome) {
      head.push([
        'script',
        { type: 'application/ld+json' },
        JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'SoftwareApplication',
          name: 'Dango',
          alternateName: 'Dango — Discord AI Bot & Agent',
          applicationCategory: 'DeveloperApplication',
          operatingSystem: 'Docker, Linux, macOS, Windows',
          description: SITE_DESCRIPTION,
          keywords: BASE_KEYWORDS.join(', '),
          url: `${SITE_ORIGIN}${BASE}`,
          image: OG_IMAGE,
          license: 'https://github.com/zhiro-labs/dango/blob/main/LICENSE',
          isAccessibleForFree: true,
          offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
          author: {
            '@type': 'Organization',
            name: 'zhiro-labs',
            url: 'https://github.com/zhiro-labs',
          },
          sameAs: ['https://github.com/zhiro-labs/dango'],
        }),
      ])
    }

    return head
  },

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    logo: '/logo.svg',

    nav: [
      { text: 'Home', link: '/' },
      { text: 'Getting Started', link: '/getting-started/discord-setup' },
      { text: 'Configuration', link: '/configuration/env-vars' },
      { text: 'Features', link: '/features/models' },
      { text: 'Usage', link: '/usage/commands' },
      // External link — VitePress appends the ↗ indicator automatically. Sits
      // beside Usage; the redundant socialLinks GitHub icon is dropped below.
      { text: 'GitHub', link: 'https://github.com/zhiro-labs/dango' },
    ],

    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Discord Setup', link: '/getting-started/discord-setup' },
          { text: 'Docker (Recommended)', link: '/getting-started/docker' },
          { text: 'uv (Developers)', link: '/getting-started/uv' },
        ],
      },
      {
        text: 'Configuration',
        items: [
          { text: 'Environment Variables', link: '/configuration/env-vars' },
          { text: 'Runtime Config', link: '/configuration/runtime' },
        ],
      },
      {
        text: 'Features',
        items: [
          { text: 'Model Providers & Routing', link: '/features/models' },
          { text: 'Tools', link: '/features/tools' },
          { text: 'Custom Commands & Tools', link: '/features/extensions' },
          { text: 'Workflow Architecture', link: '/features/workflow' },
        ],
      },
      {
        text: 'Usage',
        items: [
          { text: 'Slash Commands', link: '/usage/commands' },
          { text: 'Conversations', link: '/usage/conversations' },
        ],
      },
      {
        text: 'Advanced',
        items: [
          { text: 'Embedding into Another Bot', link: '/advanced/embedding' },
          { text: 'VPS Deployment', link: '/advanced/vps' },
        ],
      },
      {
        text: 'Reference',
        items: [
          { text: 'API Reference', link: '/reference/api' },
          { text: 'Troubleshooting', link: '/troubleshooting' },
        ],
      },
    ],

    search: { provider: 'local' },

    editLink: {
      pattern: 'https://github.com/zhiro-labs/dango/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },

    footer: {
      message:
        'MIT License · Built on <a href="https://docs.agno.com">Agno</a>',
      // Build-time year as the SSR/no-JS fallback; the theme's setup() updates
      // the .footer-year span to the visitor's current year at runtime.
      copyright: `© <span class="footer-year">${new Date().getFullYear()}</span> zhiro-labs`,
    },
  },

  vite: {
    plugins: [
      // Generates llms.txt / llms-full.txt and a same-origin .md twin for every
      // page — the self-hosted "Copy for LLM" replacement for the old
      // docs/hooks/llm_md.py build hook.
      llmstxt({
        description:
          'Discord AI Agent built on Agno. Connects to any AI model provider — Google Gemini/Gemma, OpenAI, Anthropic, Groq, Ollama, and more. Features dual-model routing, multilingual complexity scoring, table-to-image rendering, and a browser-based setup dashboard.',
      }),
    ],
  },
})
