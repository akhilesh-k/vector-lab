<script setup>
import { RouterView } from "vue-router";
import VectorLabHeader from "./components/VectorLabHeader.vue";
import SideBarHeader from "./components/SideBarHeader.vue";
</script>

<template>
  <main>
    <SideBarHeader />
    <VectorLabHeader />
    <router-view style="width: 100vw; box-sizing: border-box" />
  </main>
</template>

<style scoped>
* {
  outline: none;
  font-family: Source Sans Pro, sans-serif;
}
*:focus {
  outline: none;
}
</style>
