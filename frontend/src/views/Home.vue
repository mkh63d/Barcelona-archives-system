<template>
  <div class="flex flex-col h-full">
    <!-- Top Bar with Conversation Controls -->
    <div class="bg-dark-400 border-b border-dark-100 px-4 py-3">
      <div class="max-w-3xl mx-auto flex items-center justify-between gap-4">
        <!-- Conversation Title -->
        <div class="flex-1 flex items-center gap-3">
          <button
            @click="showConversationList = !showConversationList"
            class="p-2 hover:bg-dark-200 rounded-lg transition-colors"
            title="Conversations"
          >
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <input
            v-if="editingTitle"
            v-model="currentTitle"
            @blur="saveTitle"
            @keyup.enter="saveTitle"
            class="flex-1 bg-dark-300 text-gray-100 px-3 py-1 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Conversation title..."
          />
          <h1 v-else @click="editingTitle = true" class="text-gray-100 font-semibold cursor-pointer hover:text-primary transition-colors">
            {{ currentTitle }}
          </h1>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-2">
          <button
            @click="startNewConversation"
            class="p-2 hover:bg-dark-200 rounded-lg transition-colors"
            title="New conversation"
          >
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </button>
          <button
            v-if="currentConversationId"
            @click="exportCurrentConversation"
            class="p-2 hover:bg-dark-200 rounded-lg transition-colors"
            title="Export conversation"
          >
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
          <button
            v-if="currentConversationId"
            @click="deleteCurrentConversation"
            class="p-2 hover:bg-red-900/20 rounded-lg transition-colors"
            title="Delete conversation"
          >
            <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Conversation List Sidebar -->
    <div
      v-if="showConversationList"
      class="absolute top-14 left-0 w-80 h-[calc(100%-56px)] bg-dark-400 border-r border-dark-100 z-10 overflow-y-auto"
    >
      <div class="p-4">
        <h2 class="text-lg font-bold text-gray-100 mb-4">Conversations</h2>
        
        <!-- Search -->
        <input
          v-model="searchQuery"
          placeholder="Search conversations..."
          class="w-full bg-dark-300 text-gray-100 px-3 py-2 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-primary"
        />

        <!-- Conversation List -->
        <div class="space-y-2">
          <div
            v-for="conv in filteredConversations"
            :key="conv.id"
            @click="loadConversation(conv.id)"
            class="p-3 bg-dark-300 hover:bg-dark-200 rounded-lg cursor-pointer transition-colors"
            :class="{ 'ring-2 ring-primary': conv.id === currentConversationId }"
          >
            <h3 class="text-sm font-semibold text-gray-100 mb-1 truncate">{{ conv.title }}</h3>
            <p class="text-xs text-gray-500">
              {{ conv.messages.length }} messages • {{ formatDate(conv.updatedAt) }}
            </p>
          </div>
        </div>

        <div v-if="filteredConversations.length === 0" class="text-center text-gray-500 py-8">
          No conversations found
        </div>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto" ref="messagesContainer">
      <!-- Welcome State -->
      <div v-if="messages.length === 0" class="h-full flex items-center justify-center">
        <div class="max-w-2xl mx-auto text-center px-4">
          <div class="mb-8">
            <div class="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
            </div>
            <h2 class="text-3xl font-bold text-gray-100 mb-3">Barcelona Archives Assistant</h2>
            <p class="text-gray-400 text-lg">Ask me anything about historical archives, documents, or search for specific records.</p>
          </div>

          <!-- Example Prompts -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-3xl mx-auto">
            <button 
              v-for="example in examplePrompts" 
              :key="example"
              @click="sendMessage(example)"
              class="p-4 bg-dark-400 hover:bg-dark-200 border border-dark-100 hover:border-primary rounded-xl text-left transition-all"
            >
              <p class="text-gray-300 text-sm">{{ example }}</p>
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div v-else class="max-w-3xl mx-auto px-4 py-8 space-y-6">
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          class="flex gap-4"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <!-- Assistant Avatar -->
          <div v-if="message.role === 'assistant'" class="flex-shrink-0">
            <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>

          <!-- Message Content -->
          <div 
            class="max-w-[80%] rounded-2xl px-4 py-3"
            :class="message.role === 'user' 
              ? 'bg-primary text-white' 
              : 'bg-dark-400 text-gray-100 border border-dark-100'"
          >
            <div 
              class="text-sm leading-relaxed prose prose-invert prose-sm max-w-none"
              :class="message.role === 'user' ? 'prose-headings:text-white prose-p:text-white prose-li:text-white prose-strong:text-white' : ''"
              v-html="renderMarkdown(message.content)"
            ></div>
            
            <!-- Sources Section (NotebookLM style) -->
            <div v-if="message.role === 'assistant' && message.sources && message.sources.length > 0" class="mt-4 pt-4 border-t border-dark-200">
              <div class="text-xs text-gray-400 mb-2 font-semibold uppercase tracking-wider">Sources</div>
              <div class="space-y-2">
                <div 
                  v-for="(source, idx) in message.sources" 
                  :key="idx"
                  class="group relative bg-dark-300 hover:bg-dark-200 border border-dark-200 hover:border-primary rounded-lg p-3 cursor-pointer transition-all"
                  @click="toggleSource(index, idx)"
                >
                  <div class="flex items-start gap-3">
                    <!-- Source Number Badge -->
                    <div class="flex-shrink-0 w-6 h-6 bg-primary rounded flex items-center justify-center">
                      <span class="text-white text-xs font-bold">{{ idx + 1 }}</span>
                    </div>
                    
                    <!-- Source Info -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-1">
                        <svg class="w-4 h-4 text-primary flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span class="text-sm font-semibold text-gray-100 truncate">{{ source.filename }}</span>
                      </div>
                      
                      <!-- Relevance Score -->
                      <div class="flex items-center gap-2 mb-2">
                        <div class="flex-1 h-1.5 bg-dark-400 rounded-full overflow-hidden">
                          <div 
                            class="h-full bg-primary rounded-full transition-all"
                            :style="{ width: `${source.relevance_score * 100}%` }"
                          ></div>
                        </div>
                        <span class="text-xs text-gray-500">{{ (source.relevance_score * 100).toFixed(0) }}% match</span>
                      </div>
                      
                      <!-- Preview (expandable) -->
                      <div 
                        v-if="message.expandedSources && message.expandedSources.includes(idx)"
                        class="text-xs text-gray-400 mt-2 p-2 bg-dark-400 rounded border border-dark-100"
                      >
                        {{ source.preview }}
                      </div>
                      <div v-else class="text-xs text-gray-500 line-clamp-2">
                        {{ source.preview }}
                      </div>
                    </div>
                    
                    <!-- Expand Icon -->
                    <svg 
                      class="w-4 h-4 text-gray-500 group-hover:text-primary transition-transform flex-shrink-0"
                      :class="{ 'rotate-180': message.expandedSources && message.expandedSources.includes(idx) }"
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- User Avatar -->
          <div v-if="message.role === 'user'" class="flex-shrink-0">
            <div class="w-8 h-8 bg-dark-200 rounded-lg flex items-center justify-center">
              <span class="text-primary text-sm font-semibold">U</span>
            </div>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="isTyping" class="flex gap-4 justify-start">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
          <div class="bg-dark-400 border border-dark-100 rounded-2xl px-4 py-3">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t border-dark-100 bg-dark-300">
      <div class="max-w-3xl mx-auto p-4">
        <form @submit.prevent="handleSubmit" class="relative">
          <textarea
            v-model="inputMessage"
            @keydown.enter.exact.prevent="handleSubmit"
            placeholder="Ask about archives, documents, or historical records..."
            rows="1"
            class="w-full bg-dark-400 border border-dark-100 text-gray-100 rounded-2xl px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none max-h-32"
            style="min-height: 52px;"
          ></textarea>
          <button
            type="submit"
            :disabled="!inputMessage.trim() || isTyping"
            class="absolute right-2 bottom-2 w-8 h-8 bg-primary hover:bg-primary-600 disabled:bg-dark-200 disabled:cursor-not-allowed rounded-lg flex items-center justify-center transition-colors"
          >
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </button>
        </form>
        <p class="text-xs text-gray-500 text-center mt-2">
          Press Enter to send, Shift + Enter for new line
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { marked } from 'marked'
import { conversationService } from '../db.js'

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true
})

