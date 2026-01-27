import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import Home from './views/Home.vue'
import Settings from './views/Settings.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/chat/:id?', component: Home },
  { path: '/settings', component: Settings }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
