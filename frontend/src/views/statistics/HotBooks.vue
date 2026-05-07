<template>
  <div class="hot-books-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>热门图书 Top 10</span>
          <el-select v-model="limit" @change="handleLimitChange" style="width: 120px;">
            <el-option label="Top 10" :value="10" />
            <el-option label="Top 20" :value="20" />
            <el-option label="Top 50" :value="50" />
          </el-select>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="16">
          <el-table :data="hotBooks" stripe style="width: 100%" v-loading="loading">
            <el-table-column type="index" label="排名" width="80" align="center">
              <template #default="scope">
                <el-tag v-if="scope.$index < 3" :type="getRankType(scope.$index)">
                  {{ scope.$index + 1 }}
                </el-tag>
                <span v-else>{{ scope.$index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="borrow_count" label="借阅次数" width="120" align="center">
              <template #default="scope">
                <el-tag type="primary" size="large">{{ scope.row.borrow_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="书名" min-width="200" />
            <el-table-column prop="author" label="作者" width="120" />
            <el-table-column prop="category_name" label="分类" width="120">
              <template #default="scope">
                <el-tag type="info">{{ scope.row.category_name }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="8">
          <div ref="chartContainer" style="height: 400px;">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { statisticsApi } from '@/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const loading = ref(false)
const limit = ref(10)
const hotBooks = ref([])

const chartData = computed(() => ({
  labels: hotBooks.value.slice(0, 10).map(item => item.title.length > 8 ? item.title.substring(0, 8) + '...' : item.title),
  datasets: [
    {
      label: '借阅次数',
      data: hotBooks.value.slice(0, 10).map(item => item.borrow_count),
      backgroundColor: [
        '#667eea',
        '#f5576c',
        '#4facfe',
        '#fa709a',
        '#43e97b',
        '#38f9d7',
        '#f093fb',
        '#4facfe',
        '#ff9a9e',
        '#fecfef'
      ],
      borderRadius: 8
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: {
      display: false
    },
    title: {
      display: true,
      text: '热门图书借阅排行',
      font: {
        size: 16
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: {
        stepSize: 10
      }
    }
  }
}

const getRankType = (index) => {
  if (index === 0) return 'warning'
  if (index === 1) return 'info'
  if (index === 2) return 'danger'
  return 'info'
}

const fetchHotBooks = async () => {
  loading.value = true
  try {
    const res = await statisticsApi.getHotBooks({ limit: limit.value })
    hotBooks.value = Array.isArray(res) ? res : (res.results || [])
  } catch (error) {
    console.error('Failed to fetch hot books:', error)
  } finally {
    loading.value = false
  }
}

const handleLimitChange = () => {
  fetchHotBooks()
}

onMounted(() => {
  fetchHotBooks()
})
</script>

<style scoped>
.hot-books-container {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
