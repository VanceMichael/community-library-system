<template>
  <div class="borrowing-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>借阅记录</span>
          <el-button type="primary" @click="handleBorrow">
            <el-icon><Plus /></el-icon>
            借书
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
            <el-option label="借阅中" value="borrowed" />
            <el-option label="已归还" value="returned" />
            <el-option label="已逾期" value="overdue" />
            <el-option label="已丢失" value="lost" />
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
        <el-table-column prop="borrow_date" label="借书日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.borrow_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="应还日期" width="180">
          <template #default="scope">
            <span :class="{ 'overdue-text': scope.row.overdue_days > 0 && scope.row.status === 'borrowed' }">
              {{ formatDate(scope.row.due_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="return_date" label="归还日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.return_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="overdue_days" label="逾期天数" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.overdue_days > 0" type="danger">
              {{ scope.row.overdue_days }}天
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="renew_count" label="续借次数" width="100" align="center" />
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
                v-if="scope.row.status === 'borrowed'"
                type="success"
                link
                @click="handleReturn(scope.row)"
              >
                还书
              </el-button>
              <el-button
                v-if="scope.row.status === 'borrowed' && scope.row.renew_count < scope.row.max_renew_count && scope.row.overdue_days === 0"
                type="primary"
                link
                @click="handleRenew(scope.row)"
              >
                续借
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
      v-model="borrowDialogVisible"
      title="借书"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="borrowFormRef"
        :model="borrowForm"
        :rules="borrowRules"
        label-width="100px"
      >
        <el-form-item label="选择读者" prop="reader_id">
          <el-select
            v-model="borrowForm.reader_id"
            placeholder="请选择读者"
            filterable
            style="width: 100%"
            @change="checkReaderEligibility"
          >
            <el-option
              v-for="reader in readers"
              :key="reader.id"
              :label="`${reader.name} (${reader.reader_id})`"
              :value="reader.id"
            />
          </el-select>
          <div v-if="readerInfo" class="reader-info">
            <el-text type="info">
              借阅限额: {{ readerInfo.borrow_limit }} 本 | 当前借阅: {{ readerInfo.borrow_count }} 本
            </el-text>
          </div>
        </el-form-item>
        <el-form-item label="选择图书" prop="book_id">
          <el-select
            v-model="borrowForm.book_id"
            placeholder="请选择图书"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="book in availableBooks"
              :key="book.id"
              :label="`${book.title} (${book.isbn}) - 可借: ${book.available_copies}`"
              :value="book.id"
              :disabled="book.available_copies <= 0"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="borrowLoading" @click="handleSubmitBorrow">
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
const borrowLoading = ref(false)
const borrowDialogVisible = ref(false)
const borrowFormRef = ref(null)

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
const readers = ref([])
const availableBooks = ref([])
const readerInfo = ref(null)

const borrowForm = reactive({
  reader_id: null,
  book_id: null
})

const borrowRules = {
  reader_id: [
    { required: true, message: '请选择读者', trigger: 'change' }
  ],
  book_id: [
    { required: true, message: '请选择图书', trigger: 'change' }
  ]
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const typeMap = {
    borrowed: 'primary',
    returned: 'success',
    overdue: 'danger',
    lost: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    borrowed: '借阅中',
    returned: '已归还',
    overdue: '已逾期',
    lost: '已丢失'
  }
  return textMap[status] || status
}

const fetchBorrowings = async () => {
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

    const res = await borrowingApi.getBorrowings(params)
    if (res.results) {
      tableData.value = res.results
      pagination.total = res.count
    } else if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    }
  } catch (error) {
    console.error('Failed to fetch borrowings:', error)
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
    const res = await bookApi.getAvailable()
    availableBooks.value = Array.isArray(res) ? res : (res.results || [])
  } catch (error) {
    console.error('Failed to fetch available books:', error)
  }
}

const checkReaderEligibility = async (readerId) => {
  if (!readerId) {
    readerInfo.value = null
    return
  }
  try {
    const res = await readerApi.checkEligibility(readerId)
    readerInfo.value = res
  } catch (error) {
    console.error('Failed to check reader eligibility:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchBorrowings()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchBorrowings()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchBorrowings()
}

const handleBorrow = () => {
  borrowForm.reader_id = null
  borrowForm.book_id = null
  readerInfo.value = null
  borrowDialogVisible.value = true
}

const handleSubmitBorrow = async () => {
  const valid = await borrowFormRef.value.validate().catch(() => false)
  if (!valid) return

  borrowLoading.value = true
  try {
    await borrowingApi.createBorrowing(borrowForm)
    ElMessage.success('借书成功')
    borrowDialogVisible.value = false
    fetchBorrowings()
    fetchAvailableBooks()
  } catch (error) {
    console.error('Failed to create borrowing:', error)
  } finally {
    borrowLoading.value = false
  }
}

const handleReturn = (row) => {
  ElMessageBox.confirm(`确定要归还图书《${row.book_title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await borrowingApi.returnBook(row.id)
      ElMessage.success('还书成功')
      fetchBorrowings()
      fetchAvailableBooks()
    } catch (error) {
      console.error('Failed to return book:', error)
    }
  }).catch(() => {})
}

const handleRenew = (row) => {
  ElMessageBox.confirm(`确定要续借图书《${row.book_title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await borrowingApi.renew(row.id)
      ElMessage.success('续借成功')
      fetchBorrowings()
    } catch (error) {
      console.error('Failed to renew book:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchBorrowings()
  fetchReaders()
  fetchAvailableBooks()
})
</script>

<style scoped>
.borrowing-list-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overdue-text {
  color: #f56c6c;
  font-weight: bold;
}

.reader-info {
  margin-top: 8px;
}
</style>
