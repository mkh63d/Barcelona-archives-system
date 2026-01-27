<template>
  <div class="flex flex-col h-full">
    <!-- Settings Header -->
    <div class="border-b border-dark-100 p-6">
      <h2 class="text-2xl font-bold text-gray-100 mb-2">Model Settings</h2>
      <p class="text-gray-400">Configure your AI model connection for the archives assistant</p>
    </div>

    <!-- Settings Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-2xl mx-auto space-y-6">
        
        <!-- Connection Status -->
        <div class="card" :class="modelConfig.api_key_set ? 'border-primary' : 'border-yellow-500'">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full flex items-center justify-center"
                 :class="modelConfig.api_key_set ? 'bg-primary' : 'bg-yellow-500'">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="modelConfig.api_key_set" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-100">
                {{ modelConfig.api_key_set ? 'Connected' : 'Not Connected' }}
              </h3>
              <p class="text-sm text-gray-400">
                {{ modelConfig.api_key_set ? 'AI model is ready to use' : 'Please configure your API key below' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Provider Selection -->
        <div class="card">
          <label class="block text-sm font-semibold text-gray-100 mb-3">Model Provider</label>
          <select 
            v-model="formData.provider"
            class="input-field w-full"
          >
            <option v-for="provider in providers" :key="provider.id" :value="provider.id">
              {{ provider.name }}
            </option>
          </select>
          <p class="text-xs text-gray-500 mt-2">Select your preferred AI model provider</p>
        </div>

        <!-- Model Selection -->
        <div class="card">
          <label class="block text-sm font-semibold text-gray-100 mb-3">Model</label>
          <select 
            v-model="formData.model_name"
            class="input-field w-full"
          >
            <option v-for="model in availableModels" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
          <p class="text-xs text-gray-500 mt-2">Choose the specific model to use</p>
        </div>

        <!-- API Key -->
        <div class="card">
          <label class="block text-sm font-semibold text-gray-100 mb-3">
            {{ formData.provider === 'openai' ? 'OpenAI' : formData.provider === 'anthropic' ? 'Anthropic' : 'Google' }} API Key
          </label>
          <div class="relative">
            <input 
              :type="showApiKey ? 'text' : 'password'"
              v-model="formData.api_key"
              placeholder="sk-..."
              class="input-field w-full pr-10"
            />
            <button 
              @click="showApiKey = !showApiKey"
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary"
            >
              <svg v-if="!showApiKey" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-2">
            Get your API key from 
            <a :href="formData.provider === 'openai' ? 'https://platform.openai.com/api-keys' : formData.provider === 'anthropic' ? 'https://console.anthropic.com/' : 'https://aistudio.google.com/app/apikey'" 
               target="_blank" 
               class="text-primary hover:underline">
              {{ formData.provider === 'openai' ? 'OpenAI Platform' : formData.provider === 'anthropic' ? 'Anthropic Console' : 'Google AI Studio' }}
            </a>
          </p>
        </div>

        <!-- Temperature -->
        <div class="card">
          <label class="block text-sm font-semibold text-gray-100 mb-3">
            Temperature: {{ formData.temperature }}
          </label>
          <input 
            type="range"
            v-model.number="formData.temperature"
            min="0"
            max="1"
            step="0.1"
            class="w-full h-2 bg-dark-400 rounded-lg appearance-none cursor-pointer slider"
          />
          <div class="flex justify-between text-xs text-gray-500 mt-2">
            <span>More Focused (0)</span>
            <span>More Creative (1)</span>
          </div>
        </div>

        <!-- Save Button -->
        <div class="flex gap-3">
          <button 
            @click="saveConfig"
            :disabled="saving"
            class="btn-primary flex-1"
          >
            <span v-if="!saving">Save Configuration</span>
            <span v-else>Saving...</span>
          </button>
          <button 
            @click="testConnection"
            :disabled="testing || !formData.api_key"
            class="btn-secondary"
          >
            <span v-if="!testing">Test</span>
            <span v-else>Testing...</span>
          </button>
        </div>

        <!-- Success/Error Messages -->
        <div v-if="message" class="card" :class="message.type === 'success' ? 'border-primary bg-primary/10' : 'border-red-500 bg-red-500/10'">
          <p :class="message.type === 'success' ? 'text-primary' : 'text-red-400'">
            {{ message.text }}
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const modelConfig = ref({
  provider: 'openai',
  model_name: 'gpt-4o-mini',
  temperature: 0.7,
  api_key_set: false
})

const providers = ref([])
const showApiKey = ref(false)
const saving = ref(false)
const testing = ref(false)
const message = ref(null)

const formData = ref({
  provider: 'openai',
  model_name: 'gpt-4o-mini',
  temperature: 0.7,
  api_key: ''
})

const availableModels = computed(() => {
  const provider = providers.value.find(p => p.id === formData.value.provider)
  return provider ? provider.models : []
})

const loadConfig = async () => {
  try {
    const [configRes, providersRes] = await Promise.all([
      axios.get(`${apiUrl}/api/model/config`),
      axios.get(`${apiUrl}/api/model/providers`)
    ])
    
    modelConfig.value = configRes.data
    providers.value = providersRes.data.providers
    
    formData.value = {
      provider: configRes.data.provider,
      model_name: configRes.data.model_name,
      temperature: configRes.data.temperature,
      api_key: ''
    }
  } catch (error) {
    console.error('Failed to load config:', error)
  }
}

const saveConfig = async () => {
  saving.value = true
  message.value = null
  
  try {
    const payload = {
      provider: formData.value.provider,
      model_name: formData.value.model_name,
      temperature: formData.value.temperature
    }
    
    if (formData.value.api_key) {
      if (formData.value.provider === 'openai') {
        payload.openai_api_key = formData.value.api_key
      } else if (formData.value.provider === 'anthropic') {
        payload.anthropic_api_key = formData.value.api_key
      } else if (formData.value.provider === 'gemini') {
        payload.google_api_key = formData.value.api_key
      }
    }
    
    await axios.post(`${apiUrl}/api/model/config`, payload)
    
    message.value = {
      type: 'success',
      text: 'Configuration saved successfully! The changes will take effect immediately.'
    }
    
    await loadConfig()
  } catch (error) {
    message.value = {
      type: 'error',
      text: error.response?.data?.detail || 'Failed to save configuration'
    }
  } finally {
    saving.value = false
  }
}

const testConnection = async () => {
  testing.value = true
  message.value = null
  
  try {
    // First save the config
    await saveConfig()
    
    // Then test with a simple query
    const response = await axios.post(`${apiUrl}/api/chat`, {
      message: 'Test connection'
    })
    
    message.value = {
      type: 'success',
      text: '✓ Connection successful! The AI model is working correctly.'
    }
  } catch (error) {
    message.value = {
      type: 'error',
      text: error.response?.data?.detail || 'Connection test failed. Please check your API key.'
    }
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #009639;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #009639;
  cursor: pointer;
  border: none;
}
</style>
