<template>
  <div class="component-container errors-list">
    <div class="component-header">Последние действия</div>

    <div class="table-header">
      <span class="action-text">Действие</span>
      <span class="date-text">Дата</span>
      <span class="user-text">Юзер</span>
    </div>

    <div class="errors-list-content scroll-box">
      <div :class="`errors-card ${index % 2 === 0 ? 'bac-color-grey' : ''}`" v-for="action, index in actions" :key="action.id">
        <span class="action-text-table">{{ action.action }}</span>
        <span class="date-text-table">{{ customFormatData(action.date_time)  }}</span>
        <span class="user-text-table">{{ action.user_id }}</span>
        <!-- {{ action }} -->
      </div>
    </div>

  </div>
</template>

<script>
import moment from 'moment';

export default {
  props:{
    actions: {
      type: Array,
      default: () => []
    }
  },
  methods:{
    customFormatData(date){
      moment.locale('Ru')
      var day = moment(date).format('MMMM YYYY, h:mm:ss a')
      return day
    }
  }
}
</script>

<style scoped>
.errors-list{
  height: 358px;
  width: 710px;
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
  padding: 10px;
  /* background-color: #8cb4ff; */
  background-color: rgba(0,133,242,.1);
}
.errors-list-content{
  height: calc(100% - 57px);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.errors-card{
  display: flex;
  padding: 10px 0;
}
.errors-card + .errors-card{
  /* border-top: 1px solid black; */
  
}

.table-header{
  display: flex;
  text-align: center;
  justify-content: center;
  margin-bottom: 10px;
  font-weight: 600;
}
.action-text{
  width: 310px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-left: 20px;
}
.date-text{
  width: 250px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-left: 20px;
}
.user-text{
  width: 133px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-left: 20px;
}

.action-text-table{
  width: 310px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.date-text-table{
  width: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.user-text-table{
  width: 183px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.bac-color-grey{
  background-color: rgb(230 230 230);
}
</style>