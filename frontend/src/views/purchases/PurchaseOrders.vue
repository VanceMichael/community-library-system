<template>
  <div class="purchase-orders-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购订单</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增订单
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="order_number" label="订单编号" width="180" />
        <el-table-column prop="supplier" label="供应商" min-width="200" />
        <el-table-column prop="total_amount" label="总金额" width="120" align="center">
          <template #default="scope">
            <span style="font-weight: bold;">¥{{ scope.row.total_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right" align="center">
          <template #default="scope">
            <div class="table-actions">
              <el-button
                v-if="scope.row.status === 'draft'"
                type="primary"
                link
                @click="handleSubmit(scope.row)"
              >
                提交
              </el-button>
              <el-button
                v-if="scope.row.status === 'submitted'"
                type="success"
                link
                @click="handleApprove(scope.row)"
              >
                审批
              </el-button>
              <el-button
                v-if="scope.row.status === 'approved'"
                type="primary"
                link
                @click="handleOrder(scope.row)"
              >
                订购
              </el-button>
              <el-button
                v-if="scope.row.status === 'ordered'"
                type="success"
                link
                @click="handleReceive(scope.row)"
              >
                到货
              </el-button>
              <el-button
                v-if="scope.row.status === 'draft' || scope.row.status === 'submitted'"
                type="danger"
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
      title="新增采购订单"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="供应商" prop="supplier">
          <el-input v-model="formData.supplier" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="formData.contact_person" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="formData.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
        <el-form-item label="选择建议">
          <el-checkbox-group v-model="selectedSuggestions">
            <div v-for="suggestion in approvedSuggestions" :key="suggestion.id" class="suggestion-item">
              <el-checkbox :label="suggestion.id">
                <span style="font-weight: bold;">{{ suggestion.title }}</span>
                <span style="color: #909399; margin-left: 10px;">{{ suggestion.author }}</span>
                <span style="color: #909399; margin-left: 10px;">推荐数量: {{ suggestion.quantity }}</span>
              </el-checkbox>
            </div>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmitOrder">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { purchaseApi } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const approvedSuggestions = ref([])
const selectedSuggestions = ref([])

const formData = reactive({
  supplier: '',
  contact_person: '',
  contact_phone: '',
  remark: '',
  items: []
})

const formRules = {
  supplier: [
    { required: true, message: '请输入供应商名称', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const typeMap = {
    draft: 'info',
    submitted: 'warning',
    approved: 'primary',
    ordered: 'warning',
    received: 'success',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    submitted: '已提交',
    approved: '已批准',
    ordered: '已订购',
    received: '已到货',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    const res = await purchaseApi.getOrders(params)
    if (res.results) {
      tableData.value = res.results
      pagination.total = res.count
    } else if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    }
  } catch (error) {
    console.error('Failed to fetch orders:', error)
  } finally {
    loading.value = false
  }
}

const fetchApprovedSuggestions = async () => {
  try {
    const res = await purchaseApi.getApprovedSuggestions()
    if (Array.isArray(res)) {
      approvedSuggestions.value = res
    }
  } catch (error) {
    console.error('Failed to fetch approved suggestions:', error)
  }
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchOrders()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchOrders()
}

const handleAdd = async () => {
  Object.assign(formData, {
    supplier: '',
    contact_person: '',
    contact_phone: '',
    remark: '',
    items: []
  })
  selectedSuggestions.value = []
  await fetchApprovedSuggestions()
  if (approvedSuggestions.value.length === 0) {
    ElMessage.info('暂无已批准的采购建议，请先在采购建议页面批准建议')
    return
  }
  dialogVisible.value = true
}

const handleSubmitOrder = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (selectedSuggestions.value.length === 0) {
    ElMessage.warning('请至少选择一个采购建议')
    return
  }

  submitLoading.value = true
  try {
    const items = selectedSuggestions.value.map(id => {
      const suggestion = approvedSuggestions.value.find(s => s.id === id)
      return {
        purchase_suggestion: id,
        isbn: suggestion.isbn,
        title: suggestion.title,
        author: suggestion.author,
        publisher: suggestion.publisher,
        quantity: suggestion.quantity,
        unit_price: suggestion.price || 0,
        remark: ''
      }
    })

    const orderData = {
      supplier: formData.supplier,
      contact_person: formData.contact_person,
      contact_phone: formData.contact_phone,
      remark: formData.remark,
      items: items
    }

    await purchaseApi.createOrder(orderData)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchOrders()
  } catch (error) {
    console.error('Failed to create order:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleSubmit = (row) => {
  ElMessageBox.confirm(`确定要提交采购订单"${row.order_number}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await purchaseApi.submitOrder(row.id)
      ElMessage.success('提交成功')
      fetchOrders()
    } catch (error) {
      console.error('Failed to submit order:', error)
    }
  }).catch(() => {})
}

const handleApprove = (row) => {
  ElMessageBox.confirm(`确定要批准采购订单"${row.order_number}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await purchaseApi.approveOrder(row.id)
      ElMessage.success('审批成功')
      fetchOrders()
    } catch (error) {
      console.error('Failed to approve order:', error)
    }
  }).catch(() => {})
}

const handleOrder = (row) => {
  ElMessageBox.confirm(`确定要标记采购订单"${row.order_number}"为已订购吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await purchaseApi.orderPurchase(row.id)
      ElMessage.success('订购成功')
      fetchOrders()
    } catch (error) {
      console.error('Failed to order purchase:', error)
    }
  }).catch(() => {})
}

const handleReceive = (row) => {
  ElMessageBox.confirm(`确定要标记采购订单"${row.order_number}"为已到货吗？到货后将自动创建图书记录。`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await purchaseApi.receiveOrder(row.id)
      ElMessage.success('到货确认成功')
      fetchOrders()
    } catch (error) {
      console.error('Failed to receive order:', error)
    }
  }).catch(() => {})
}

const handleCancel = (row) => {
  ElMessageBox.confirm(`确定要取消采购订单"${row.order_number}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await purchaseApi.cancelOrder(row.id)
      ElMessage.success('取消成功')
      fetchOrders()
    } catch (error) {
      console.error('Failed to cancel order:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.purchase-orders-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
