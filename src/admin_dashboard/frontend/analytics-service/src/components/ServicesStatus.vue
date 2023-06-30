<template>
  <div class="component-container errors-list">
    <div class="component-header">Успешность работы сторонних сервисов</div>

    <div class="table-header">
      <span class="action-text">Имя сервиса</span>
      <span class="date-text">Успешность</span>
    </div>

    <div class="errors-list-content scroll-box">
      <div :class="`errors-card ${index % 2 === 0 ? 'bac-color-grey' : ''}`" v-for="error, index in errors" :key="error.id">
        <span class="action-text-table">{{ error.serviceName }}</span>
        <span class="date-text-table">{{ error.workload }}</span>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  props:{
    errors: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
    }
  },
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
  border-bottom: 2px solid #e6e6e6;
  padding: 10px;
  /* background-color: #8cb4ff; */
  background-color: rgba(0,133,242,.1);
}
.errors-list-content{
  height: calc(100% - 114px);
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 24px;
}
.errors-card{
  display: flex;
  padding: 10px 0;
  cursor: pointer;
}
.errors-card + .errors-card{
  /* border-top: 1px solid black; */
  margin: 10px 0;
}

.table-header{
  display: flex;
  text-align: center;
  justify-content: center;
  font-weight: 600;
}
.action-text{
  width: 346px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-left: 20px;
}
.date-text{
  width: 346px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-left: 20px;
}


.action-text-table{
  width: 346px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.date-text-table{
  width: 346px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.bac-color-grey{
  background-color: rgb(230 230 230);
}
</style>