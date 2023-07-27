<template>
  <div class="page-container">
    <div class="header-container">
      <h1>Дашборд для админов для аналитики сервисов</h1>
      <h4>Сегодня: {{ getDate() }} | Время обновления дешборда: {{ DateDashboard }}</h4>
    </div>
   
    <!-- <div class="sub-container">
      <h4 v-for="sub in subs" :key="sub.id">{{sub.title}}({{sub.description}}) price: {{ sub.price }}</h4>
    </div> -->
    <div class="flex-keks">
      <service-workload :infoAboutServices="ownServicesStore?.mappedOwnServices"></service-workload>
      <ErrorsList :errors="lastErrorssStore?.lastErrorsMapped"></ErrorsList>
      <ActionList :actions="lastActionsStore?.lastActions"></ActionList>
      <ServicesStatus :errors="serviceStaus"></ServicesStatus>

      <Vchart :errors="lastErrorssStore?.weekErrorsMapped"></Vchart>
    </div>
  </div>
</template>

<script>
import ServiceWorkload from './components/ServiceWorkload.vue'
import ErrorsList from './components/ErrorsList.vue'
import ActionList from './components/ActionList.vue'
import ServicesStatus from './components/ServicesStatus.vue'
import Vchart from '@/components/VChart.vue'
import { useLastActions } from '@/stores/lastActions'
import { useLastErrors } from '@/stores/lastErrors'
import { useOwnServices } from '@/stores/ownServices'




export default {
  setup(){
    const lastActionsStore = useLastActions()
    const lastErrorssStore = useLastErrors()
    const ownServicesStore  = useOwnServices()

    return {lastActionsStore, lastErrorssStore, ownServicesStore}
  },
  name: 'App',
  components: {
    ServiceWorkload,
    ErrorsList,
    ActionList,
    ServicesStatus,
    Vchart
  },
  data() {
    return {
      DateDashboard: '',
      serviceStaus: [
        {
          id: 1,
          serviceName: 'Service 1',
          workload: '76%'
        },
        {
          id: 2,
          serviceName: 'Service 2',
          workload: '76%'
        },
      ],
      lables1:[],
      data1:[]
    }
  },
  methods:{
    getDate(){
      let date = new Date(Date.now())
      var options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        timezone: 'UTC',

      };
      return date.toLocaleString("ru", options)
    },
    getDateDashboard(){
      let date = new Date(Date.now())
      var options = {
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
        timezone: 'UTC',

      };
      this.DateDashboard = date.toLocaleString("ru", options)
    },
    parsErrors(){
      const errorsEntries = Object.entries(this.lastErrorssStore.weekErrors)
      const lables = errorsEntries.map((value) => {
        return value[0]
      })
      this.lables = lables
      const data = errorsEntries.map((value) => {
        return value[1]
      })
      this.data = data
    }
  },
  async mounted(){
    await this.lastActionsStore.fetchLastActions()
    await this.lastErrorssStore.fetchLastErrors()
    await this.ownServicesStore.fetchOwnServices()
    await this.lastErrorssStore.fetchLastWeekErrors()
    this.getDateDashboard()
  },
  computed:{
    subs(){
      return this.ownServicesStore.subscription
    },
  }
}
</script>

<style scoped>
#app {
  font-family: 'Montserrat', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
}

.sub-container{
  box-shadow: 2px 2px 5px black;
  border-radius: 5px;
  padding: 10px;
}
.page-container h1 {
  /* margin: 10px 0; */
}

.header-container{
  margin: 10px 0;
}
</style>
