<template>
  <div class="flex flex-col h-full bg-dark-300">
    <!-- Header -->
    <div class="border-b border-dark-100 bg-dark-400">
      <div class="px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <button 
            @click="goBack"
            class="text-gray-400 hover:text-gray-100 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <div>
            <h1 class="text-xl font-bold text-gray-100">Source Document</h1>
            <p class="text-sm text-gray-400">{{ source?.filename || 'Loading...' }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div v-if="!loadingDocument" class="flex items-center gap-2">
            <span class="text-xs text-gray-400">Relevance:</span>
            <div class="w-24 h-2 bg-dark-300 rounded-full overflow-hidden">
              <div 
                class="h-full bg-primary rounded-full transition-all"
                :style="{ width: `${(source?.relevance_score || 0) * 100}%` }"
              ></div>
            </div>
            <span class="text-xs text-gray-500">{{ ((source?.relevance_score || 0) * 100).toFixed(0) }}%</span>
          </div>
          <a 
            v-if="source?.web_url" 
            :href="source.web_url" 
            target="_blank"
            rel="noopener noreferrer"
            class="px-4 py-2 bg-primary hover:bg-primary-600 text-white rounded-lg transition-colors font-medium flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Open Original
          </a>
        </div>
      </div>

      <!-- Censorship Warning -->
      <div v-if="source?.has_watermark" class="px-6 pb-4">
        <div class="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-sm text-yellow-300 flex items-start gap-3">
          <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>This document was checked by censorship. The real interpretation might differ from reality.</span>
        </div>
      </div>

      <!-- Loading indicator -->
      <div v-if="loadingDocument" class="px-6 pb-4">
        <div class="p-3 bg-dark-300 border border-dark-100 rounded-lg text-sm text-gray-400 flex items-center gap-3">
          <svg class="animate-spin w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Loading full document...</span>
        </div>
      </div>
    </div>

    <!-- Side-by-Side Comparison -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Left Panel - Rendered Markdown -->
      <div class="flex-1 flex flex-col border-r border-dark-100">
        <div class="px-6 py-3 bg-dark-400 border-b border-dark-100">
          <h2 class="text-sm font-semibold text-gray-100 uppercase tracking-wider">Rendered Content</h2>
          <p class="text-xs text-gray-400 mt-1">Markdown formatted view of the full document</p>
        </div>
        <div class="flex-1 overflow-y-auto px-6 py-6" ref="renderedContainer">
          <div v-if="loadingDocument" class="text-gray-400 text-center py-12">
            Loading document...
          </div>
          <div v-else>
            <div 
              class="prose prose-invert prose-sm max-w-none"
              v-html="renderMarkdownWithHighlight(fullDocument)"
            ></div>
          </div>
        </div>
      </div>

      <!-- Right Panel - Original Document -->
      <div class="flex-1 flex flex-col">
        <div class="px-6 py-3 bg-dark-400 border-b border-dark-100">
          <h2 class="text-sm font-semibold text-gray-100 uppercase tracking-wider">Original Text</h2>
          <p class="text-xs text-gray-400 mt-1">Raw source document content</p>
        </div>
        <div class="flex-1 overflow-y-auto px-6 py-6" ref="originalContainer">
          <div v-if="loadingDocument" class="text-gray-400 text-center py-12">
            Loading document...
          </div>
          <pre v-else class="text-sm text-gray-300 whitespace-pre-wrap font-mono leading-relaxed" v-html="highlightChunkInOriginal(fullDocument)"></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import axios from 'axios'

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true
})

const route = useRoute()
const router = useRouter()
const source = ref(null)
const fullDocument = ref('')
const loadingDocument = ref(true)
const renderedContainer = ref(null)
const originalContainer = ref(null)

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

onMounted(async () => {
  // Get source data from route state
  if (route.params.source) {
    try {
      source.value = JSON.parse(decodeURIComponent(route.params.source))
      
      // Fetch the full document
      await fetchFullDocument()
    } catch (e) {
      console.error('Failed to parse source data:', e)
      loadingDocument.value = false
    }
  }
})

