<template>
  <div class="flex h-screen bg-dark-300 overflow-hidden">
    <!-- Sidebar -->
    <aside 
      class="w-64 bg-dark-400 border-r border-dark-100 flex flex-col transition-all duration-300"
      :class="{ '-ml-64': !sidebarOpen }"
    >
      <!-- Sidebar Header -->
      <div class="p-4 border-b border-dark-100">
        <div class="flex lg:items-center lg:justify-between justify-center">
          <img src="./assets/logotip.svg" alt="Barcelona Archives" class="h-10" />
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

      <!-- Chat History -->
      <div class="flex-1 overflow-y-auto p-3 space-y-2">
        <div class="text-xs text-gray-500 uppercase tracking-wider mb-2">Recent</div>
        <div 
          v-for="chat in chatHistory" 
          :key="chat.id"
          @click="selectChat(chat.id)"
          class="p-3 rounded-lg cursor-pointer transition-colors"
          :class="currentChatId === chat.id ? 'bg-dark-200 border border-primary' : 'bg-dark-300 hover:bg-dark-200'"
        >
          <div class="text-sm text-gray-100 font-medium truncate">{{ chat.title }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ chat.date }}</div>
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

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <!-- Mobile Sidebar Toggle -->
      <div class="lg:hidden p-4 border-b border-dark-100">
        <button @click="toggleSidebar" class="text-gray-400 hover:text-primary">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const appName = import.meta.env.VITE_APP_NAME || 'Barcelona Archives System'
const sidebarOpen = ref(true)
const currentChatId = ref(1)

const chatHistory = ref([
  { id: 1, title: 'Historical records query', date: 'Today' },
  { id: 2, title: 'Architecture documents search', date: 'Yesterday' },
  { id: 3, title: 'Municipal archives 1900-1920', date: '2 days ago' },
  { id: 4, title: 'Gothic Quarter buildings', date: '3 days ago' },
  { id: 5, title: 'Civil registry documents', date: 'Last week' }
])

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const createNewChat = () => {
  const newId = Math.max(...chatHistory.value.map(c => c.id)) + 1
  chatHistory.value.unshift({
    id: newId,
    title: 'New conversation',
    date: 'Just now'
  })
  currentChatId.value = newId
}

const selectChat = (id) => {
  currentChatId.value = id
}
</script>
