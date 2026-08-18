import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/news', name: 'news', component: () => import('../views/NewsView.vue') },
    { path: '/history', name: 'history', component: () => import('../views/HistoryView.vue') },
    { path: '/groups', name: 'groups', component: () => import('../views/GroupsView.vue') },
    { path: '/recruit', name: 'recruit', component: () => import('../views/RecruitView.vue') },
    { path: '/cooperate', name: 'cooperate', component: () => import('../views/CooperateView.vue') },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth', top: 80 }
    }
    return { top: 0 }
  },
})

export default router
