<!-- 仪表盘图表 - 用于综合评分展示 -->
<template>
  <div
    ref="chartRef"
    class="relative w-full"
    :style="{ height: props.height }"
    v-loading="props.loading"
  ></div>
</template>

<script setup lang="ts">
  import { useChartOps, useChartComponent } from '@/hooks/core/useChart'
  import { getCssVar } from '@/utils/ui'
  import { graphic, type EChartsOption } from '@/plugins/echarts'

  defineOptions({ name: 'ArtGaugeChart' })

  export interface GaugeChartProps {
    /** 图表高度 */
    height?: string
    /** 是否加载中 */
    loading?: boolean
    /** 是否为空 */
    isEmpty?: boolean
    /** 仪表盘数值 (0-100) */
    value?: number
    /** 仪表盘名称 */
    name?: string
    /** 最小值 */
    min?: number
    /** 最大值 */
    max?: number
    /** 仪表盘半径 */
    radius?: string
    /** 自定义颜色，不提供则根据数值自动变化 */
    color?: string
  }

  const props = withDefaults(defineProps<GaugeChartProps>(), {
    height: '280px',
    loading: false,
    isEmpty: false,
    value: 0,
    name: '综合评分',
    min: 0,
    max: 100,
    radius: '75%',
    color: ''
  })

  // 根据数值获取颜色
  const getGaugeColor = (val: number) => {
    if (props.color) return props.color
    // 0-60 红色, 60-80 黄色, 80-100 绿色
    if (val < 60) return '#F56C6C'
    if (val < 80) return '#E6A23C'
    return '#67C23A'
  }

  // 根据数值获取背景色
  const getGaugeBgColor = (val: number) => {
    if (val < 60) return 'rgba(245, 108, 108, 0.1)'
    if (val < 80) return 'rgba(230, 162, 60, 0.1)'
    return 'rgba(103, 194, 58, 0.1)'
  }

  const { chartRef, isDark, getAnimationConfig } = useChartComponent({
    props,
    checkEmpty: () => props.value === 0 && !props.name,
    watchSources: [() => props.value, () => props.name, () => props.color],
    generateOptions: (): EChartsOption => {
      const color = getGaugeColor(props.value)
      const bgColor = getGaugeBgColor(props.value)

      return {
        series: [
          {
            type: 'gauge',
            radius: props.radius,
            center: ['50%', '60%'],
            startAngle: 200,
            endAngle: -20,
            min: props.min,
            max: props.max,
            splitNumber: 10,
            itemStyle: {
              color: color
            },
            progress: {
              show: true,
              width: 18,
              itemStyle: {
                color: new graphic.LinearGradient(0, 0, 1, 0, [
                  { offset: 0, color: color },
                  { offset: 1, color: color }
                ])
              }
            },
            pointer: {
              show: false
            },
            axisLine: {
              lineStyle: {
                width: 18,
                color: [[1, isDark.value ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)']]
              }
            },
            axisTick: {
              show: false
            },
            splitLine: {
              show: false
            },
            axisLabel: {
              show: false
            },
            anchor: {
              show: false
            },
            title: {
              show: true,
              offsetCenter: [0, '20%'],
              fontSize: 14,
              color: isDark.value ? '#ccc' : '#999'
            },
            detail: {
              valueAnimation: true,
              offsetCenter: [0, '-10%'],
              fontSize: 42,
              fontWeight: 'bold',
              formatter: '{value}',
              color: color
            },
            data: [
              {
                value: props.value,
                name: props.name
              }
            ],
            ...getAnimationConfig(200, 1500)
          }
        ],
        backgroundColor: 'transparent'
      }
    }
  })
</script>
