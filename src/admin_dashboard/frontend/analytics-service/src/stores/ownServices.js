import { defineStore } from 'pinia'
import httpRequester from '../miscellaneous/requester.js'

export const useOwnServices = defineStore('ownServices', {
  state: () => ({ 
    ownServices: []
  }),



  getters: {
    mappedOwnServices: (state) => {
      return state.ownServices.map((value) => {
        const tuple = Object.entries(value)[0]
        return {serviceName: tuple[0], serviceSuccsess: tuple[1]}
      })
    },
  },



  actions: {
    async fetchOwnServices() {
      try {
        const result = await httpRequester.get('/info_own_services/')
        this.ownServices = result.data.own_services

      } 
      catch (error) {
        console.error(error)
      }
      
    },

  },

})