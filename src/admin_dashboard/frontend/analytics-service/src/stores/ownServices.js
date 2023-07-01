import { defineStore } from 'pinia'
import axios from 'axios'

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
        const result = await axios.get('http://127.0.0.1:8002/info_own_services/')
        this.ownServices = result.data.own_services

      } 
      catch (error) {
        console.error(error)
      }
      
    },

  },

})