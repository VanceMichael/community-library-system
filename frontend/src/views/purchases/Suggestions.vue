<template>
  <div class="suggestions-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购建议</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增建议
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="isbn" label="ISBN" width="140" />
        <el-table-column prop="title" label="书名" min-width="200" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="reader_name" label="推荐人" width="100" />
        <el-table-column prop="reason" label="推荐理由" min-width="200" show-overflow-tooltip />
        <el-table-column prop="quantity" label="推荐数量" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="scope">
            <div class="table-actions">
              <el-button
                v-if="isAdmin && scope.row.status === 'pending'"
                type="success"
                link
                @click="handleApprove(scope.row)"
              >
                批准
              </el-button>
              <el-button
                v-if="isAdmin && scope.row.status === 'pending'"
                type="danger"
                link
                @click="handleReject(scope.row)"
              >
                拒绝
              </el-button>
              <el-button
                v-if="scope.row.status === 'pending'"
                type="warning"
                link
                @click="handleCancel(scope.row)"
              >
                取消
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
      title="新增采购建议"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="formData.isbn" placeholder="请输入ISBN" />
        </el-form-item>
        <el-form-item label="书名" prop="title">
          <el-input v-model="formData.title" placeholder="请输入书名" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="formData.author" placeholder="请输入作者" />
        </el-form-item>
        <el-form-item label="出版社">
          <el-input v-model="formData.publisher" placeholder="请输入出版社" />
        </el-form-item>
        <el-form-item label="推荐数量">
          <el-input-number v-model="formData.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="推荐理由" prop="reason">
          <el-input v-model="formData.reason" type="textarea" :rows="3" placeholder="请输入推荐理由" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { purchaseApi, readerApi } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)

const currentUser = ref({
  is_staff: false,
  is_superuser: false,
  is_reader: false
})

const isAdmin = computed(() => {
  return currentUser.value.is_staff || currentUser.value.is_superuser
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])

const formData = reactive({
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  quantity: 1,
  reason: ''
})

const formRules = {
  isbn: [
    { required: true, message: '请输入ISBN', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入书名', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请输入推荐理由', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    purchased: 'primary',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '待审核',
    approved: '已批准',
    rejected: '已拒绝',
    purchased: '已采购',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

const fetchCurrentUser = async () => {
  try {
    const res = await readerApi.getCurrentUser()
    Object.assign(currentUser.value, res)
  } catch (error) {
    console.error('Failed to fetch current user:', error)
  }
}

const fetchSuggestions = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    const res = await purchaseApi.getSuggestions(params)
    if (res.results) {
      tableData.value = res.results
      pagination.total = res.count
    } else if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    }
  } catch (error) {
    console.error('Failed to fetch suggestions:', error)
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchSuggestions()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchSuggestions()
}

const handleAdd = () => {
  Object.assign(formData, {
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    quantity: 1,
    reason: ''
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    await purchaseApi.createSuggestion(formData)
    ElMessage.success('提交成功')
    dialogVisible.value = false
    fetchSuggestions()
  } catch (error) {
    console.error('Failed to submit suggestion:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleApprove = (row) => {
  ElMessageBox.prompt('请输入审核意见（可选）', '批准采购建议', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async ({ value }) => {
    try {
      await purchaseApi.reviewSuggestion(row.id, {
        status: 'approved',
        review_comment: value || ''
      })
      ElMessage.success('批准成功')
      fetchSuggestions()
    } catch (error) {
      console.error('Failed to approve suggestion:', error)
    }
  }).catch(() => {})
}

const handleReject = (row) => {
  ElMessageBox.prompt('请输入拒绝原因', '拒绝采购建议', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.+/,
    inputErrorMessage: '请输入拒绝原因'
  }).then(async ({ value }) => {
    try {
      await purchaseApi.reviewSuggestion(row.id, {
        status: 'rejected',
        review_comment: value
      })
      ElMessage.success('拒绝成功')
      fetchSuggestions()
    } catch (error) {
      console.error('Failed to reject suggestion:', error)
    }
  }).catch(() => {})
}

const handleCancel = (row) => {
  ElMessageBox.confirm(`确定要取消采购建议《${row.title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await purchaseApi.cancelSuggestion(row.id)
      ElMessage.success('取消成功')
      fetchSuggestions()
    } catch (error) {
      console.error('Failed to cancel suggestion:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchCurrentUser()
  fetchSuggestions()
})
</script>

<style scoped>
.suggestions-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
