import { defineStore } from 'pinia'
import axios from 'axios'

export const useOutsideServices = defineStore('outsideServices', {
  state: () => ({ 
    outsideServices: []
  }),



  getters: {
    subsFromGetter: (state) => state.subs,
  },



  actions: {
    async fetchOutsideServices() {
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