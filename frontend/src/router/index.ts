import { createRouter, createWebHistory } from 'vue-router'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/sector-c' },
    {
      path: '/sector-a',
      name: 'sector-a',
      component: () => import('@/views/SectorSophon.vue'),
      meta: { title: '智子终端', sector: 'alpha' },
    },
    {
      path: '/sector-b',
      name: 'sector-b',
      component: () => import('@/views/ChronicleView.vue'),
      meta: { title: '文明编年史', sector: 'beta' },
    },
    // 保留其它扇区入口，后续可接真实组件
    {
      path: '/sector-c',
      name: 'sector-c',
      component: () => import('@/views/UniverseView.vue'),
      meta: { title: '宇宙广播站', sector: 'gamma' },
    },
    {
      path: '/sector-d',
      name: 'sector-d',
      component: () => import('@/views/GalleryView.vue'),
      meta: { title: '二向箔画廊', sector: 'delta' },
    },
    {
      path: '/sector-p',
      name: 'sector-p',
      component: () => import('@/views/SectorFigures.vue'),
      meta: { title: '人物志', sector: 'pi' },
    },
    {
      path: '/sector-e',
      name: 'sector-e',
      component: () => import('@/views/SectorDarkForest.vue'),
      meta: { title: '黑暗森林广场', sector: 'epsilon' },
    },
    {
      path: '/sector-t',
      name: 'sector-t',
      component: () => import('@/views/SectorPendulum.vue'),
      meta: { title: '三体摆', sector: 'theta' },
    },
    {
      path: '/sector-u',
      name: 'sector-u',
      component: () => import('@/views/SectorMiniUniverse.vue'),
      meta: { title: '647号小宇宙', sector: 'upsilon' },
    },
    {
      path: '/sector-f',
      name: 'sector-f',
      component: () => import('@/views/SectorWallfacer.vue'),
      meta: { title: '面壁计划', sector: 'zeta' },
    },
    {
      path: '/sector-zero-v2',
      redirect: '/sector-c',
    },
    {
      path: '/sector-s',
      name: 'sector-s',
      component: () => import('@/views/SectorStaircase.vue'),
      meta: { title: '阶梯计划', sector: 'sigma' },
    },
    {
      path: '/sector-g',
      name: 'sector-g',
      component: () => import('@/views/SectorFourthDimension.vue'),
      meta: { title: '四维碎片', sector: 'gamma' },
    },
    {
      path: '/sector-r',
      name: 'sector-r',
      component: () => import('@/views/SectorRedCoast.vue'),
      meta: { title: '红岸控制台', sector: 'rho' },
    },
    {
      path: '/sector-l',
      name: 'sector-l',
      component: () => import('@/views/SectorCurvature.vue'),
      meta: { title: '曲率驱动', sector: 'lambda' },
    },
    {
      path: '/sector-j',
      name: 'sector-j',
      component: () => import('@/views/SectorBunker.vue'),
      meta: { title: '掩体世界', sector: 'iota' },
    },
    {
      path: '/sector-w',
      name: 'sector-w',
      component: () => import('@/views/SectorDroplet.vue'),
      meta: { title: '水滴', sector: 'omega' },
    },
    {
      path: '/sector-x',
      name: 'sector-x',
      component: () => import('@/views/SectorX.vue'),
      meta: { title: '未知区域', sector: 'x' },
    },
    {
      path: '/sector-pdc',
      name: 'sector-pdc',
      component: () => import('@/views/SectorPDC.vue'),
      meta: { title: '行星防御理事会', sector: 'pdc' },
    },
    {
      path: '/sector-ravine',
      name: 'sector-ravine',
      component: () => import('@/views/SectorRavine.vue'),
      meta: { title: '大低谷', sector: 'ravine' },
    },
    {
      path: '/sector-blind',
      name: 'sector-blind',
      component: () => import('@/views/SectorBlind.vue'),
      meta: { title: '盲区', sector: 'blind' },
    },
    {
      path: '/sector-tomb',
      name: 'sector-tomb',
      component: () => import('@/views/SectorTomb.vue'),
      meta: { title: '文明墓碑', sector: 'tomb' },
    },
    {
      path: '/sector-human',
      name: 'sector-galaxy-human',
      component: () => import('@/views/SectorGalaxyHuman.vue'),
      meta: { title: '银河人类', sector: 'galaxy-human' },
    },
    {
      path: '/sector-m',
      name: 'sector-membrane',
      component: () => import('@/views/SectorMembrane.vue'),
      meta: { title: '宇宙膜', sector: 'membrane' },
    },
    {
      path: '/sector-boundary',
      name: 'sector-boundary',
      component: () => import('@/views/SectorScientificBoundary.vue'),
      meta: { title: '科学边界', sector: 'boundary' },
    },
    {
      path: '/sector-v',
      name: 'sector-v',
      component: () => import('@/views/SectorComputer.vue'),
      meta: { title: '人列计算机', sector: 'von-neumann' },
    },
    {
      path: '/sector-library',
      name: 'sector-library',
      component: () => import('@/views/SectorChronicle.vue'),
      meta: { title: '原著阅读', sector: 'library' },
    },
    {
      path: '/sector-guestbook',
      name: 'sector-guestbook',
      component: () => import('@/views/CosmicGuestbook.vue'),
      meta: { title: '宇宙留言簿', sector: 'guestbook' },
    },
    { path: '/figures', redirect: '/sector-p' },
    { path: '/sophon', redirect: '/sector-a' },
    { path: '/chronicle', redirect: '/sector-b' },
    { path: '/reader', redirect: '/sector-library' },
    { path: '/library', redirect: '/sector-library' },
    { path: '/gallery', redirect: '/sector-d' },
    { path: '/home', redirect: '/sector-c' },
  ],
})

router.beforeEach((_to, _from, next) => {
  next()
})

router.afterEach((to) => {
  const title = (to.meta?.title as string) || '3body'
  document.title = `${title} — 3Body X`
})

export default router
