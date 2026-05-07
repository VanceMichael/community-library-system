import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', icon: 'DataAnalysis' }
      },
      {
        path: 'books',
        name: 'Books',
        meta: { title: '图书管理', icon: 'Reading' },
        children: [
          {
            path: 'list',
            name: 'BookList',
            component: () => import('@/views/books/BookList.vue'),
            meta: { title: '图书列表' }
          },
          {
            path: 'categories',
            name: 'Categories',
            component: () => import('@/views/books/Categories.vue'),
            meta: { title: '分类管理' }
          }
        ]
      },
      {
        path: 'readers',
        name: 'Readers',
        meta: { title: '读者管理', icon: 'User' },
        children: [
          {
            path: 'list',
            name: 'ReaderList',
            component: () => import('@/views/readers/ReaderList.vue'),
            meta: { title: '读者列表' }
          }
        ]
      },
      {
        path: 'borrowings',
        name: 'Borrowings',
        meta: { title: '借阅管理', icon: 'Document' },
        children: [
          {
            path: 'list',
            name: 'BorrowingList',
            component: () => import('@/views/borrowings/BorrowingList.vue'),
            meta: { title: '借阅记录' }
          },
          {
            path: 'reservations',
            name: 'Reservations',
            component: () => import('@/views/borrowings/Reservations.vue'),
            meta: { title: '预约管理' }
          }
        ]
      },
      {
        path: 'fines',
        name: 'Fines',
        meta: { title: '逾期管理', icon: 'Warning' },
        children: [
          {
            path: 'list',
            name: 'FineList',
            component: () => import('@/views/fines/FineList.vue'),
            meta: { title: '罚款记录' }
          },
          {
            path: 'reminders',
            name: 'Reminders',
            component: () => import('@/views/fines/Reminders.vue'),
            meta: { title: '逾期提醒' }
          }
        ]
      },
      {
        path: 'purchases',
        name: 'Purchases',
        meta: { title: '采购管理', icon: 'ShoppingCart' },
        children: [
          {
            path: 'suggestions',
            name: 'Suggestions',
            component: () => import('@/views/purchases/Suggestions.vue'),
            meta: { title: '采购建议' }
          },
          {
            path: 'orders',
            name: 'PurchaseOrders',
            component: () => import('@/views/purchases/PurchaseOrders.vue'),
            meta: { title: '采购订单' }
          }
        ]
      },
      {
        path: 'statistics',
        name: 'Statistics',
        meta: { title: '借阅统计', icon: 'PieChart' },
        children: [
          {
            path: 'hot-books',
            name: 'HotBooks',
            component: () => import('@/views/statistics/HotBooks.vue'),
            meta: { title: '热门图书' }
          },
          {
            path: 'trend',
            name: 'BorrowTrend',
            component: () => import('@/views/statistics/BorrowTrend.vue'),
            meta: { title: '借阅趋势' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '社区图书馆管理系统'

  const token = localStorage.getItem('token')
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
