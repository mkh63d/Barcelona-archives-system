<template>
  <aside 
    class="w-64 bg-dark-400 border-r border-dark-100 flex flex-col transition-all duration-300"
    :class="{ '-ml-64': !sidebarOpen }"
  >
    <!-- Sidebar Header -->
    <div class="p-4 border-b border-dark-100">
      <div class="flex lg:items-center lg:justify-between justify-center">
        <img src="../assets/logotip.svg" alt="Barcelona Archives" class="h-10" />
        <button @click="toggleSidebar" class="lg:hidden text-gray-400 hover:text-primary">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- New Chat Button -->
    <div class="p-3">
      <button 
        @click="createNewChat"
        class="w-full btn-primary flex items-center justify-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Chat
      </button>
    </div>

    <!-- Search Conversations -->
    <div class="px-3 pb-3">
      <input
        v-model="searchQuery"
        placeholder="Search conversations..."
        class="w-full bg-dark-300 text-gray-100 px-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      />
    </div>

    <!-- Chat History -->
    <div class="flex-1 overflow-y-auto p-3 space-y-2">
      <div class="text-xs text-gray-500 uppercase tracking-wider mb-2">Recent</div>
      
      <!-- Loading State -->
      <div v-if="isLoading" class="text-sm text-gray-500 text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
        <p class="mt-2">Loading...</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="filteredConversations.length === 0" class="text-sm text-gray-500 text-center py-8">
        {{ searchQuery ? 'No conversations found' : 'No conversations yet' }}
      </div>
      
      <!-- Conversations List -->
      <div 
        v-else
        v-for="chat in filteredConversations" 
        :key="chat.id"
        @click="selectChat(chat.id)"
        class="p-3 rounded-lg cursor-pointer transition-colors group relative"
        :class="currentChatId === chat.id ? 'bg-dark-200 border-2 border-primary' : 'bg-dark-300 hover:bg-dark-200 border-2 border-transparent'"
      >
        <div class="text-sm text-gray-100 font-medium truncate mb-1">{{ chat.title }}</div>
        <div v-if="chat.messages && chat.messages.length > 0" class="text-xs text-gray-500 truncate mb-1">
          {{ chat.messages[chat.messages.length - 1].content.substring(0, 40) }}...
        </div>
        <div class="text-xs text-gray-500">
          {{ chat.messages?.length || 0 }} msgs • {{ formatDate(chat.updatedAt) }}
        </div>
        
        <!-- Delete Button -->
        <button
          v-if="currentChatId === chat.id"
          @click.stop="deleteChat(chat.id)"
          class="absolute top-2 right-2 p-1 bg-red-900/20 hover:bg-red-900/40 rounded transition-colors"
          title="Delete"
        >
          <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Sidebar Footer -->
    <div class="p-4 border-t border-dark-100 space-y-3">
      <button
        @click="$router.push('/settings')"
        class="w-full p-3 rounded-lg bg-dark-300 hover:bg-dark-200 transition-colors flex items-center gap-3"
      >
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span class="text-sm text-gray-300">Settings</span>
      </button>
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
          <span class="text-white text-sm font-semibold">U</span>
        </div>
        <div class="flex-1">
          <div class="text-sm text-gray-100">User</div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, provide } from 'vue'
import { useRouter } from 'vue-router'
import { conversationService } from '../db.js'

const router = useRouter()

const currentChatId = ref(null)
const sidebarOpen = ref(true)
const conversations = ref([])
const searchQuery = ref('')
const isLoading = ref(true)

// Provide currentChatId to child components (like Home.vue)
provide('currentChatId', currentChatId)

const filteredConversations = computed(() => {
  if (!searchQuery.value) return conversations.value
  return conversations.value.filter(conv => 
    conv.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    conv.messages?.some(msg => 
      msg.content.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  )
})

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

const loadConversations = async () => {
  conversations.value = await conversationService.getAllConversations()
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const createNewChat = async () => {
  const conversation = await conversationService.createConversation()
  currentChatId.value = conversation.id
  await loadConversations()
  
  // Navigate to home and trigger new chat
  if (router.currentRoute.value.path !== '/') {
    router.push('/')
  }
  
  window.dispatchEvent(new CustomEvent('new-chat', { detail: conversation.id }))
}

const selectChat = async (id) => {
  console.log('Sidebar: selectChat called with id:', id)
  currentChatId.value = id
  
  // Navigate to home if not already there
  if (router.currentRoute.value.path !== '/') {
    router.push('/')
  }
  
  console.log('Sidebar: dispatching load-chat event')
  window.dispatchEvent(new CustomEvent('load-chat', { detail: id }))
}

const deleteChat = async (id) => {
  if (confirm('Delete this conversation?')) {
    await conversationService.deleteConversation(id)
    await loadConversations()
    
    if (currentChatId.value === id) {
      await createNewChat()
    }
  }
}

// Expose reload function for Home.vue
window.reloadConversations = loadConversations

onMounted(async () => {
  try {
    console.log('Sidebar mounted, loading conversations...')
    await loadConversations()
    console.log('Conversations loaded:', conversations.value.length)
    
    if (conversations.value.length > 0) {
      currentChatId.value = conversations.value[0].id
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('load-chat', { detail: conversations.value[0].id }))
      }, 100)
    } else {
      console.log('No conversations found, creating new one')
      await createNewChat()
    }
  } catch (error) {
    console.error('Error initializing sidebar:', error)
    const conversation = await conversationService.createConversation()
    conversations.value = [conversation]
    currentChatId.value = conversation.id
  } finally {
    isLoading.value = false
  }
})
</script>
