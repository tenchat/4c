<!-- 词云图 -->
<template>
  <div ref="chartRef" :style="{ height: props.height }" v-loading="props.loading"></div>
</template>

<script setup lang="ts">
  import { useChartOps } from '@/hooks/core/useChart'
  import { echarts, graphic } from '@/plugins/echarts'
  import type { EChartsOption } from '@/plugins/echarts'

  defineOptions({ name: 'ArtWordCloud' })

  export interface WordCloudItem {
    name: string
    value: number
  }

  export interface WordCloudProps {
    height?: string
    loading?: boolean
    data?: WordCloudItem[]
    sizeRange?: [number, number]
    rotationRange?: [number, number]
  }

  const props = withDefaults(defineProps<WordCloudProps>(), {
    height: '240px',
    loading: false,
    data: () => [],
    sizeRange: () => [12, 40],
    rotationRange: () => [-45, 45]
  })

  const chartRef = ref<HTMLDivElement>()
  let chartInstance: echarts.ECharts | null = null

  // 颜色列表
  const colors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#1677ff'
  ]

  const initChart = () => {
    if (!chartRef.value) return

    if (chartInstance) {
      chartInstance.dispose()
    }

    chartInstance = echarts.init(chartRef.value)

    const option: EChartsOption = {
      tooltip: {
        show: true,
        backgroundColor: 'rgba(0,0,0,0.7)',
        textStyle: { color: '#fff' },
        formatter: (params: any) => {
          return `${params.name}: ${params.value}次`
        }
      },
      series: [
        {
          type: 'wordCloud',
          shape: 'circle',
          left: 'center',
          top: 'center',
          width: '90%',
          height: '90%',
          sizeRange: props.sizeRange,
          rotationRange: props.rotationRange,
          rotationStep: 15,
          gridSize: 8,
          drawOutOfBound: false,
          textStyle: {
            fontFamily: 'sans-serif',
            fontWeight: 'bold',
            color: () => {
              return colors[Math.floor(Math.random() * colors.length)]
            }
          },
          emphasis: {
            textStyle: {
              shadowBlur: 10,
              shadowColor: '#333'
            }
          },
          data: props.data.map((item, index) => ({
            name: item.name,
            value: item.value,
            textStyle: {
              color: colors[index % colors.length]
            }
          }))
        }
      ]
    }

    chartInstance.setOption(option)
  }

  const resizeChart = () => {
    chartInstance?.resize()
  }

  watch(
    () => props.data,
    () => {
      initChart()
    },
    { deep: true }
  )

  onMounted(() => {
    nextTick(() => {
      initChart()
      window.addEventListener('resize', resizeChart)
    })
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', resizeChart)
    chartInstance?.dispose()
  })
</script>
