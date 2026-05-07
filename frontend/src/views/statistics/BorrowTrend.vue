<template>
  <div class="borrow-trend-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>借阅趋势</span>
          <el-select v-model="days" @change="handleDaysChange" style="width: 150px;">
            <el-option label="近7天" :value="7" />
            <el-option label="近30天" :value="30" />
            <el-option label="近90天" :value="90" />
          </el-select>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="24">
          <div ref="chartContainer" style="height: 400px;">
            <Line :data="chartData" :options="chartOptions" />
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalBorrows }}</div>
                <div class="stat-label">总借阅数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalReturns }}</div>
                <div class="stat-label">总归还数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.netChange >= 0 ? '+' : '' }}{{ stats.netChange }}</div>
                <div class="stat-label">净变化</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.avgDaily }}</div>
                <div class="stat-label">日均借阅</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
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
  Filler
)

const loading = ref(false)
const days = ref(30)
const trendData = ref([])

const stats = computed(() => {
  const totalBorrows = trendData.value.reduce((sum, item) => sum + (item.borrow_count || 0), 0)
  const totalReturns = trendData.value.reduce((sum, item) => sum + (item.return_count || 0), 0)
  const netChange = totalBorrows - totalReturns
  const avgDaily = trendData.value.length > 0 ? Math.round(totalBorrows / trendData.value.length) : 0

  return {
    totalBorrows,
    totalReturns,
    netChange,
    avgDaily
  }
})

const chartData = computed(() => ({
  labels: trendData.value.map(item => item.date),
  datasets: [
    {
      label: '借阅数量',
      data: trendData.value.map(item => item.borrow_count || 0),
      borderColor: '#667eea',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6
    },
    {
      label: '归还数量',
      data: trendData.value.map(item => item.return_count || 0),
      borderColor: '#43e97b',
      backgroundColor: 'rgba(67, 233, 123, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false
  },
  plugins: {
    legend: {
      display: true,
      position: 'top'
    },
    title: {
      display: true,
      text: `借阅趋势分析（近${days.value}天）`,
      font: {
        size: 18,
        weight: 'bold'
      }
    },
    tooltip: {
      mode: 'index',
      intersect: false
    }
  },
  scales: {
    x: {
      display: true,
      title: {
        display: true,
        text: '日期'
      }
    },
    y: {
      display: true,
      title: {
        display: true,
        text: '数量'
      },
      beginAtZero: true
    }
  }
}

const fetchTrend = async () => {
  loading.value = true
  try {
    const res = await statisticsApi.getBorrowTrend({ days: days.value })
    trendData.value = Array.isArray(res) ? res : (res.results || [])
  } catch (error) {
    console.error('Failed to fetch borrow trend:', error)
  } finally {
    loading.value = false
  }
}

const handleDaysChange = () => {
  fetchTrend()
}

onMounted(() => {
  fetchTrend()
})
</script>

<style scoped>
.borrow-trend-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-info {
  margin-left: 16px;

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
  }

  .stat-label {
    font-size: 14px;
    color: #909399;
    margin-top: 4px;
  }
}
</style>
