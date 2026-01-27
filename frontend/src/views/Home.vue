<template>
  <div class="flex flex-col h-full">
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
            <div class="text-sm leading-relaxed whitespace-pre-wrap">{{ message.content }}</div>
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
import { ref, nextTick } from 'vue'
import axios from 'axios'

const messages = ref([])
const inputMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref(null)

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const examplePrompts = [
  'Show me historical records from 1900-1920',
  'Find architectural plans from Gothic Quarter',
  'Search for civil registry documents',
  'What photography collections are available?'
]

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
    // Call LangGraph chat endpoint
    const response = await axios.post(`${apiUrl}/api/chat`, {
      message: content
    })
    
    messages.value.push({
      role: 'assistant',
      content: response.data.response
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
      content: errorMessage
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const handleSubmit = () => {
  if (inputMessage.value.trim() && !isTyping.value) {
    sendMessage(inputMessage.value)
  }
}
</script>