const fetchFullDocument = async () => {
  if (!source.value?.filename) {
    loadingDocument.value = false
    return
  }

  try {
    loadingDocument.value = true
    const response = await axios.get(`${apiUrl}/api/document/${source.value.filename}`)
    fullDocument.value = response.data.content
    
    // After document loads, scroll to the chunk
    await nextTick()
    scrollToChunk()
  } catch (error) {
    console.error('Failed to load full document:', error)
    // Fallback to preview if full document can't be loaded
    fullDocument.value = source.value.preview
  } finally {
    loadingDocument.value = false
  }
}

const escapeHtml = (text) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return text.replace(/[&<>"']/g, m => map[m])
}

const findChunkInDocument = (fullDoc, chunk) => {
  // Try to find the exact chunk
  const chunkTrimmed = chunk.trim()
  let index = fullDoc.indexOf(chunkTrimmed)
  
  if (index === -1) {
    // Try first 100 characters of chunk
    const chunkStart = chunkTrimmed.substring(0, 100)
    index = fullDoc.indexOf(chunkStart)
  }
  
  if (index === -1) {
    // Try fuzzy match with first line
    const firstLine = chunkTrimmed.split('\n')[0].trim()
    if (firstLine.length > 20) {
      index = fullDoc.indexOf(firstLine)
    }
  }
  
  return index
}

const highlightChunkInOriginal = (fullDoc) => {
  if (!fullDoc || !source.value?.preview) return escapeHtml(fullDoc)
  
  const chunkIndex = findChunkInDocument(fullDoc, source.value.preview)
  
  if (chunkIndex === -1) {
    // If chunk not found, return full document
    return escapeHtml(fullDoc)
  }
  
  const chunkLength = source.value.preview.trim().length
  const before = fullDoc.substring(0, chunkIndex)
  const chunk = fullDoc.substring(chunkIndex, chunkIndex + chunkLength)
  const after = fullDoc.substring(chunkIndex + chunkLength)
  
  return (
    escapeHtml(before) +
    '<mark class="bg-primary/50 text-gray-100 px-1 rounded" id="highlighted-chunk">' +
    escapeHtml(chunk) +
    '</mark>' +
    escapeHtml(after)
  )
}

const renderMarkdownWithHighlight = (fullDoc) => {
  if (!fullDoc) return ''
  
  // Render markdown
  let rendered = marked(fullDoc)
  
  // If we have a chunk, try to highlight it in the rendered HTML
  if (source.value?.preview) {
    const chunkPreview = source.value.preview.trim()
    const firstLine = chunkPreview.split('\n')[0].trim()
    
    // Try to find and highlight the first line in rendered HTML
    if (firstLine.length > 20) {
      // Create a simple highlight by wrapping content
      const escapedFirstLine = firstLine.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const regex = new RegExp(`(${escapedFirstLine})`, 'i')
      rendered = rendered.replace(regex, '<mark class="bg-primary/30 px-1 rounded" id="highlighted-chunk">$1</mark>')
    }
  }
  
  return rendered
}

const scrollToChunk = () => {
  // Wait a bit for DOM to update
  setTimeout(() => {
    const highlighted = document.getElementById('highlighted-chunk')
    if (highlighted) {
      // Scroll in both containers
      if (renderedContainer.value) {
        const renderedHighlight = renderedContainer.value.querySelector('#highlighted-chunk')
        if (renderedHighlight) {
          renderedHighlight.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }
      if (originalContainer.value) {
        const originalHighlight = originalContainer.value.querySelector('#highlighted-chunk')
        if (originalHighlight) {
          originalHighlight.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }
    }
  }, 100)
}

const renderMarkdown = (content) => {
  return marked(content || '')
}

const goBack = () => {
  // If we have a 'from' query parameter (conversation ID), navigate to that chat
  const fromConversationId = route.query.from
  if (fromConversationId) {
    router.push(`/chat/${fromConversationId}`)
  } else {
    // Fallback to browser back
    router.back()
  }
}
</script>

<style scoped>
/* Custom scrollbar for better aesthetics */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
  background: #3a3a3a;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4a4a4a;
}

/* Highlight styling */
:deep(mark) {
  animation: highlight-fade 2s ease-in-out;
}

@keyframes highlight-fade {
  0% {
    background-color: rgba(0, 150, 57, 0.5);
  }
  50% {
    background-color: rgba(0, 150, 57, 0.3);
  }
  100% {
    background-color: rgba(0, 150, 57, 0.3);
  }
}
</style>
