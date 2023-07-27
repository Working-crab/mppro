<template>
  <Line
    v-if="load"
    id="my-chart-id"
    :options="chartOptions"
    :data="chartData"
    style="background: white; margin: 10px;"
  />
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement } from 'chart.js'

ChartJS.register(CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend)

export default {
  name: 'BarChart',
  components: { Line },
  data() {
    return {
      chartData: {
        labels: ['21.03.2023'],
        datasets: [ 
          { data: [], backgroundColor: '#f87979', label: 'Data One', },
        ],
      },
      chartOptions: {
        responsive: true
      },
      load: false
    }
  },
  props:{
    errors:{
      type: Object,
      default: () => {}
    }
  },
  watch:{
    errors(){
      this.chartData.labels = this.errors.lables
      this.chartData.datasets[0].data = this.errors.data
      this.load = true
    }
  }
}
</script>