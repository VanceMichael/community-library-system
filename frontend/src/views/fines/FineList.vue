<template>
  <div class="fine-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>罚款记录</span>
          <el-button type="primary" @click="handleGenerate">
            <el-icon><Refresh /></el-icon>
            生成罚款
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="reader_name" label="读者" width="120" />
        <el-table-column prop="book_title" label="书名" min-width="200" />
        <el-table-column prop="amount" label="罚款金额" width="120" align="center">
          <template #default="scope">
            <span style="color: #f56c6c; font-weight: bold;">¥{{ scope.row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="overdue_days" label="逾期天数" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paid_date" label="缴纳日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.paid_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="scope">
            <div class="table-actions">
              <el-button
                v-if="scope.row.status === 'unpaid'"
                type="success"
                link
                @click="handlePay(scope.row)"
              >
                缴纳
              </el-button>
              <el-button
                v-if="scope.row.status === 'unpaid'"
                type="warning"
                link
                @click="handleWaive(scope.row)"
              >
                减免
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElInput } from 'element-plus'
import { fineApi } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const typeMap = {
    unpaid: 'danger',
    paid: 'success',
    waived: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    unpaid: '未缴纳',
    paid: '已缴纳',
    waived: '已减免'
  }
  return textMap[status] || status
}

const fetchFines = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    const res = await fineApi.getList(params)
    if (res.results) {
      tableData.value = res.results
      pagination.total = res.count
    } else if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    }
  } catch (error) {
    console.error('Failed to fetch fines:', error)
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  ElMessageBox.confirm('确定要生成逾期罚款记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await fineApi.generateFines()
      ElMessage.success(res.message || '生成成功')
      fetchFines()
    } catch (error) {
      console.error('Failed to generate fines:', error)
    }
  }).catch(() => {})
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchFines()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchFines()
}

const handlePay = (row) => {
  ElMessageBox.confirm(`确定要标记该罚款为已缴纳吗？金额：¥${row.amount}`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await fineApi.pay(row.id)
      ElMessage.success('缴纳成功')
      fetchFines()
    } catch (error) {
      console.error('Failed to pay fine:', error)
    }
  }).catch(() => {})
}

const handleWaive = (row) => {
  ElMessageBox.prompt('请输入减免原因', '减免罚款', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.+/,
    inputErrorMessage: '请输入减免原因'
  }).then(async ({ value }) => {
    try {
      await fineApi.waive(row.id, { remark: value })
      ElMessage.success('减免成功')
      fetchFines()
    } catch (error) {
      console.error('Failed to waive fine:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchFines()
})
</script>

<style scoped>
.fine-list-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
