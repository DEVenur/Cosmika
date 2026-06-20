<script setup lang="ts">
// Self-hosted "Copy page for LLM" control — WorkOS-style split button.
// Ported from the old docs/javascripts/copy-page.js (MkDocs build). Reads the
// same-origin Markdown twin emitted by vitepress-plugin-llms and offers
// copy / view Markdown plus "Open in <assistant>" deep links.
import { ref, computed, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useData, useRoute, withBase } from 'vitepress'

const ICONS = {
  copy: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H8V7h11v14z"/></svg>',
  chevron: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>',
  link: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M3.9 12a3.1 3.1 0 0 1 3.1-3.1h4V7H7a5 5 0 0 0 0 10h4v-1.9H7A3.1 3.1 0 0 1 3.9 12zM8 13h8v-2H8v2zm9-6h-4v1.9h4a3.1 3.1 0 1 1 0 6.2h-4V17h4a5 5 0 0 0 0-10z"/></svg>',
  markdown: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M22.27 19.385H1.73A1.73 1.73 0 0 1 0 17.655V6.345a1.73 1.73 0 0 1 1.73-1.73h20.54A1.73 1.73 0 0 1 24 6.345v11.308a1.73 1.73 0 0 1-1.73 1.731zM5.769 15.923v-4.5l2.308 2.885l2.307-2.885v4.5h2.308V8.078h-2.308l-2.307 2.885l-2.308-2.885H3.46v7.847zM21.232 12h-2.309V8.077h-2.307V12h-2.308l3.461 4.039z"/></svg>',
  external: '<svg viewBox="0 0 24 24" width="14" height="14" class="llm-ext" aria-hidden="true"><path fill="currentColor" d="M14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/></svg>',
  chatgpt: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M22.282 9.821a6 6 0 0 0-.516-4.91a6.05 6.05 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a6 6 0 0 0-3.998 2.9a6.05 6.05 0 0 0 .743 7.097a5.98 5.98 0 0 0 .51 4.911a6.05 6.05 0 0 0 6.515 2.9A6 6 0 0 0 13.26 24a6.06 6.06 0 0 0 5.772-4.206a6 6 0 0 0 3.997-2.9a6.06 6.06 0 0 0-.747-7.073M13.26 22.43a4.48 4.48 0 0 1-2.876-1.04l.141-.081l4.779-2.758a.8.8 0 0 0 .392-.681v-6.737l2.02 1.168a.07.07 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494M3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085l4.783 2.759a.77.77 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646M2.34 7.896a4.5 4.5 0 0 1 2.366-1.973V11.6a.77.77 0 0 0 .388.677l5.815 3.354l-2.02 1.168a.08.08 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.08.08 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667m2.01-3.023l-.141-.085l-4.774-2.782a.78.78 0 0 0-.785 0L9.409 9.23V6.897a.07.07 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.8.8 0 0 0-.393.681zm1.097-2.365l2.602-1.5l2.607 1.5v2.999l-2.597 1.5l-2.607-1.5Z"/></svg>',
  claude: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M17.304 3.541h-3.672l6.696 16.918H24Zm-10.608 0L0 20.459h3.744l1.37-3.553h7.005l1.369 3.553h3.744L10.536 3.541Zm-.371 10.223L8.616 7.82l2.291 5.945Z"/></svg>',
  cursor: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M11.503.131 1.891 5.678a.84.84 0 0 0-.42.726v11.188c0 .3.162.575.42.724l9.609 5.55a1 1 0 0 0 .998 0l9.61-5.55a.84.84 0 0 0 .42-.724V6.404a.84.84 0 0 0-.42-.726L12.497.131a1.01 1.01 0 0 0-.996 0M2.657 6.338h18.55c.263 0 .43.287.297.515L12.23 22.918c-.062.107-.229.064-.229-.06V12.335a.59.59 0 0 0-.295-.51l-9.11-5.257c-.109-.063-.064-.23.061-.23"/></svg>',
  perplexity: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M22.3977 7.0896h-2.3106V.0676l-7.5094 6.3542V.1577h-1.1554v6.1966L4.4904 0v7.0896H1.6023v10.3976h2.8882V24l6.932-6.3591v6.2005h1.1554v-6.0469l6.9318 6.1807v-6.4879h2.8882V7.0896zm-3.4657-4.531v4.531h-5.355l5.355-4.531zm-13.2862.0676 4.8691 4.4634H5.6458V2.6262zM2.7576 16.332V8.245h7.8476l-6.1149 6.1147v1.9723H2.7576zm2.8882 5.0404v-3.8852h.0001v-2.6488l5.7763-5.7764v7.0111l-5.7764 5.2993zm12.7086.0248-5.7766-5.1509V9.0618l5.7766 5.7766v6.5588zm2.8882-5.0652h-1.733v-1.9723L13.3948 8.245h7.8478v8.087z"/></svg>',
  grok: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="m19.25 5.08l-9.52 9.67l6.64-4.96c.33-.24.79-.15.95.23c.82 1.99.45 4.39-1.17 6.03c-1.63 1.64-3.89 2.01-5.96 1.18l-2.26 1.06c3.24 2.24 7.18 1.69 9.64-.8c1.95-1.97 2.56-4.66 1.99-7.09c-.82-3.56.2-4.98 2.29-7.89L22 2.3zm-9.53 9.67h.01zm-1.37 1.21c-2.33-2.25-1.92-5.72.06-7.73c1.47-1.48 3.87-2.09 5.97-1.2l2.25-1.05c-.41-.3-.93-.62-1.52-.84a7.45 7.45 0 0 0-8.13 1.65c-2.11 2.14-2.78 5.42-1.63 8.22c.85 2.09-.54 3.57-1.95 5.07c-.5.53-1 1.06-1.4 1.62z"/></svg>',
}

