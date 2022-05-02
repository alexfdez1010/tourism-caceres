<template>
  <div id="app">
    <h1>Turismo en Cáceres</h1>
    <TourismCaceres/>
  </div>
</template>

<script>

import TourismCaceres from "./components/TourismCaceres"

export default {
  name: 'App',
  components: {
    TourismCaceres
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
