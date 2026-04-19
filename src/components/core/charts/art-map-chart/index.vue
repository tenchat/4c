<!-- 地图图表 -->
<template>
  <div class="relative w-full" :style="{ height: 'calc(100vh - 120px)' }">
    <div v-if="isEmpty" class="h-full flex-cc">
      <ElEmpty description="暂无地图数据" />
    </div>

    <div v-else id="china-map" ref="chinaMapRef" class="h-full w-full overflow-hidden rounded-lg" />

    <!-- 地图来源标注 -->
    <div class="absolute bottom-2 right-3 text-xs text-gray-400 z-10">
      地图来源：阿里云 DataV.GeoAtlas（审图号：GS(2025)5996 号）
    </div>
  </div>
</template>

<script setup lang="ts">
  import { echarts } from '@/plugins/echarts'
  import { useSettingStore } from '@/store/modules/setting'
  import chinaMapJson from '@/mock/json/chinaMap.json'
  import type { MapChartProps } from '@/types/component/chart'

  defineOptions({ name: 'ArtMapChart' })

  const chinaMapRef = ref<HTMLElement | null>(null)
  const chartInstance = shallowRef<echarts.ECharts | null>(null)
  const settingStore = useSettingStore()
  const { isDark } = storeToRefs(settingStore)

  const props = withDefaults(defineProps<MapChartProps>(), {
    mapData: () => [],
    selectedRegion: '',
    showLabels: true,
    showScatter: true,
    isEmpty: false
  })

  // 定义 emit
  const emit = defineEmits<{
    renderComplete: []
    regionClick: [region: { name: string; adcode: string; level: string }]
  }>()

  // 检查是否为空数据
  const isEmpty = computed(() => {
    return props.isEmpty || (!props.mapData?.length && !chinaMapJson)
  })

  // 省份名称标准化（去掉后缀以匹配数据库中的名称）
  const normalizeProvinceName = (name: string): string => {
    return name
      .replace(/市$/, '')
      .replace(/省$/, '')
      .replace(/自治区$/, '')
      .replace(/特别行政区$/, '')
      .replace(/壮族$/, '')
      .replace(/回族$/, '')
      .replace(/维吾尔$/, '')
  }

  // 根据 geoJson 数据准备地图数据
  const prepareMapData = (geoJson: {
    features: Array<{ properties: Record<string, unknown> }>
  }) => {
    return geoJson.features.map((feature) => ({
      name: feature.properties.name as string,
      value: Math.round(Math.random() * 1000),
      adcode: feature.properties.adcode as string,
      level: feature.properties.level as string,
      selected: false
    }))
  }

  // 获取主题相关的样式配置
  const getThemeStyles = () => ({
    borderColor: isDark.value ? 'rgba(255,255,255,0.6)' : 'rgba(147,235,248,1)',
    shadowColor: isDark.value ? 'rgba(0,0,0,0.8)' : 'rgba(128,217,248,1)',
    labelColor: isDark.value ? '#fff' : '#333',
    backgroundColor: isDark.value ? 'rgba(0,0,0,0.8)' : 'rgba(255,255,255,0.9)'
  })

  // 构造 ECharts 配置项
  const createChartOption = (mapData: Array<Record<string, unknown>>) => {
    const themeStyles = getThemeStyles()

    return {
      animation: false, // 关闭动画效果，减少鼠标移动高亮时的掉帧感
      tooltip: {
        show: true,
        backgroundColor: themeStyles.backgroundColor,
        borderColor: isDark.value ? '#333' : '#ddd',
        borderWidth: 1,
        textStyle: {
          color: themeStyles.labelColor
        },
        formatter: ({ data }: { data?: Record<string, unknown> }) => {
          if (!data) return ''
          const { name, bachelor, master, doctoral, total } = data
          return `
            <div style="padding: 8px; min-width: 160px;">
              <div style="font-size: 14px; font-weight: bold; margin-bottom: 6px; border-bottom: 1px solid #ddd; padding-bottom: 4px;">${name || '未知区域'}</div>
              <div style="display: flex; justify-content: space-between; margin: 3px 0;"><span>本科生:</span><span style="font-weight: bold;">${bachelor || 0} 人</span></div>
              <div style="display: flex; justify-content: space-between; margin: 3px 0;"><span>硕士生:</span><span style="font-weight: bold;">${master || 0} 人</span></div>
              <div style="display: flex; justify-content: space-between; margin: 3px 0;"><span>博士生:</span><span style="font-weight: bold;">${doctoral || 0} 人</span></div>
              <div style="display: flex; justify-content: space-between; margin: 3px 0; border-top: 1px solid #ddd; padding-top: 4px; font-weight: bold;"><span>总人数:</span><span>${total || 0} 人</span></div>
            </div>
          `
        }
      },
      geo: {
        map: 'china',
        zoom: 1,
        show: true,
        roam: false,
        scaleLimit: {
          min: 0.8,
          max: 3
        },
        layoutSize: '100%',
        emphasis: {
          label: { show: props.showLabels },
          itemStyle: {
            areaColor: 'rgba(82,180,255,0.9)',
            borderColor: '#fff',
            borderWidth: 3
          }
        },
        itemStyle: {
          borderColor: themeStyles.borderColor,
          borderWidth: 2,
          shadowColor: themeStyles.shadowColor,
          shadowOffsetX: 2,
          shadowOffsetY: 15,
          shadowBlur: 15
        }
      },
      series: [
        {
          type: 'map',
          map: 'china',
          aspectScale: 0.75,
          zoom: 1,
          label: {
            show: props.showLabels,
            color: '#fff',
            fontSize: 10
          },
          itemStyle: {
            borderColor: 'rgba(147,235,248,0.8)',
            borderWidth: 2,
            areaColor: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(147,235,248,0.3)' },
                { offset: 1, color: 'rgba(32,120,207,0.9)' }
              ]
            },
            shadowColor: 'rgba(32,120,207,1)',
            shadowOffsetY: 15,
            shadowBlur: 20
          },
          emphasis: {
            label: {
              show: true,
              color: '#fff',
              fontSize: 12
            },
            itemStyle: {
              areaColor: 'rgba(82,180,255,0.9)',
              borderColor: '#fff',
              borderWidth: 3
            }
          },
          select: {
            label: {
              show: true,
              color: '#fff',
              fontWeight: 'bold'
            },
            itemStyle: {
              areaColor: '#4FAEFB',
              borderColor: '#fff',
              borderWidth: 2
            }
          },
          data: mapData
        },
        // 散点标记配置（例如：城市标记）
        ...(props.showScatter
          ? [
              {
                name: '城市',
                type: 'scatter',
                coordinateSystem: 'geo',
                symbol: 'pin',
                symbolSize: 15,
                label: { show: false },
                itemStyle: {
                  color: '#F99020',
                  shadowBlur: 10,
                  shadowColor: '#333'
                },
                data: [
                  { name: '北京', value: [116.405285, 39.904989, 100] },
                  { name: '上海', value: [121.472644, 31.231706, 100] },
                  { name: '深圳', value: [114.085947, 22.547, 100] }
                ]
              }
            ]
          : [])
      ]
    }
  }

  // 初始化并渲染地图
  const initMap = async (): Promise<void> => {
    if (!chinaMapRef.value) return

    chartInstance.value = echarts.init(chinaMapRef.value)

    echarts.registerMap('china', chinaMapJson as any)

    // 如果有省份数据，合并到地图数据中
    let mapData: Array<Record<string, unknown>>
    if (props.mapData && props.mapData.length > 0) {
      // 使用省份数据，将province映射到name用于地图显示
      const provinceMap = new Map<string, Record<string, unknown>>()
      props.mapData.forEach((p: Record<string, unknown>) => {
        // 使用标准化后的省份名作为key
        const normalizedName = normalizeProvinceName(p.province as string)
        provinceMap.set(normalizedName, p)
      })

      // 基于geoJson创建地图数据，合并省份数据
      mapData = chinaMapJson.features.map((feature) => {
        const provinceName = feature.properties.name as string
        const normalizedName = normalizeProvinceName(provinceName)
        const provinceData = provinceMap.get(normalizedName)
        return {
          name: provinceName,
          adcode: feature.properties.adcode as string,
          level: feature.properties.level as string,
          province: provinceName,
          bachelor: provinceData?.bachelor || 0,
          master: provinceData?.master || 0,
          doctoral: provinceData?.doctoral || 0,
          total: provinceData?.total || 0,
          value: provinceData?.total || Math.round(Math.random() * 1000),
          selected: false
        }
      })
    } else {
      mapData = prepareMapData(chinaMapJson)
    }

    const option = createChartOption(mapData)

    chartInstance.value.setOption(option)

    // 绑定事件
    chartInstance.value.on('click', handleMapClick)

    emit('renderComplete')
  }

  // 处理地图点击事件
  const handleMapClick = (params: Record<string, unknown>) => {
    if (params.componentType === 'series') {
      const data = params.data as Record<string, unknown> | undefined
      const regionData = {
        name: params.name as string,
        adcode: (data?.adcode as string) || '',
        level: (data?.level as string) || ''
      }

      console.log(`选中区域: ${params.name}`, params)

      // 高亮选中区域
      chartInstance.value?.dispatchAction({
        type: 'select',
        seriesIndex: 0,
        dataIndex: params.dataIndex as number
      })

      emit('regionClick', regionData)
    }
  }

  // 窗口 resize 时调整图表大小
  const resizeChart = () => {
    chartInstance.value?.resize()
  }

  // 处理组件销毁
  const cleanupChart = () => {
    if (chartInstance.value) {
      chartInstance.value.off('click', handleMapClick)
      chartInstance.value.dispose()
      chartInstance.value = null
    }
    window.removeEventListener('resize', resizeChart)
  }

  // 生命周期钩子
  onMounted(() => {
    if (!isEmpty.value) {
      initMap().then(() => {
        setTimeout(resizeChart, 100)
      })
    }
    window.addEventListener('resize', resizeChart)
  })

  onUnmounted(cleanupChart)

  // 监听主题变化，重新初始化地图
  watch(isDark, (newVal, oldVal) => {
    if (newVal !== oldVal && chartInstance.value) {
      cleanupChart()
      nextTick(() => {
        if (!isEmpty.value) {
          initMap()
        }
      })
    }
  })

  // 监听数据变化
  watch(
    () => props.mapData,
    () => {
      if (chartInstance.value && !isEmpty.value) {
        // 和initMap一样的逻辑，合并省份数据到地图
        let mapData: Array<Record<string, unknown>>
        if (props.mapData && props.mapData.length > 0) {
          const provinceMap = new Map<string, Record<string, unknown>>()
          props.mapData.forEach((p: Record<string, unknown>) => {
            const normalizedName = normalizeProvinceName(p.province as string)
            provinceMap.set(normalizedName, p)
          })

          mapData = chinaMapJson.features.map((feature) => {
            const provinceName = feature.properties.name as string
            const normalizedName = normalizeProvinceName(provinceName)
            const provinceData = provinceMap.get(normalizedName)
            return {
              name: provinceName,
              adcode: feature.properties.adcode as string,
              level: feature.properties.level as string,
              province: provinceName,
              bachelor: provinceData?.bachelor || 0,
              master: provinceData?.master || 0,
              doctoral: provinceData?.doctoral || 0,
              total: provinceData?.total || 0,
              value: provinceData?.total || Math.round(Math.random() * 1000),
              selected: false
            }
          })
        } else {
          mapData = prepareMapData(chinaMapJson)
        }
        const option = createChartOption(mapData)
        chartInstance.value.setOption(option)
      }
    },
    { deep: true }
  )
</script>
