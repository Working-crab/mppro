<template>
  <div class="page-container">
    <h1>Дашборд для админов по аналитеке сервисов</h1>
    <h4>Сегодня: {{ getDate() }} | Время обновления дешборда: {{ DateDashboard }}</h4>
    <!-- <div class="sub-container">
      <h4 v-for="sub in subs" :key="sub.id">{{sub.title}}({{sub.description}}) price: {{ sub.price }}</h4>
    </div> -->
    <div class="flex">
      <service-workload :infoAboutServices="infoAboutServices"></service-workload>
      <ErrorsList :errors="errors"></ErrorsList>
      <ActionList :actions="lastActionsStore.lastActions"></ActionList>
      <ServicesStatus :errors="serviceStaus"></ServicesStatus>
    </div>
    

    
  </div>
</template>

<script>
import ServiceWorkload from './components/ServiceWorkload.vue'
import ErrorsList from './components/ErrorsList.vue'
import ActionList from './components/ActionList.vue'
import ServicesStatus from './components/ServicesStatus.vue'
import { useLastActions } from '@/stores/lastActions'


export default {
  setup(){
    const lastActionsStore = useLastActions()

    return {lastActionsStore}
  },
  name: 'App',
  components: {
    ServiceWorkload,
    ErrorsList,
    ActionList,
    ServicesStatus
  },
  data() {
    return {
      DateDashboard: '',
      errors: [
        {
          id: 1,
          action: 'Получение рекламных ставок',
          date: '10.04.2023',
          user: 'Вася Пупкин'
        },
        {
          id: 2,
          action: 'Получение рекламных кампаний',
          date: '10.04.2023',
          user: 'Полный Алексей'
        },
        {
          id: 3,
          action: 'Установка токенов',
          date: '10.04.2023',
          user: 'Вася Пупкин Пупкин Пупкин'
        },
        // {
        //   id: 4,
        //   action: 'Установка токенов',
        //   date: '10.04.2023',
        //   user: 'Вася Пупкин'
        // },
      ],
      infoAboutServices:[
        {
          id: 1,
          serviceName: 'Service 1',
          workload: '100%'
        },
        {
          id: 2,
          serviceName: 'Service 2 ti petux no ti lox obelsa blox',
          workload: '95%'
        },
        {
          id: 3,
          serviceName: 'Service 3',
          workload: '84%'
        },
        {
          id: 4,
          serviceName: 'Service 4',
          workload: '76%'
        },
        {
          id: 5,
          serviceName: 'Service 5',
          workload: '76%'
        },
      ],
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
      ]
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
    }
  },
  async mounted(){
    await this.lastActionsStore.fetchLastActions()
    this.getDateDashboard()
  },
  computed:{
    subs(){
      return this.OwnServicesStore.subscription
    },
  }
}
</script>

<style>
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
</style>
