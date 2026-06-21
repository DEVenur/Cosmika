import DefaultTheme from 'vitepress/theme'
import { h, nextTick, onMounted, watch } from 'vue'
import { useRoute } from 'vitepress'
import CopyForLLM from './CopyForLLM.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    // Render the "Copy for LLM" split button at the top of every doc page.
    return h(DefaultTheme.Layout, null, {
      'doc-before': () => h(CopyForLLM),
    })
  },
  setup() {
    // Update the footer copyright year to the visitor's current year at
    // runtime (the build-time value in config is only the SSR/no-JS fallback).
    const syncYear = () => {
      const year = String(new Date().getFullYear())
      document.querySelectorAll('.footer-year').forEach((el) => {
        el.textContent = year
      })
    }
    // Wrap the trailing "Agent" word of the hero title so CSS can glow it.
    const glowAgent = () => {
      const el = document.querySelector('.VPHero .text')
      if (!el || el.querySelector('.glow-agent')) return
      el.innerHTML = el.innerHTML.replace(
        /Agent(?=\s*$)/,
        '<span class="glow-agent">Agent</span>',
      )
    }
    const enhance = () => {
      syncYear()
      glowAgent()
    }
    const route = useRoute()
    onMounted(() => {
      enhance()
      // The footer/hero can appear on pages reached via client-side navigation.
      watch(() => route.path, () => nextTick(enhance))
    })
  },
}