const PROVIDERS = [
  { label: 'Open in ChatGPT', icon: ICONS.chatgpt, url: (p: string) => 'https://chatgpt.com/?q=' + encodeURIComponent(p) },
  { label: 'Open in Claude', icon: ICONS.claude, url: (p: string) => 'https://claude.ai/new?q=' + encodeURIComponent(p) },
  { label: 'Open in Cursor', icon: ICONS.cursor, url: (p: string) => 'https://cursor.com/link/prompt?text=' + encodeURIComponent(p) },
  { label: 'Open in Perplexity', icon: ICONS.perplexity, url: (p: string) => 'https://www.perplexity.ai/?q=' + encodeURIComponent(p) },
  { label: 'Open in Grok', icon: ICONS.grok, url: (p: string) => 'https://grok.com/?q=' + encodeURIComponent(p) },
]

const route = useRoute()
const { page } = useData()

// The same-origin Markdown twin: vitepress-plugin-llms mirrors each page to a
// sibling `.md` file. Derive its relative path from the current page path.
const mdRel = computed(() => withBase('/' + page.value.relativePath.replace(/\.md$/, '') + '.md'))
const mdAbs = ref('')

const open = ref(false)
const toastMsg = ref('')
let toastTimer: ReturnType<typeof setTimeout> | undefined

// The button is teleported onto the anchor that the markdown-it rule drops
// after each page's intro lede, so it renders below the title and opening text.
const target = ref<HTMLElement | null>(null)
async function locateAnchor() {
  target.value = null
  await nextTick()
  target.value = document.querySelector<HTMLElement>('.vp-llm-copy-anchor')
}

function showToast(msg: string) {
  toastMsg.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toastMsg.value = ''), 2200)
}

async function copyText(text: string) {
  if (navigator.clipboard?.writeText) return navigator.clipboard.writeText(text)
  const ta = document.createElement('textarea')
  ta.value = text
  ta.style.cssText = 'position:fixed;opacity:0'
  document.body.appendChild(ta)
  ta.select()
  document.execCommand('copy')
  document.body.removeChild(ta)
}

async function copyPage() {
  try {
    const res = await fetch(mdAbs.value)
    if (!res.ok) throw new Error(String(res.status))
    await copyText(await res.text())
    showToast('Page copied as Markdown')
  } catch {
    showToast("Couldn't copy this page")
  }
}

async function copyLink() {
  await copyText(mdAbs.value)
  showToast('Markdown link copied')
}

const prompt = () => 'I have a question about this documentation page: ' + mdAbs.value

function openIn(url: (p: string) => string) {
  open.value = false
  window.open(url(prompt()), '_blank', 'noopener')
}

function onOutside(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('.llm-copy')) open.value = false
}
function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') open.value = false
}

onMounted(() => {
  mdAbs.value = new URL(mdRel.value, location.href).href
  document.addEventListener('click', onOutside, true)
  document.addEventListener('keydown', onKey, true)
  locateAnchor()
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onOutside, true)
  document.removeEventListener('keydown', onKey, true)
})
watch(() => route.path, () => {
  if (typeof location !== 'undefined') mdAbs.value = new URL(mdRel.value, location.href).href
  open.value = false
  locateAnchor()
})
</script>