const messages = ref([])
const inputMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref(null)

// Conversation management
const currentConversationId = ref(null)
const currentTitle = ref('New Conversation')
const conversations = ref([])
const showConversationList = ref(false)
const editingTitle = ref(false)
const searchQuery = ref('')

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const examplePrompts = [
  'What notable film was being heavily promoted at the time, and how was it described to audiences?',
  'Which movie was portrayed as a dramatic odyssey against communist oppression?',
  'What major film studio was associated with the release of this movie?',
  'What kind of political authority is depicted as exerting control over the characters?'
]

const renderMarkdown = (content) => {
  return marked(content)
}

// Computed property for filtered conversations
const filteredConversations = computed(() => {
  if (!searchQuery.value) return conversations.value
  return conversations.value.filter(conv => 
    conv.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    conv.messages.some(msg => 
      msg.content.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  )
})

// Format date helper
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMs = now - date
  const diffInMins = Math.floor(diffInMs / 60000)
  const diffInHours = Math.floor(diffInMs / 3600000)
  const diffInDays = Math.floor(diffInMs / 86400000)

  if (diffInMins < 1) return 'Just now'
  if (diffInMins < 60) return `${diffInMins}m ago`
  if (diffInHours < 24) return `${diffInHours}h ago`
  if (diffInDays < 7) return `${diffInDays}d ago`
  return date.toLocaleDateString()
}

