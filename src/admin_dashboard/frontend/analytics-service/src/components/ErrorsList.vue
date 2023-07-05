<template>
  <div class="component-container errors-list">
    <div class="component-header">Последние ошибки</div>

    <div class="table-header">
      <span class="action-text">Действие</span>
      <span class="date-text">Дата</span>
      <span class="user-text">ID Пользователя</span>
    </div>

    <div class="errors-list-content scroll-box">
      <div 
        :class="`errors-card ${index % 2 === 0 ? 'bac-color-grey' : ''}`" 
        @click="openDialog(error)"
        @mouseenter="mackeGray($event)"
        @mouseleave="deleteGray($event)"
        v-for="error, index in errors" :key="error.id"
      >
        <span class="action-text-table">{{ error.action }}</span>
        <div class="date-container">
          <time class="date">{{ mainDate(error.date_time) }}</time>
          <time class="hours">{{ hoursDate(error.date_time) }}</time>
        </div>
        <span class="user-text-table">{{ error.user_id }}</span>
      </div>
    </div>

    <v-dialog v-model="dialog" width="auto">
      <v-card>
        <v-card-title>
          Детали ошибки
        </v-card-title>
        <v-card-text>
          <h4>User ID: {{errorDetail.user_id}}</h4>
          <h4>User telegram name: {{ userStore.user.telegram_username }}</h4>
          <h4>Action: {{errorDetail.action}}</h4>
          <p class="mt-2"> <span class="font-weight-bold">Detail:</span> {{ errorDetail.description }}</p>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" block @click="dialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </div>
</template>

<script>
import moment from 'moment';
moment.locale('Ru')

import { useUser } from '@/stores/user'

export default {
  setup(){
    const userStore = useUser()

    return {userStore}
  },
  props:{
    errors: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      dialog: false,
      errorDetail: {}
    }
  },
  methods: {
    mainDate(date){
      let day = moment(date).format('DD.MM.YY')
      return day
    },
    hoursDate(date){
      let day = moment(date).format('h:mm:ss')
      return day
    },
    mackeGray(e){
      e.target.classList.add('gray')
    },
    deleteGray(e){
      e.target.classList.remove('gray')
    },
    async openDialog(errorDetail){
      this.errorDetail = errorDetail
      this.dialog = true
      await this.userStore.fetchUser(errorDetail.user_id)
    }
  },
}
</script>

<style scoped>
.errors-list{
  height: 360px;
  width: 700px;
  margin: 10px;
  box-shadow: 2px 2px 5px black;
  /* border-radius: 5px; */
  font-size: 20px;
  background-color: white;
}
.component-header{
  text-align: start;
  font-weight: 600;
  margin-bottom: 20px;
  border-bottom: 2px solid #e6e6e6;
  padding: 10px;
  /* background-color: #8cb4ff; */
  background-color: rgba(0,133,242,.1);
}
.errors-list-content{
  height: calc(100% - 101px);
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
}
.errors-card{
  display: flex;
  margin: 10px 0;
  cursor: pointer;
  transition: .5s
}
.errors-card + .errors-card{
  /* border-top: 1px solid black; */
  /* margin: 10px 0; */
}

.table-header{
  display: flex;
  text-align: center;
  justify-content: center;
  font-weight: 600;
}
.action-text{
  width: 233px;
  display: flex;
  justify-content: center;
  align-items: center;
  /* padding-left: 20px; */
}
.date-text{
  width: 233px;
  display: flex;
  justify-content: center;
  align-items: center;
  /* padding-left: 20px; */
}
.user-text{
  width: 233px;
  display: flex;
  justify-content: center;
  align-items: center;
  /* padding-left: 20px; */
}

.action-text-table{
  width: 233px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.date-container{
  width: 233px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.user-text-table{
  width: 233px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.date-container{
  width: 233px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.date{

}
.hours{
  font-size: 15px;
}

.bac-color-grey{
  background-color: rgb(230 230 230);
}
.gray{
  background-color: gray;
}
</style>