<template>
  <Teleport v-if="target" :to="target">
  <div class="llm-copy">
    <button type="button" class="llm-btn llm-btn-main" @click="copyPage">
      <span v-html="ICONS.copy" /><span class="llm-btn-text">Copy page</span>
    </button>
    <button
      type="button"
      class="llm-btn llm-btn-caret"
      aria-haspopup="menu"
      :aria-expanded="open"
      aria-label="More copy options"
      @click="open = !open"
    >
      <span v-html="ICONS.chevron" />
    </button>
    <div v-show="open" class="llm-menu" role="menu">
      <button type="button" class="llm-menu-item" role="menuitem" @click="open = false; copyPage()">
        <span v-html="ICONS.copy" /><span class="llm-menu-label">Copy page as Markdown</span>
      </button>
      <button type="button" class="llm-menu-item" role="menuitem" @click="open = false; copyLink()">
        <span v-html="ICONS.link" /><span class="llm-menu-label">Copy markdown link</span>
      </button>
      <a class="llm-menu-item" role="menuitem" :href="mdAbs" target="_blank" rel="noopener" @click="open = false">
        <span v-html="ICONS.markdown" /><span class="llm-menu-label">View Markdown</span><span v-html="ICONS.external" />
      </a>
      <div class="llm-menu-sep" role="separator" />
      <button
        v-for="p in PROVIDERS"
        :key="p.label"
        type="button"
        class="llm-menu-item"
        role="menuitem"
        @click="openIn(p.url)"
      >
        <span v-html="p.icon" /><span class="llm-menu-label">{{ p.label }}</span><span v-html="ICONS.external" />
      </button>
    </div>
  </div>
  </Teleport>
  <Teleport to="body">
    <div class="llm-toast" :class="{ 'llm-toast--show': toastMsg }">{{ toastMsg }}</div>
  </Teleport>
</template>

<style>
.llm-copy {
  position: relative;
  display: inline-flex;
  flex: 0 0 auto;
  /* Sits between the intro lede and the first section heading, whose own
     top margin provides the spacing below — so only a small top gap here. */
  margin: 0.25rem 0 0;
  font-size: 0.78rem;
  white-space: nowrap;
}
.llm-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  height: 2rem;
  padding: 0 0.7em;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-2);
  font: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s, border-color 0.15s;
}
.llm-btn svg { flex: 0 0 auto; }
.llm-btn:hover { background: var(--vp-c-bg-soft); color: var(--vp-c-text-1); }
.llm-btn-main { border-radius: 0.4rem 0 0 0.4rem; }
.llm-btn-caret { border-radius: 0 0.4rem 0.4rem 0; border-left: 0; padding: 0 0.35em; }
.llm-btn-caret[aria-expanded='true'] { background: var(--vp-c-bg-soft); color: var(--vp-c-text-1); }

.llm-menu {
  position: absolute;
  top: calc(100% + 0.35rem);
  left: 0;
  z-index: 30;
  min-width: 15rem;
  padding: 0.3rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 0.6rem;
  background: var(--vp-c-bg);
  box-shadow: var(--vp-shadow-3);
}
.llm-menu-item {
  display: flex;
  align-items: center;
  gap: 0.6em;
  width: 100%;
  padding: 0.45rem 0.55rem;
  border: 0;
  border-radius: 0.4rem;
  background: transparent;
  color: var(--vp-c-text-1);
  font: inherit;
  text-align: left;
  cursor: pointer;
  text-decoration: none;
}
.llm-menu-item:hover { background: var(--vp-c-bg-soft); }
.llm-menu-sep { height: 1px; margin: 0.3rem 0.45rem; background: var(--vp-c-divider); }
.llm-menu-label { flex: 1 1 auto; }
.llm-menu-item .llm-ext { color: var(--vp-c-text-3); opacity: 0.8; }

.llm-toast {
  position: fixed;
  left: 50%;
  bottom: 1.5rem;
  transform: translate(-50%, 1rem);
  z-index: 1000;
  padding: 0.5rem 0.9rem;
  border-radius: 0.4rem;
  background: var(--vp-c-brand-1);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 500;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s, transform 0.2s;
}
.llm-toast--show { opacity: 1; transform: translate(-50%, 0); }
</style>
