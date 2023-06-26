import { defineStore } from 'pinia'
import axios from 'axios'

export const useLastErrors = defineStore('lastErrors', {
  state: () => ({ 
    lastErrors: []
  }),



  getters: {
    lastErrorsFromGetter: (state) => state.subs,
  },

  

  actions: {
    async fetchLastErrors() {
      try {
        const result = await axios.get('http://127.0.0.1:8002/testFront/')
        this.subscription = result.data.subs

      } 
      catch (error) {
        console.error(error)
      }
      
    },

    async fetchtErrorTaceback() {
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