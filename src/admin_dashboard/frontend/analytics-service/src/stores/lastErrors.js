import { defineStore } from 'pinia'
import httpRequester from '../miscellaneous/requester.js'

export const useLastErrors = defineStore('lastErrors', {
  state: () => ({ 
    lastErrors: []
  }),



  getters: {
    lastErrorsMapped: (state) => state.lastErrors.map((value) => {
      const arr = value.description.split('Description:')//Attention: mutaiting value
      if (arr.length > 1) {
        value.detail = arr[0]
        value.description = arr[1]
        return value
      }
      else {
        value.detail = arr[0]
        return value
      }
    }),
  },

  

  actions: {
    async fetchLastErrors() {
      try {
        const result = await httpRequester.get('/last_errors/')
        this.lastErrors = result.data.last_errors

      } 
      catch (error) {
        console.error(error)
      }
      
    },

    async fetchtErrorTaceback() {
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