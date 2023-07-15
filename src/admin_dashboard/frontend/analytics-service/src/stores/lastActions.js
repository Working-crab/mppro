import { defineStore } from 'pinia'
import httpRequester from '../miscellaneous/requester.js'

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
        const result = await httpRequester.get('/last_actons/')
        this.lastActions = result.data.last_actions
      } 
      catch (error) {
        console.error(error)
      }
      
    },

  },

})