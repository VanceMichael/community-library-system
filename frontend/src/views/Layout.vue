<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo">
        <el-icon v-if="!isCollapse" class="logo-icon"><Reading /></el-icon>
        <span v-if="!isCollapse" class="logo-text">图书馆系统</span>
        <el-icon v-else class="logo-icon"><Reading /></el-icon>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>

        <el-sub-menu index="/books">
          <template #title>
            <el-icon><Reading /></el-icon>
            <span>图书管理</span>
          </template>
          <el-menu-item index="/books/list">图书列表</el-menu-item>
          <el-menu-item index="/books/categories">分类管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/readers">
          <template #title>
            <el-icon><User /></el-icon>
            <span>读者管理</span>
          </template>
          <el-menu-item index="/readers/list">读者列表</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/borrowings">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>借阅管理</span>
          </template>
          <el-menu-item index="/borrowings/list">借阅记录</el-menu-item>
          <el-menu-item index="/borrowings/reservations">预约管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/fines">
          <template #title>
            <el-icon><Warning /></el-icon>
            <span>逾期管理</span>
          </template>
          <el-menu-item index="/fines/list">罚款记录</el-menu-item>
          <el-menu-item index="/fines/reminders">逾期提醒</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/purchases">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>采购管理</span>
          </template>
          <el-menu-item index="/purchases/suggestions">采购建议</el-menu-item>
          <el-menu-item index="/purchases/orders">采购订单</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/statistics">
          <template #title>
            <el-icon><PieChart /></el-icon>
            <span>借阅统计</span>
          </template>
          <el-menu-item index="/statistics/hot-books">热门图书</el-menu-item>
          <el-menu-item index="/statistics/trend">借阅趋势</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon class="user-icon"><UserFilled /></el-icon>
              <span>{{ displayName }}</span>
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
          <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>

  <el-dialog
    v-model="profileDialogVisible"
    title="个人信息"
    width="500px"
    :close-on-click-modal="false"
  >
    <el-form :model="currentUser" label-width="100px">
      <el-form-item label="用户名">
        <el-input v-model="currentUser.username" disabled />
      </el-form-item>
      <el-form-item label="姓名" v-if="currentUser.is_reader">
        <el-input v-model="currentUser.name" disabled />
      </el-form-item>
      <el-form-item label="读者证号" v-if="currentUser.is_reader">
        <el-input v-model="currentUser.reader_id" disabled />
      </el-form-item>
      <el-form-item label="联系电话" v-if="currentUser.is_reader">
        <el-input v-model="currentUser.phone" disabled />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="currentUser.email" disabled />
      </el-form-item>
      <el-form-item label="角色">
        <el-tag :type="currentUser.is_staff || currentUser.is_superuser ? 'primary' : 'info'">
          {{ currentUser.is_staff || currentUser.is_superuser ? '管理员' : '读者' }}
        </el-tag>
      </el-form-item>
    </el-form>
  </el-dialog>

  <el-dialog
    v-model="passwordDialogVisible"
    title="修改密码"
    width="500px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="passwordFormRef"
      :model="passwordForm"
      :rules="passwordRules"
      label-width="100px"
    >
      <el-form-item label="旧密码" prop="old_password">
        <el-input
          v-model="passwordForm.old_password"
          type="password"
          placeholder="请输入旧密码"
          show-password
        />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input
          v-model="passwordForm.new_password"
          type="password"
          placeholder="请输入新密码"
          show-password
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirm_password">
        <el-input
          v-model="passwordForm.confirm_password"
          type="password"
          placeholder="请再次输入新密码"
          show-password
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="passwordDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { readerApi } from '@/api'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)

const currentUser = ref({
  username: '',
  email: '',
  is_staff: false,
  is_superuser: false,
  is_reader: false,
  name: '',
  reader_id: '',
  reader_pk: null,
  phone: '',
  id: null
})

const displayName = computed(() => {
  if (currentUser.value.is_reader && currentUser.value.name) {
    return currentUser.value.name
  }
  if (currentUser.value.is_staff || currentUser.value.is_superuser) {
    return '管理员'
  }
  return currentUser.value.username || '用户'
})

const profileDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const passwordFormRef = ref(null)
const passwordLoading = ref(false)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 3, message: '密码长度不能少于3位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title
  }))
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const fetchCurrentUser = async () => {
  try {
    const res = await readerApi.getCurrentUser()
    Object.assign(currentUser.value, res)
  } catch (error) {
    console.error('Failed to fetch current user:', error)
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('refresh')
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'profile') {
    profileDialogVisible.value = true
  } else if (command === 'changePassword') {
    Object.assign(passwordForm, {
      old_password: '',
      new_password: '',
      confirm_password: ''
    })
    passwordDialogVisible.value = true
  }
}

const handleChangePassword = async () => {
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  if (!currentUser.value.is_reader) {
    ElMessage.error('管理员账号暂不支持修改密码')
    return
  }

  if (!currentUser.value.reader_pk) {
    ElMessage.error('无法获取读者信息，请重新登录')
    return
  }

  passwordLoading.value = true
  try {
    await readerApi.changePassword(currentUser.value.reader_pk, {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (error) {
    console.error('Failed to change password:', error)
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  fetchCurrentUser()
})
</script>

<style scoped>
.layout-container {
  height: 100%;
}

.layout-aside {
  background-color: #304156;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #2b3a4a;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.logo-icon {
  font-size: 28px;
  margin-right: 10px;
}

.logo-text {
  font-size: 16px;
  white-space: nowrap;
}

.layout-header {
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-icon {
  font-size: 20px;
  cursor: pointer;
  margin-right: 20px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.user-icon {
  font-size: 18px;
  margin-right: 8px;
}

.arrow-icon {
  font-size: 12px;
  margin-left: 4px;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
