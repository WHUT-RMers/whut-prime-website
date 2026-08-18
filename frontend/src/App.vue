<script setup lang="ts">
import SiteNav from './components/SiteNav.vue'
import HeroSection from './components/HeroSection.vue'
import MarqueeBand from './components/MarqueeBand.vue'
import EventSection from './components/EventSection.vue'
import NewsSection from './components/NewsSection.vue'
import HistorySection from './components/HistorySection.vue'
import GroupsSection from './components/GroupsSection.vue'
import RecruitSection from './components/RecruitSection.vue'
import CooperateSection from './components/CooperateSection.vue'
import AppFooter from './components/AppFooter.vue'
</script>

<template>
  <SiteNav />
  <main>
    <HeroSection />
    <MarqueeBand />
    <EventSection />
    <NewsSection />
    <HistorySection />
    <GroupsSection />
    <RecruitSection />
    <CooperateSection />
  </main>
  <AppFooter />
</template>
