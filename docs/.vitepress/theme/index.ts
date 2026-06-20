import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
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
}
