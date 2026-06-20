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
    const route = useRoute()
    onMounted(() => {
      syncYear()
      // The footer can appear on pages reached via client-side navigation.
      watch(() => route.path, () => nextTick(syncYear))
    })
  },
}
