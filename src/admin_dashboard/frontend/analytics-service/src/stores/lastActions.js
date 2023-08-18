import { defineStore } from 'pinia'
import httpRequester from '../miscellaneous/requester.js'

export const useLastActions = defineStore('lastActions', {
  state: () => ({ 
    lastActions: [],
    lastActionsForChart: []
  }),

  getters: {
    subsFromGetter: (state) => state.subs,
    lastActionsForChartMapped: (state) => {
      const errorsEntries = Object.entries(state.lastActionsForChart)
      
      const lables = errorsEntries.map((value) => {
        return value[0]
      })
      const errorsData = errorsEntries.map((value) => {
        return value[1].error_count
      })
      const successData = errorsEntries.map((value) => {
        return value[1].success_count
      })

      return {
        errors: {
          data: errorsData
        },
        success:{
          
          data: successData
        },
        labels: lables, 
      }
    }
  },
  
  actions: {
    async fetchLastActions() {
      try {
        const result = await httpRequester.get('/last_actons/')
        this.lastActions = result.data.last_actions
      } 
      catch (error) {
        console.error(error)
      }
      
    },

    async fetchTimeIntervalErrors() {
      try {
        const result = await httpRequester.get('/last_week_errors/')
        this.lastActionsForChart = result.data.errors
      } 
      catch (error) {
        console.error(error)
      }
    },
  },

})