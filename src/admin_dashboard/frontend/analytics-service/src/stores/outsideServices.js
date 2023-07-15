import { defineStore } from 'pinia'
import httpRequester from '../miscellaneous/requester.js'

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
        const result = await httpRequester.get('/testFront/')
        this.subscription = result.data.subs

      } 
      catch (error) {
        console.error(error)
      }
    },

  },

})