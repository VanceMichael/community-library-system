<template>
  <div class="reservations-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预约管理</span>
          <el-button type="primary" @click="handleCreateReservation">
            <el-icon><Plus /></el-icon>
            新建预约
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="读者/书名">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入读者姓名或书名"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="等待中" value="pending" />
            <el-option label="可领取" value="available" />
            <el-option label="已领取" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已过期" value="expired" />
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
        <el-table-column prop="reader_name" label="读者" width="120" />
        <el-table-column prop="book_title" label="书名" min-width="200" />
        <el-table-column prop="reserve_date" label="预约日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.reserve_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="available_date" label="可领取日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.available_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="expire_date" label="过期日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.expire_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="queue_position" label="队列位置" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="scope">
            <div class="table-actions">
              <el-button
                v-if="scope.row.status === 'pending' || scope.row.status === 'available'"
                type="warning"
                link
                @click="handleCancel(scope.row)"
              >
                取消
              </el-button>
              <el-button
                v-if="scope.row.status === 'available'"
                type="success"
                link
                @click="handleClaim(scope.row)"
              >
                领取
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-empty
        v-if="!loading && tableData.length === 0"
        description="暂无预约记录"
        :image-size="60"
      >
        <el-button type="primary" @click="handleCreateReservation">
          新建预约
        </el-button>
      </el-empty>

      <div class="pagination-container" v-if="pagination.total > 0">
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
      v-model="reservationDialogVisible"
      title="新建预约"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="reservationFormRef"
        :model="reservationForm"
        :rules="reservationRules"
        label-width="100px"
      >
        <el-form-item label="选择读者" prop="reader_id">
          <el-select
            v-model="reservationForm.reader_id"
            placeholder="请选择读者"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="reader in readers"
              :key="reader.id"
              :label="`${reader.name} (${reader.reader_id})`"
              :value="reader.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择图书" prop="book_id">
          <el-select
            v-model="reservationForm.book_id"
            placeholder="请选择图书"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="book in availableBooks"
              :key="book.id"
              :label="`${book.title} (${book.isbn})`"
              :value="book.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reservationDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="reservationLoading" @click="handleSubmitReservation">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { borrowingApi, readerApi, bookApi } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const reservationLoading = ref(false)
const reservationDialogVisible = ref(false)
const reservationFormRef = ref(null)

const searchForm = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const reservationForm = reactive({
  reader_id: null,
  book_id: null
})

const reservationRules = {
  reader_id: [
    { required: true, message: '请选择读者', trigger: 'change' }
  ],
  book_id: [
    { required: true, message: '请选择图书', trigger: 'change' }
  ]
}

const tableData = ref([])
const readers = ref([])
const availableBooks = ref([])

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    available: 'success',
    completed: 'primary',
    cancelled: 'info',
    expired: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '等待中',
    available: '可领取',
    completed: '已领取',
    cancelled: '已取消',
    expired: '已过期'
  }
  return textMap[status] || status
}

const fetchReservations = async () => {
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

    const res = await borrowingApi.getReservations(params)
    if (res.results) {
      tableData.value = res.results
      pagination.total = res.count
    } else if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    } else {
      tableData.value = []
      pagination.total = 0
    }
  } catch (error) {
    console.error('Failed to fetch reservations:', error)
    ElMessage.error('获取预约列表失败')
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const fetchReaders = async () => {
  try {
    const res = await readerApi.getList({ page_size: 1000 })
    readers.value = res.results || res || []
  } catch (error) {
    console.error('Failed to fetch readers:', error)
  }
}

const fetchAvailableBooks = async () => {
  try {
    const res = await bookApi.getList({ page_size: 1000 })
    availableBooks.value = res.results || res || []
  } catch (error) {
    console.error('Failed to fetch books:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchReservations()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchReservations()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchReservations()
}

const handleCreateReservation = () => {
  reservationForm.reader_id = null
  reservationForm.book_id = null
  fetchReaders()
  fetchAvailableBooks()
  reservationDialogVisible.value = true
}

const handleSubmitReservation = async () => {
  const valid = await reservationFormRef.value.validate().catch(() => false)
  if (!valid) return

  reservationLoading.value = true
  try {
    await borrowingApi.createReservation(reservationForm)
    ElMessage.success('预约成功')
    reservationDialogVisible.value = false
    fetchReservations()
  } catch (error) {
    console.error('Failed to create reservation:', error)
  } finally {
    reservationLoading.value = false
  }
}

const handleCancel = (row) => {
  ElMessageBox.confirm(`确定要取消预约《${row.book_title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await borrowingApi.cancelReservation(row.id)
      ElMessage.success('取消成功')
      fetchReservations()
    } catch (error) {
      console.error('Failed to cancel reservation:', error)
    }
  }).catch(() => {})
}

const handleClaim = (row) => {
  ElMessageBox.confirm(`确定要领取预约的《${row.book_title}》吗？领取后将自动完成借阅。`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await borrowingApi.claimReservation(row.id)
      ElMessage.success('领取成功')
      fetchReservations()
    } catch (error) {
      console.error('Failed to claim reservation:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchReservations()
})
</script>

<style scoped>
.reservations-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.table-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>
