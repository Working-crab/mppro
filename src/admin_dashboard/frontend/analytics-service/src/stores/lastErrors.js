import { defineStore } from 'pinia'
import httpRequester from '../miscellaneous/requester.js'

export const useLastErrors = defineStore('lastErrors', {
  state: () => ({ 
    lastErrors: [],
    weekErrors: []
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
    
    weekErrorsMapped: (state) => {
      const errorsEntries = Object.entries(state.weekErrors)
      
      const lables = errorsEntries.map((value) => {
        return value[0]
      })
      const data = errorsEntries.map((value) => {
        return value[1]
      })

      return {lables: lables, data: data}
    }


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

    async fetchLastWeekErrors() {
      try {
        const result = await httpRequester.get('/last_week_errors/')
        this.weekErrors = result.data.errors

      } 
      catch (error) {
        console.error(error)
      }
      
    },

  },

})