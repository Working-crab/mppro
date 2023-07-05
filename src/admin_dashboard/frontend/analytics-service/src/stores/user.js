import { defineStore } from 'pinia'
import axios from 'axios'

export const useUser = defineStore('user', {
  state: () => ({ 
    user: []
  }),

  getters: {
  },

  actions: {
    async fetchUser(userId) {
      try {
        const result = await axios.get(`http://127.0.0.1:8002/user/${userId}`)
        this.user = result.data.user
      } 
      catch (error) {
        console.error(error)
      }
      
    },

  },

})