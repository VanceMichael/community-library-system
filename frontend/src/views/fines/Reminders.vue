<template>
  <div class="reminders-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>逾期提醒</span>
          <el-button type="primary" @click="handleGenerate">
            <el-icon><Plus /></el-icon>
            生成提醒
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="reader_name" label="读者" width="120" />
        <el-table-column prop="book_title" label="书名" min-width="200" />
        <el-table-column prop="reminder_type" label="提醒方式" width="100" align="center">
          <template #default="scope">
            <el-tag>{{ getReminderTypeText(scope.row.reminder_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="提醒内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="reminder_date" label="提醒日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.reminder_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_sent" label="是否发送" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_sent ? 'success' : 'warning'">
              {{ scope.row.is_sent ? '已发送' : '未发送' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sent_date" label="发送日期" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.sent_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="scope">
            <div class="table-actions">
              <el-button
                v-if="!scope.row.is_sent"
                type="primary"
                link
                @click="handleMarkSent(scope.row)"
              >
                标记发送
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
import { ElMessage, ElMessageBox } from 'element-plus'
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

const getReminderTypeText = (type) => {
  const textMap = {
    email: '邮件',
    sms: '短信',
    phone: '电话',
    letter: '信函'
  }
  return textMap[type] || type
}

const fetchReminders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    const res = await fineApi.getReminders(params)
    if (res.results) {
      tableData.value = res.results
      pagination.total = res.count
    } else if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    }
  } catch (error) {
    console.error('Failed to fetch reminders:', error)
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  ElMessageBox.confirm('确定要生成逾期提醒记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await fineApi.generateReminders({ reminder_type: 'email' })
      ElMessage.success(res.message || '生成成功')
      fetchReminders()
    } catch (error) {
      console.error('Failed to generate reminders:', error)
    }
  }).catch(() => {})
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchReminders()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchReminders()
}

const handleMarkSent = (row) => {
  ElMessageBox.confirm('确定要标记该提醒为已发送吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await fineApi.markReminderSent(row.id)
      ElMessage.success('标记成功')
      fetchReminders()
    } catch (error) {
      console.error('Failed to mark reminder as sent:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchReminders()
})
</script>

<style scoped>
.reminders-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
