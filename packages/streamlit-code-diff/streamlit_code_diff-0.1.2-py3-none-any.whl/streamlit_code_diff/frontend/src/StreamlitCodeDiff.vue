<template>
  <div class="streamlit-code-diff" :class="`theme-${computedTheme}`">
    <CodeDiff
      v-if="args.old_string || args.new_string"
      :old-string="args.old_string"
      :new-string="args.new_string"
      :language="args.language"
      :output-format="args.output_format"
      :diff-style="args.diff_style"
      :context="args.context"
      :filename="args.filename"
      :new-filename="args.new_filename"
      :theme="computedTheme"
      :trim="args.trim"
      :no-diff-line-feed="args.no_diff_line_feed"
      :hide-header="args.hide_header"
      :hide-stat="args.hide_stat"
      :force-inline-comparison="args.force_inline_comparison"
      :max-height="args.height"
      :ignore-matching-lines="args.ignore_matching_lines"
      @onComplete="onDiffComplete"
    />
    <div v-else class="loading-placeholder">
      <p>Loading diff...</p>
      <pre>{{ JSON.stringify(args, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Streamlit } from 'streamlit-component-lib'
import { CodeDiff } from 'v-code-diff'

interface Args {
  old_string: string
  new_string: string
  language: string
  output_format: 'line-by-line' | 'side-by-side'
  diff_style: 'word' | 'char'
  context: number
  filename?: string
  new_filename?: string
  theme?: 'light' | 'dark'
  trim: boolean
  no_diff_line_feed: boolean
  height?: string
  force_inline_comparison: boolean
  hide_header: boolean
  hide_stat: boolean
  ignore_matching_lines?: string
}

// Component state
const args = ref<Args>({
  old_string: '',
  new_string: '',
  language: 'text',
  output_format: 'side-by-side',
  diff_style: 'word',
  context: 3,
  trim: false,
  no_diff_line_feed: false,
  force_inline_comparison: false,
  hide_header: false,
  hide_stat: false,
})

const theme = ref({ base: 'light' })
const hasReceivedData = ref(false)

// Compute theme based on args or auto-detect from Streamlit
const computedTheme = computed(() => {
  return args.value.theme || (theme.value.base === 'dark' ? 'dark' : 'light')
})

// Debug function to check diff HTML structure
const onDiffComplete = () => {
  if (!args.value.old_string && !args.value.new_string) return

  setTimeout(() => {
    const diffElement = document.querySelector('.streamlit-code-diff .v-code-diff')
    if (diffElement) {
      const insElements = diffElement.querySelectorAll('ins')
      const delElements = diffElement.querySelectorAll('del')
      console.log('Diff rendered with inline elements:', { insElements: insElements.length, delElements: delElements.length })
    }
  }, 100)
}

// Calculate diff statistics
const calculateStats = () => {
  const isChanged = args.value.old_string !== args.value.new_string
  const oldLines = args.value.old_string.split('\n')
  const newLines = args.value.new_string.split('\n')

  let addNum = 0
  let delNum = 0

  if (isChanged) {
    const maxLines = Math.max(oldLines.length, newLines.length)
    for (let i = 0; i < maxLines; i++) {
      const oldLine = oldLines[i] || ""
      const newLine = newLines[i] || ""

      if (i >= oldLines.length) {
        addNum++
      } else if (i >= newLines.length) {
        delNum++
      } else if (oldLine !== newLine) {
        if (oldLine === "") {
          addNum++
        } else if (newLine === "") {
          delNum++
        } else {
          addNum++
          delNum++
        }
      }
    }
  }

  return { isChanged, addNum, delNum }
}

// Update Streamlit with stats and height
const updateStreamlit = async () => {
  // Only send messages after we've received data from Streamlit
  if (!hasReceivedData.value) return

  await nextTick()

  // Send diff statistics to Streamlit
  const stats = calculateStats()
  Streamlit.setComponentValue(stats)

  // Update frame height after content is rendered using actual rendered height
  setTimeout(() => {
    const element = document.querySelector('.streamlit-code-diff') as HTMLElement
    if (element) {
      // Use offsetHeight to get the actual rendered height, respecting max-height
      const height = element.offsetHeight || 400
      Streamlit.setFrameHeight(height + 20) // Minimal padding
    }
  }, 300)
}

// Watch for changes in args
watch(args, () => {
  if (hasReceivedData.value) {
    updateStreamlit()
  }
}, { deep: true })

watch(theme, () => {
  if (hasReceivedData.value) {
    updateStreamlit()
  }
}, { deep: true })

// Initialize component and set up Streamlit integration
onMounted(() => {
  // Set component ready first
  Streamlit.setComponentReady()

  // Set up render event listener
  const handleRender = (event: any) => {
    const eventData = event.detail || event
    const { args: eventArgs, theme: eventTheme } = eventData

    if (eventArgs) {
      args.value = {
        old_string: eventArgs.old_string || '',
        new_string: eventArgs.new_string || '',
        language: eventArgs.language || 'text',
        output_format: eventArgs.output_format || 'side-by-side',
        diff_style: eventArgs.diff_style || 'word',
        context: eventArgs.context || 3,
        filename: eventArgs.filename,
        new_filename: eventArgs.new_filename,
        theme: eventArgs.theme,
        trim: eventArgs.trim || false,
        no_diff_line_feed: eventArgs.no_diff_line_feed || false,
        height: eventArgs.height,
        force_inline_comparison: eventArgs.force_inline_comparison || false,
        hide_header: eventArgs.hide_header || false,
        hide_stat: eventArgs.hide_stat || false,
        ignore_matching_lines: eventArgs.ignore_matching_lines,
      }
    }

    if (eventTheme) {
      theme.value = eventTheme
    }

    // Mark that we've received data from Streamlit
    hasReceivedData.value = true
    updateStreamlit()
  }

  // Use modern Streamlit event handling
  if (Streamlit.events && Streamlit.RENDER_EVENT) {
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, handleRender)
  }

  // Also try window message listener as fallback
  window.addEventListener('message', (event) => {
    if (event.data.type === 'streamlit:render') {
      handleRender(event.data)
    }
  })
})
</script>

<style scoped>
.streamlit-code-diff {
  font-family: 'Consolas', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Courier New', monospace;
  width: 100%;
  margin: 0;
  padding: 0;
}

.loading-placeholder {
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  color: #333;
  margin: 0;
}

.loading-placeholder pre {
  background-color: #eee;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  overflow: auto;
}
</style>