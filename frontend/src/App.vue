<script setup lang="ts">
import SiteNav from './components/SiteNav.vue'
import AppFooter from './components/AppFooter.vue'
</script>

<template>
  <SiteNav />
  <main>
    <RouterView />
  </main>
  <AppFooter />
</template>
