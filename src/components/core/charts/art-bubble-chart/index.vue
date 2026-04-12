<!-- 气泡图 - 用于技能可视化 -->
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

  defineOptions({ name: 'ArtBubbleChart' })

  export interface SkillBubble {
    /** 技能名称 */
    name: string
    /** 掌握程度 (0-1) */
    mastery: number
    /** 相关度/重要度 (0-1) */
    relevance: number
    /** 气泡大小权重 (默认1) */
    weight?: number
  }

  export interface BubbleChartProps {
    /** 图表高度 */
    height?: string
    /** 是否加载中 */
    loading?: boolean
    /** 是否为空 */
    isEmpty?: boolean
    /** 气泡数据 */
    data?: SkillBubble[]
    /** 颜色配置 */
    colors?: string[]
  }

  const props = withDefaults(defineProps<BubbleChartProps>(), {
    height: '300px',
    loading: false,
    isEmpty: false,
    data: () => [],
    colors: () => ['#67C23A', '#E6A23C', '#F56C6C']
  })

  // 根据 mastery 获取颜色
  const getBubbleColor = (mastery: number) => {
    if (mastery >= 0.7) return props.colors![0] // 绿色 - 已掌握
    if (mastery >= 0.4) return props.colors![1] // 黄色 -学习中
    return props.colors![2] // 红色 - 需提升
  }

  const { chartRef, isDark, getAnimationConfig, getTooltipStyle } = useChartComponent({
    props,
    checkEmpty: () => !props.data?.length,
    watchSources: [() => props.data, () => props.colors],
    generateOptions: (): EChartsOption => {
      // 将技能数据转换为散点图数据
      // x = relevance (相关度), y = mastery (掌握度), size = weight * 50
      const scatterData = props.data.map((item) => ({
        name: item.name,
        value: [
          item.relevance * 100, // x轴: 相关度
          item.mastery * 100, // y轴: 掌握度
          (item.weight || 1) * 50 // 气泡大小
        ],
        itemStyle: {
          color: new graphic.RadialGradient(0.5, 0.5, 0.5, [
            { offset: 0, color: getBubbleColor(item.mastery) },
            { offset: 1, color: getBubbleColor(item.mastery) + '99' }
          ])
        },
        mastery: item.mastery,
        relevance: item.relevance
      }))

      return {
        grid: {
          top: 40,
          right: 40,
          bottom: 50,
          left: 60
        },
        tooltip: getTooltipStyle('item', {
          formatter: (params: any) => {
            const data = params.data
            const masteryPercent = Math.round(data.mastery * 100)
            const relevancePercent = Math.round(data.relevance * 100)
            return `<div style="font-weight: 600">${data.name}</div>
                    <div style="color: #999; font-size: 12px">
                      掌握度: ${masteryPercent}% | 相关度: ${relevancePercent}%
                    </div>`
          }
        }),
        xAxis: {
          type: 'value',
          name: '相关度',
          nameLocation: 'middle',
          nameGap: 30,
          nameTextStyle: {
            color: isDark.value ? '#999' : '#666',
            fontSize: 12
          },
          min: 0,
          max: 100,
          axisLine: {
            lineStyle: {
              color: isDark.value ? '#444' : '#ddd'
            }
          },
          axisLabel: {
            color: isDark.value ? '#999' : '#666',
            formatter: '{value}%'
          },
          splitLine: {
            lineStyle: {
              color: isDark.value ? '#333' : '#eee',
              type: 'dashed'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '掌握度',
          nameLocation: 'middle',
          nameGap: 40,
          nameTextStyle: {
            color: isDark.value ? '#999' : '#666',
            fontSize: 12
          },
          min: 0,
          max: 100,
          axisLine: {
            lineStyle: {
              color: isDark.value ? '#444' : '#ddd'
            }
          },
          axisLabel: {
            color: isDark.value ? '#999' : '#666',
            formatter: '{value}%'
          },
          splitLine: {
            lineStyle: {
              color: isDark.value ? '#333' : '#eee',
              type: 'dashed'
            }
          }
        },
        series: [
          {
            type: 'scatter',
            data: scatterData,
            symbolSize: (val: number[]) => Math.sqrt(val[2]) * 2,
            label: {
              show: true,
              position: 'top',
              formatter: '{b}',
              color: isDark.value ? '#ccc' : '#666',
              fontSize: 12
            },
            emphasis: {
              scale: 1.3,
              label: {
                show: true,
                fontWeight: 'bold'
              }
            },
            ...getAnimationConfig(100, 1200)
          }
        ]
      }
    }
  })
</script>
