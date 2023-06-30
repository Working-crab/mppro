import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import momentp from '@/plugins/momentp'

import '@/assets/css/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(momentp)
app.mount('#app')
