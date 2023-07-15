import { defineStore } from 'pinia'
import axios from 'axios'

export const useLastActions = defineStore('lastActions', {
  state: () => ({ 
    lastActions: []
  }),

  getters: {
    subsFromGetter: (state) => state.subs,
  },
  
  actions: {
    async fetchLastActions() {
      try {
        const result = await axios.get('http://127.0.0.1:8002/last_actons/')
        this.lastActions = result.data.last_actions
      } 
      catch (error) {
        console.error(error)
      }
      
    },

  },

})