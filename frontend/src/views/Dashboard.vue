<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.books?.total_books || 0 }}</div>
              <div class="stat-label">图书总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.readers?.total_readers || 0 }}</div>
              <div class="stat-label">读者总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.borrowings?.active_borrowings || 0 }}</div>
              <div class="stat-label">当前借阅</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.borrowings?.overdue_borrowings || 0 }}</div>
              <div class="stat-label">逾期记录</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>热门图书 Top 10</span>
          </template>
          <el-table :data="hotBooks" stripe style="width: 100%">
            <el-table-column prop="borrow_count" label="借阅次数" width="100">
              <template #default="scope">
                <el-tag type="primary">{{ scope.row.borrow_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="书名" />
            <el-table-column prop="author" label="作者" width="120" />
            <el-table-column prop="category_name" label="分类" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>借阅趋势 (近30天)</span>
          </template>
          <div ref="chartContainer" style="height: 300px;">
            <Line :data="chartData" :options="chartOptions" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>分类统计</span>
          </template>
          <div ref="pieChartContainer" style="height: 300px;">
            <Doughnut :data="categoryChartData" :options="categoryChartOptions" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>读者活跃情况</span>
          </template>
          <el-table :data="readerStats" stripe style="width: 100%">
            <el-table-column prop="name" label="状态" width="150">
              <template #default="scope">
                <el-tag :type="scope.row.type">{{ scope.row.name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="value" label="数量" width="150">
              <template #default="scope">
                <strong>{{ scope.row.value }}</strong>
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="占比">
              <template #default="scope">
                <el-progress
                  :percentage="scope.row.percentage"
                  :status="scope.row.type === '活跃' ? 'success' : scope.row.type === '挂失' ? 'warning' : 'info'"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { statisticsApi } from '@/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

const statistics = reactive({
  books: {},
  readers: {},
  borrowings: {},
  fines: {}
})

const hotBooks = ref([])

const chartData = ref({
  labels: [],
  datasets: [
    {
      label: '借阅数量',
      data: [],
      borderColor: '#667eea',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      fill: true,
      tension: 0.4
    },
    {
      label: '归还数量',
      data: [],
      borderColor: '#f5576c',
      backgroundColor: 'rgba(245, 87, 108, 0.1)',
      fill: true,
      tension: 0.4
    }
  ]
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

const categoryChartData = ref({
  labels: [],
  datasets: [
    {
      data: [],
      backgroundColor: [
        '#667eea',
        '#f5576c',
        '#4facfe',
        '#fa709a',
        '#43e97b',
        '#38f9d7',
        '#f093fb',
        '#4facfe'
      ]
    }
  ]
})

const categoryChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'right'
    }
  }
}

const readerStats = ref([])

const fetchStatistics = async () => {
  try {
    const res = await statisticsApi.getDashboard()
    Object.assign(statistics, res)

    const total = statistics.readers.total_readers || 1
    readerStats.value = [
      {
        name: '活跃',
        value: statistics.readers.active_readers || 0,
        percentage: Math.round(((statistics.readers.active_readers || 0) / total) * 100),
        type: 'success'
      },
      {
        name: '挂失',
        value: statistics.readers.suspended_readers || 0,
        percentage: Math.round(((statistics.readers.suspended_readers || 0) / total) * 100),
        type: 'warning'
      },
      {
        name: '注销',
        value: statistics.readers.closed_readers || 0,
        percentage: Math.round(((statistics.readers.closed_readers || 0) / total) * 100),
        type: 'info'
      }
    ]
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  }
}

const fetchHotBooks = async () => {
  try {
    const res = await statisticsApi.getHotBooks({ limit: 10 })
    hotBooks.value = res
  } catch (error) {
    console.error('Failed to fetch hot books:', error)
  }
}

const fetchBorrowTrend = async () => {
  try {
    const res = await statisticsApi.getBorrowTrend({ days: 30 })
    chartData.value = {
      labels: res.map(item => item.date),
      datasets: [
        {
          label: '借阅数量',
          data: res.map(item => item.borrow_count),
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: '归还数量',
          data: res.map(item => item.return_count),
          borderColor: '#f5576c',
          backgroundColor: 'rgba(245, 87, 108, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    }
  } catch (error) {
    console.error('Failed to fetch borrow trend:', error)
  }
}

const fetchCategoryStatistics = async () => {
  try {
    const res = await statisticsApi.getCategoryStatistics()
    categoryChartData.value = {
      labels: res.map(item => item.category_name),
      datasets: [
        {
          data: res.map(item => item.book_count),
          backgroundColor: [
            '#667eea',
            '#f5576c',
            '#4facfe',
            '#fa709a',
            '#43e97b',
            '#38f9d7',
            '#f093fb',
            '#4facfe'
          ]
        }
      ]
    }
  } catch (error) {
    console.error('Failed to fetch category statistics:', error)
  }
}

onMounted(() => {
  fetchStatistics()
  fetchHotBooks()
  fetchBorrowTrend()
  fetchCategoryStatistics()
})
</script>

<style scoped>
.dashboard-container {
  width: 100%;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-card {
  .el-card__body {
    padding: 20px;
  }
}
</style>