// Auto-save messages when they change
watch(messages, async (newMessages) => {
  if (currentConversationId.value && newMessages.length > 0) {
    await conversationService.updateConversation(
      currentConversationId.value,
      newMessages
    )
    await loadConversationList()
  }
}, { deep: true })

// Load conversations list
const loadConversationList = async () => {
  conversations.value = await conversationService.getAllConversations()
}

// Start new conversation
const startNewConversation = async () => {
  const conversation = await conversationService.createConversation()
  currentConversationId.value = conversation.id
  currentTitle.value = conversation.title
  messages.value = []
  await loadConversationList()
  showConversationList.value = false
}

// Load a conversation
const loadConversation = async (id) => {
  const conversation = await conversationService.getConversation(id)
  if (conversation) {
    currentConversationId.value = conversation.id
    currentTitle.value = conversation.title
    messages.value = conversation.messages
    showConversationList.value = false
    scrollToBottom()
  }
}

// Save conversation title
const saveTitle = async () => {
  editingTitle.value = false
  if (currentConversationId.value && currentTitle.value.trim()) {
    await conversationService.updateTitle(
      currentConversationId.value,
      currentTitle.value
    )
    await loadConversationList()
  }
}

// Export conversation
const exportCurrentConversation = async () => {
  if (currentConversationId.value) {
    await conversationService.exportConversation(currentConversationId.value)
  }
}

// Delete conversation
const deleteCurrentConversation = async () => {
  if (currentConversationId.value && confirm('Delete this conversation?')) {
    await conversationService.deleteConversation(currentConversationId.value)
    await loadConversationList()
    await startNewConversation()
  }
}

// Initialize on mount
onMounted(async () => {
  await loadConversationList()
  if (conversations.value.length > 0) {
    // Load the most recent conversation
    await loadConversation(conversations.value[0].id)
  } else {
    // Create first conversation
    await startNewConversation()
  }
})

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async (content) => {
  if (!content.trim()) return
  
  // Add user message
  messages.value.push({
    role: 'user',
    content: content
  })
  
  inputMessage.value = ''
  scrollToBottom()
  
  // Show typing indicator
  isTyping.value = true
  
  try {
    // Call RAG chat endpoint
    const response = await axios.post(`${apiUrl}/api/chat`, {
      message: content
    })
    
    messages.value.push({
      role: 'assistant',
      content: response.data.response,
      sources: response.data.sources || [],
      context_used: response.data.context_used || false,
      num_sources: response.data.num_sources || 0,
      expandedSources: [] // Track which sources are expanded
    })
  } catch (error) {
    let errorMessage = "I'm having trouble processing your request. "
    
    if (error.response?.status === 400 && error.response?.data?.detail?.includes('API_KEY')) {
      errorMessage += "Please configure your AI model API key in Settings."
    } else if (error.response?.data?.detail) {
      errorMessage += error.response.data.detail
    } else {
      errorMessage += "Please make sure the backend service is running and configured properly."
    }
    
    messages.value.push({
      role: 'assistant',
      content: errorMessage,
      sources: []
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const toggleSource = (messageIndex, sourceIndex) => {
  const message = messages.value[messageIndex]
  if (!message.expandedSources) {
    message.expandedSources = []
  }
  
  const idx = message.expandedSources.indexOf(sourceIndex)
  if (idx > -1) {
    message.expandedSources.splice(idx, 1)
  } else {
    message.expandedSources.push(sourceIndex)
  }
}

const handleSubmit = () => {
  if (inputMessage.value.trim() && !isTyping.value) {
    sendMessage(inputMessage.value)
  }
}
</script>
