<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="mb-8">
      <h2 class="text-3xl font-bold text-gray-100 mb-4">Archives</h2>
      
      <div class="flex gap-4 mb-6">
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Search archives..." 
          class="input-field flex-1"
        />
        <button @click="fetchArchives" class="btn-primary">
          Search
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      <p class="text-gray-400 mt-4">Loading archives...</p>
    </div>

    <div v-else-if="error" class="card bg-red-900/20 border-red-500">
      <p class="text-red-400">{{ error }}</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4">
      <div v-for="archive in archives" :key="archive.id" class="card hover:border-primary transition-colors">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h3 class="text-xl font-semibold text-gray-100 mb-2">{{ archive.title }}</h3>
            <p class="text-gray-400 mb-3">{{ archive.description }}</p>
            <div class="flex gap-2">
              <span class="px-3 py-1 bg-dark-400 text-primary text-sm rounded-full">{{ archive.category }}</span>
              <span class="px-3 py-1 bg-dark-400 text-gray-300 text-sm rounded-full">{{ archive.date }}</span>
            </div>
          </div>
          <button class="btn-secondary ml-4">View</button>
        </div>
      </div>

      <div v-if="archives.length === 0" class="card text-center py-12">
        <p class="text-gray-400 text-lg">No archives found. Try connecting to the backend API.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const searchQuery = ref('')
const archives = ref([])
const loading = ref(false)
const error = ref(null)

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const fetchArchives = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get(`${apiUrl}/api/archives`, {
      params: { search: searchQuery.value }
    })
    archives.value = response.data
  } catch (err) {
    error.value = 'Failed to fetch archives. Make sure the backend is running.'
    console.error('Error fetching archives:', err)
    
    // Mock data for demonstration when backend is not available
    archives.value = [
      {
        id: 1,
        title: 'Historical Records 1900-1920',
        description: 'Collection of municipal records from early 20th century Barcelona',
        category: 'Municipal',
        date: '1900-1920'
      },
      {
        id: 2,
        title: 'Architectural Plans',
        description: 'Original architectural drawings of Gothic Quarter buildings',
        category: 'Architecture',
        date: '1850-1900'
      }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchArchives()
})
</script>
