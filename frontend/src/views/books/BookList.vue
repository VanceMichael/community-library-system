<template>
  <div class="book-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>图书列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加图书
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="书名/ISBN">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入书名或ISBN"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="请选择分类" clearable>
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="可借" value="available" />
            <el-option label="已借出" value="borrowed" />
            <el-option label="已预约" value="reserved" />
            <el-option label="维护中" value="maintenance" />
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
        <el-table-column prop="isbn" label="ISBN" width="140" />
        <el-table-column prop="title" label="书名" min-width="200" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="location" label="馆藏位置" width="100" />
        <el-table-column prop="total_copies" label="总馆藏" width="80" align="center" />
        <el-table-column prop="available_copies" label="可借数量" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.available_copies > 0 ? 'success' : 'danger'">
              {{ scope.row.available_copies }}
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
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="scope">
            <div class="table-actions">
              <el-button type="primary" link @click="handleEdit(scope.row)">
                编辑
              </el-button>
              <el-button type="danger" link @click="handleDelete(scope.row)">
                删除
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
        <el-form-item label="分类" prop="category">
          <el-select v-model="formData.category" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="馆藏位置" prop="location">
          <el-input v-model="formData.location" placeholder="请输入馆藏位置" />
        </el-form-item>
        <el-form-item label="总馆藏数" prop="total_copies">
          <el-input-number v-model="formData.total_copies" :min="1" />
        </el-form-item>
        <el-form-item label="可借数量" prop="available_copies">
          <el-input-number v-model="formData.available_copies" :min="0" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="formData.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="图书描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入图书描述" />
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
import { bookApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  keyword: '',
  category: null,
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const categories = ref([])

const isEdit = ref(false)

const dialogTitle = computed(() => (isEdit.value ? '编辑图书' : '添加图书'))

const formData = reactive({
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  category: null,
  location: '',
  total_copies: 1,
  available_copies: 1,
  price: null,
  description: ''
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
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  location: [
    { required: true, message: '请输入馆藏位置', trigger: 'blur' }
  ],
  total_copies: [
    { required: true, message: '请输入总馆藏数', trigger: 'blur' }
  ],
  available_copies: [
    { required: true, message: '请输入可借数量', trigger: 'blur' }
  ]
}

const getStatusType = (status) => {
  const typeMap = {
    available: 'success',
    borrowed: 'warning',
    reserved: 'info',
    maintenance: 'info',
    lost: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    available: '可借',
    borrowed: '已借出',
    reserved: '已预约',
    maintenance: '维护中',
    lost: '已丢失'
  }
  return textMap[status] || status
}

const fetchCategories = async () => {
  try {
    const res = await bookApi.getCategories()
    categories.value = Array.isArray(res) ? res : (res.results || [])
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const fetchBooks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (searchForm.keyword) {
      params.search = searchForm.keyword
    }
    if (searchForm.category) {
      params.category = searchForm.category
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }

    const res = await bookApi.getList(params)
    if (res.results) {
      tableData.value = res.results
      pagination.total = res.count
    } else if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    }
  } catch (error) {
    console.error('Failed to fetch books:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchBooks()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.category = null
  searchForm.status = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchBooks()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchBooks()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(formData, {
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    category: null,
    location: '',
    total_copies: 1,
    available_copies: 1,
    price: null,
    description: ''
  })
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  isEdit.value = true
  try {
    const detail = await bookApi.getDetail(row.id)
    Object.assign(formData, {
      id: detail.id,
      isbn: detail.isbn,
      title: detail.title,
      author: detail.author,
      publisher: detail.publisher || '',
      category: detail.category,
      location: detail.location,
      total_copies: detail.total_copies,
      available_copies: detail.available_copies,
      price: detail.price,
      description: detail.description || ''
    })
  } catch (error) {
    console.error('Failed to fetch book detail:', error)
    Object.assign(formData, {
      id: row.id,
      isbn: row.isbn,
      title: row.title,
      author: row.author,
      publisher: row.publisher || '',
      category: row.category,
      location: row.location,
      total_copies: row.total_copies,
      available_copies: row.available_copies,
      price: row.price,
      description: row.description || ''
    })
  }
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除图书《${row.title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await bookApi.delete(row.id)
      ElMessage.success('删除成功')
      fetchBooks()
    } catch (error) {
      console.error('Failed to delete book:', error)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await bookApi.update(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await bookApi.create(formData)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchBooks()
  } catch (error) {
    console.error('Failed to submit book:', error)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchBooks()
})
</script>

<style scoped>
.book-list-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
