import { defineStore } from 'pinia'
import axios from 'axios'

export const useOwnServices = defineStore('ownServices', {
  state: () => ({ 
    ownServices: []
  }),



  getters: {
    subsFromGetter: (state) => state.subs,
  },



  actions: {
    async fetchOwnServices() {
      try {
        const result = await axios.get('http://127.0.0.1:8002/testFront/')
        this.subscription = result.data.subs

      } 
      catch (error) {
        console.error(error)
      }
      
    },

  },

})