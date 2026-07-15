<template>
  <router-view></router-view>
</template>

<script>
export default {
  name: "App"
}
</script>

<style>
body {
  margin: 0;
  background: #f5f7fb;
}

#app {
  min-height: 100vh;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #243447;
}

.card {
  border: 0;
  box-shadow: 0 0.25rem 0.8rem rgba(33, 37, 41, 0.08);
}
</style>
