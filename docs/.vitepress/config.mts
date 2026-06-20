import { readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { defineConfig } from 'vitepress'
import llmstxt from 'vitepress-plugin-llms'

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
  description:
    'Open-source Discord AI bot — connect Gemini, GPT-4o, Claude, Llama, or Ollama to your Discord server in minutes. Web UI setup, slash commands, tools, and no restarts needed.',
  lang: 'en-US',

  // Published at https://zhiro-labs.github.io/dango
  base: '/dango/',
  cleanUrls: true,
  lastUpdated: true,
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

  // Emit a <meta name="keywords"> per page from the legacy `tags` front matter,
  // preserving the SEO value the old MkDocs `tags` plugin provided.
  transformHead({ pageData }) {
    const tags = pageData.frontmatter.tags as string[] | undefined
    if (tags?.length) {
      return [['meta', { name: 'keywords', content: tags.join(', ') }]]
    }
  },

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Getting Started', link: '/getting-started/discord-setup' },
      { text: 'Configuration', link: '/configuration/env-vars' },
      { text: 'Features', link: '/features/models' },
      { text: 'Usage', link: '/usage/commands' },
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

    socialLinks: [
      { icon: 'github', link: 'https://github.com/zhiro-labs/dango' },
    ],

    search: { provider: 'local' },

    editLink: {
      pattern: 'https://github.com/zhiro-labs/dango/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },

    footer: {
      message:
        'MIT License · Built on <a href="https://docs.agno.com">Agno</a>',
      copyright: '© 2025 zhiro-labs',
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
