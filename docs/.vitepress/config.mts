import { defineConfig } from 'vitepress'
import llmstxt from 'vitepress-plugin-llms'

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
