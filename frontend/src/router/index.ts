import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NewsView from '../views/NewsView.vue'
import HistoryView from '../views/HistoryView.vue'
import GroupsView from '../views/GroupsView.vue'
import RecruitView from '../views/RecruitView.vue'
import CooperateView from '../views/CooperateView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/news', name: 'news', component: NewsView },
    { path: '/history', name: 'history', component: HistoryView },
    { path: '/groups', name: 'groups', component: GroupsView },
    { path: '/recruit', name: 'recruit', component: RecruitView },
    { path: '/cooperate', name: 'cooperate', component: CooperateView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth', top: 76 }
    }
    return { top: 0 }
  },
})

export default router
