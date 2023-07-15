import { defineStore } from 'pinia'
import httpRequester from '../miscellaneous/requester.js'

export const useUser = defineStore('user', {
  state: () => ({ 
    user: []
  }),

  getters: {
  },

  actions: {
    async fetchUser(userId) {
      try {
        const result = await httpRequester.get(`/user/${userId}`)
        this.user = result.data.user
      } 
      catch (error) {
        console.error(error)
      }
      
    },

  },

})