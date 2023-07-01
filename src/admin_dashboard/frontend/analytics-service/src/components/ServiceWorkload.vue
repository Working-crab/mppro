<template>
  <div class="component-container service-workload">
    <div class="component-header">Успешность работы сервисов</div>

    <div class="service-table-header">
      <span class="service-name" style="text-align: center;">Имя сервиса</span>
      <span class="service-load">Успешнось</span>
    </div>

    <div class="service-list-content scroll-box">
      <div class="service-card" v-for="service in infoAboutServices" :key="service.id">
        <span class="service-table-name">{{ service.serviceName }}</span>
        <span :class="`service-table-load ${serviceWorkloadStainer(service.serviceSuccsess)}`">{{ service.serviceSuccsess }}%</span>
      </div>
    </div>    

  </div>
</template>

<script>
export default {
  name: 'ServiceWorkload',
  props: {
    infoAboutServices: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
    }
  },
  methods:{
    serviceWorkloadStainer(serviceWorkload){
      let value = serviceWorkload
      if(value > 90){
        return 'greate'
      }
      if (value > 80) {
        return 'normal'
      }
      if (value <= 80) {
        return 'bad'
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.service-workload{
  height: 358px;
  width: 710px;
  margin: 10px;
  box-shadow: 2px 2px 5px black;
  /* border-radius: 3px; */
  font-size: 21px;
  background-color: white;
}
.component-header{
  text-align: start;
  font-weight: 600;
  margin-bottom: 20px;
  padding: 10px;
  background-color: rgba(0,133,242,.1);
}
.service-table-header{
  text-align: start;
  display: flex;
  border-bottom: 2px solid #e6e6e6;
  font-weight: 600;
}
.service-card{
  text-align: start;
  display: flex;
  align-items: center;
  padding: 5px;
  margin: 0 10px;
  padding: 10px 0;
}
.service-card + .service-card{
  /* border-top: 1px solid black; */
}
.service-list-content{
  height: calc(100% - 92px);
}

.service-name{
  width: 300px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-left: 20px;
  
}
.service-load{
  width: 400px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-left: 20px;
}

.service-table-name{
  width: 300px;
  
}
.service-table-load{
  width: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.greate{
  
  color: #42b983;
}
.normal{
  color: rgb(165, 221, 34);
}
.bad{
  color: orange;
}
.bac-color-grey{
  background-color: rgb(211, 211, 211);
}
</style>
