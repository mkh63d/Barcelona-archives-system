<template>
  <div class="flex h-screen bg-dark-300 overflow-hidden">
    <!-- Sidebar Component -->
    <Sidebar />

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <!-- Mobile Sidebar Toggle -->
      <div class="lg:hidden p-4 border-b border-dark-100">
        <button class="text-gray-400 hover:text-primary">
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
import Sidebar from './components/Sidebar.vue'
</script>
