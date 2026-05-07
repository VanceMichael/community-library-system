<template>
  <div class="reader-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>读者列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增读者
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="姓名/读者证号">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入姓名或读者证号"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="正常" value="active" />
            <el-option label="挂失" value="suspended" />
            <el-option label="注销" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="reader_id" label="读者证号" width="140" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="80" align="center">
          <template #default="scope">
            {{ scope.row.gender === 'male' ? '男' : scope.row.gender === 'female' ? '女' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="borrow_limit" label="借阅限额" width="100" align="center" />
        <el-table-column prop="borrow_count" label="当前借阅" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.borrow_count > 0 ? 'primary' : 'info'">
              {{ scope.row.borrow_count }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="register_date" label="注册日期" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.register_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right" align="center">
          <template #default="scope">
            <div class="table-actions">
              <el-button type="primary" link @click="handleEdit(scope.row)">
                编辑
              </el-button>
              <el-button
                v-if="scope.row.status === 'active'"
                type="warning"
                link
                @click="handleSuspend(scope.row)"
              >
                挂失
              </el-button>
              <el-button
                v-if="scope.row.status === 'suspended'"
                type="success"
                link
                @click="handleActivate(scope.row)"
              >
                激活
              </el-button>
              <el-button
                v-if="scope.row.status !== 'closed'"
                type="danger"
                link
                @click="handleClose(scope.row)"
              >
                注销
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名（登录用）" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="formData.password" type="password" placeholder="请输入密码（留空则自动生成）" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="formData.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="formData.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="联系地址">
          <el-input v-model="formData.address" type="textarea" :rows="2" placeholder="请输入联系地址" />
        </el-form-item>
        <el-form-item label="借阅限额">
          <el-input-number v-model="formData.borrow_limit" :min="1" :max="20" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { readerApi } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const isEdit = ref(false)

const dialogTitle = computed(() => (isEdit.value ? '编辑读者' : '新增读者'))

const formData = reactive({
  id: null,
  username: '',
  password: '',
  name: '',
  gender: null,
  phone: '',
  email: '',
  id_card: '',
  address: '',
  borrow_limit: 5
})

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
  ],
  id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

const getStatusType = (status) => {
  const typeMap = {
    active: 'success',
    suspended: 'warning',
    closed: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    active: '正常',
    suspended: '挂失',
    closed: '注销'
  }
  return textMap[status] || status
}

const fetchReaders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (searchForm.keyword) {
      params.search = searchForm.keyword
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }

    const res = await readerApi.getList(params)
    if (res.results) {
      tableData.value = res.results
      pagination.total = res.count
    } else if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    }
  } catch (error) {
    console.error('Failed to fetch readers:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchReaders()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchReaders()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchReaders()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(formData, {
    id: null,
    username: '',
    password: '',
    name: '',
    gender: null,
    phone: '',
    email: '',
    id_card: '',
    address: '',
    borrow_limit: 5
  })
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  isEdit.value = true
  try {
    const detail = await readerApi.getDetail(row.id)
    Object.assign(formData, {
      id: detail.id,
      username: detail.username || '',
      password: '',
      name: detail.name,
      gender: detail.gender,
      phone: detail.phone,
      email: detail.email || '',
      id_card: detail.id_card,
      address: detail.address || '',
      borrow_limit: detail.borrow_limit
    })
  } catch (error) {
    console.error('Failed to fetch reader detail:', error)
    Object.assign(formData, {
      id: row.id,
      username: row.username || '',
      password: '',
      name: row.name,
      gender: row.gender,
      phone: row.phone,
      email: row.email || '',
      id_card: row.id_card,
      address: row.address || '',
      borrow_limit: row.borrow_limit
    })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await readerApi.update(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await readerApi.create(formData)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchReaders()
  } catch (error) {
    console.error('Failed to submit reader:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleSuspend = (row) => {
  ElMessageBox.confirm(`确定要挂失读者"${row.name}"的读者证吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await readerApi.suspend(row.id)
      ElMessage.success('挂失成功')
      fetchReaders()
    } catch (error) {
      console.error('Failed to suspend reader:', error)
    }
  }).catch(() => {})
}

const handleActivate = (row) => {
  ElMessageBox.confirm(`确定要激活读者"${row.name}"的读者证吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await readerApi.activate(row.id)
      ElMessage.success('激活成功')
      fetchReaders()
    } catch (error) {
      console.error('Failed to activate reader:', error)
    }
  }).catch(() => {})
}

const handleClose = (row) => {
  ElMessageBox.confirm(`确定要注销读者"${row.name}"的读者证吗？注销后无法恢复。`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await readerApi.close(row.id)
      ElMessage.success('注销成功')
      fetchReaders()
    } catch (error) {
      console.error('Failed to close reader:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchReaders()
})
</script>

<style scoped>
.reader-list-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
