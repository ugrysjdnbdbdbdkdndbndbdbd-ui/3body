<script setup lang="ts">
// @ts-nocheck
/**
 * 人物关系星图 (Constellation Network)
 * 以「星图/星座」形式展示人物关系网络：节点为人物，边为关系，力导向布局 + 悬停高亮路径
 */
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'
import type { Figure } from '@/types/figures'
import type { FigureRelationship } from '@/types/figures'

const props = defineProps<{ figures: Figure[] }>()
const emit = defineEmits<{ select: [figure: Figure | null] }>()

const containerRef = ref<HTMLElement | null>(null)
const hoveredNodeId = ref<string | null>(null)

function parseJson<T>(str: string | null | undefined): T | null {
  if (!str) return null
  try {
    return JSON.parse(str) as T
  } catch {
    return null
  }
}

function getRelationships(f: Figure): FigureRelationship[] {
  const raw = f.relationships
  if (!raw) return []
  if (typeof raw === 'string') {
    const parsed = parseJson<FigureRelationship[]>(raw)
    return Array.isArray(parsed) ? parsed : []
  }
  return Array.isArray(raw) ? (raw as FigureRelationship[]) : []
}

// 从 figures 构建图数据：节点（人物 + 仅出现在 target 中的名字）、边（关系）
const graphData = computed(() => {
  const nameToFigure = new Map<string, Figure>()
  for (const f of props.figures) nameToFigure.set(f.name, f)

  const nodeIds = new Set<string>(nameToFigure.keys())
  const links: { source: string; target: string; relation_type: string }[] = []

  for (const f of props.figures) {
    for (const r of getRelationships(f)) {
      nodeIds.add(r.target)
      links.push({
        source: f.name,
        target: r.target,
        relation_type: r.relation_type || '',
      })
    }
  }

  const nodes = Array.from(nodeIds).map((id) => ({
    id: id,
    name: id,
    figure: nameToFigure.get(id) ?? null,
    isExternal: !nameToFigure.has(id),
  }))

  return { nodes, links }
})

// 力导向仿真与 SVG 渲染
let simulation: ReturnType<typeof d3.forceSimulation<GraphNode>> | null = null
let zoomBehavior: ReturnType<typeof d3.zoom<SVGSVGElement, unknown>> | null = null

interface GraphNode {
  id: string
  name: string
  figure: Figure | null
  isExternal: boolean
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
}

interface GraphLink {
  source: string | GraphNode
  target: string | GraphNode
  relation_type: string
}

function runSimulation() {
  const el = containerRef.value
  if (!el || props.figures.length === 0) return

  const { width, height } = el.getBoundingClientRect()
  const { nodes, links } = graphData.value

  // 深拷贝供 d3 修改坐标
  const nodesCopy: GraphNode[] = nodes.map((n) => ({
    ...n,
    x: width / 2 + (Math.random() - 0.5) * 200,
    y: height / 2 + (Math.random() - 0.5) * 200,
  }))

  const linksCopy: GraphLink[] = links.map((l) => ({
    ...l,
    source: l.source,
    target: l.target,
  }))

  simulation = d3
    .forceSimulation<GraphNode>(nodesCopy)
    .force(
      'link',
      d3
        .forceLink<GraphNode, GraphLink>(linksCopy)
        .id((d) => (d as GraphNode).id)
        .distance(120)
    )
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide<GraphNode>().radius(36))

  const svgEl = d3
    .select(el)
    .append('svg')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('viewBox', [0, 0, width, height])

  // 星图背景：网格 + 光晕
  const defs = svgEl.append('defs')
  defs
    .append('filter')
    .attr('id', 'glow')
    .append('feGaussianBlur')
    .attr('stdDeviation', 3)
    .attr('result', 'coloredBlur')
  const feMerge = defs.append('feMerge')
  feMerge.append('feMergeNode').attr('in', 'coloredBlur')
  feMerge.append('feMergeNode').attr('in', 'SourceGraphic')

  const g = svgEl.append('g')

  // 背景网格（极淡）
  const gridSize = 40
  for (let x = 0; x <= width; x += gridSize) {
    g.append('line')
      .attr('x1', x)
      .attr('y1', 0)
      .attr('x2', x)
      .attr('y2', height)
      .attr('stroke', 'rgba(0,255,255,0.04)')
      .attr('stroke-width', 1)
  }
  for (let y = 0; y <= height; y += gridSize) {
    g.append('line')
      .attr('x1', 0)
      .attr('y1', y)
      .attr('x2', width)
      .attr('y2', y)
      .attr('stroke', 'rgba(0,255,255,0.04)')
      .attr('stroke-width', 1)
  }

  // 缩放与拖拽
  zoomBehavior = d3
    .zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.2, 4])
    .on('zoom', (ev: { transform: unknown }) => g.attr('transform', ev.transform))
  svgEl.call(zoomBehavior)

  // 边
  const link = g
    .append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(linksCopy)
    .join('line')
    .attr('stroke', 'rgba(0,255,255,0.15)')
    .attr('stroke-width', 1.5)
    .attr('stroke-dasharray', '2 4')
    .attr('stroke-linecap', 'round')

  // 边上的关系类型标签（小字，可选显示）
  const linkLabel = g
    .append('g')
    .attr('class', 'link-labels')
    .selectAll('text')
    .data(linksCopy)
    .join('text')
    .attr('font-size', 9)
    .attr('fill', 'rgba(0,255,255,0.35)')
    .attr('text-anchor', 'middle')
    .attr('pointer-events', 'none')
    .text((d: GraphLink) => d.relation_type)

  // 节点组
  const node = g
    .append('g')
    .attr('class', 'nodes')
    .selectAll('g')
    .data(nodesCopy)
    .join('g')
    .attr('cursor', 'pointer')
    .call(
      d3
        .drag<SVGGElement, GraphNode>()
        .on('start', (ev: { active: number; subject: GraphNode }) => {
          if (!ev.active) simulation?.alphaTarget(0.3).restart()
          ev.subject.fx = ev.subject.x
          ev.subject.fy = ev.subject.y
        })
        .on('drag', (ev: { subject: GraphNode; x: number; y: number }) => {
          ev.subject.fx = ev.x
          ev.subject.fy = ev.y
        })
        .on('end', (ev: { active: number; subject: GraphNode }) => {
          if (!ev.active) simulation?.alphaTarget(0)
          ev.subject.fx = null
          ev.subject.fy = null
        })
    )

  // 外圈光晕（仅在有档案的人物上更亮）
  node
    .append('circle')
    .attr('r', (d: GraphNode) => (d.figure ? 24 : 18))
    .attr('fill', 'none')
    .attr('stroke', (d: GraphNode) =>
      d.figure ? 'rgba(0,255,255,0.4)' : 'rgba(255,180,0,0.25)'
    )
    .attr('stroke-width', 2)
    .attr('filter', 'url(#glow)')
    .attr('class', 'node-glow')

  // 节点圆点
  node
    .append('circle')
    .attr('r', (d: GraphNode) => (d.figure ? 20 : 14))
    .attr('fill', (d: GraphNode) =>
      d.figure ? 'rgba(0,40,50,0.9)' : 'rgba(40,30,0,0.8)'
    )
    .attr('stroke', (d: GraphNode) =>
      d.figure ? '#00ffff' : 'rgba(255,180,0,0.6)'
    )
    .attr('stroke-width', 1.5)
    .attr('class', 'node-dot')

  // 节点名称
  node
    .append('text')
    .attr('dy', (d: GraphNode) => (d.figure ? 32 : 26))
    .attr('text-anchor', 'middle')
    .attr('fill', (d: GraphNode) =>
      d.figure ? 'rgba(0,255,255,0.9)' : 'rgba(255,180,0,0.7)'
    )
    .attr('font-size', (d: GraphNode) => (d.figure ? 11 : 9))
    .attr('font-family', 'monospace')
    .attr('pointer-events', 'none')
    .text((d: GraphNode) => d.name)

  node.on('click', (_: unknown, d: GraphNode) => {
    emit('select', d.figure ?? null)
  })

  node.on('mouseenter', function (ev: MouseEvent, d: GraphNode) {
    hoveredNodeId.value = d.id
    const gEl = ev.currentTarget as SVGGElement
    d3.select(gEl).select('.node-glow').attr('stroke', 'rgba(0,255,255,0.9)')
    d3.select(gEl).select('.node-dot').attr('stroke-width', 2.5)
    link.attr('stroke', (l: unknown) => {
      const edge = l as GraphLink
      const s = (edge.source as GraphNode)?.id ?? edge.source
      const t = (edge.target as GraphNode)?.id ?? edge.target
      return s === d.id || t === d.id
        ? 'rgba(0,255,255,0.7)'
        : 'rgba(0,255,255,0.06)'
    })
    link.attr('stroke-width', (l: unknown) => {
      const edge = l as GraphLink
      const s = (edge.source as GraphNode)?.id ?? edge.source
      const t = (edge.target as GraphNode)?.id ?? edge.target
      return s === d.id || t === d.id ? 2.5 : 1.5
    })
  })

  node.on('mouseleave', function (ev: MouseEvent) {
    hoveredNodeId.value = null
    const gEl = ev.currentTarget as SVGGElement
    d3.select(gEl).select('.node-glow').attr('stroke', (d: GraphNode) =>
      d.figure ? 'rgba(0,255,255,0.4)' : 'rgba(255,180,0,0.25)'
    )
    d3.select(gEl).select('.node-dot').attr('stroke-width', 1.5)
    link.attr('stroke', 'rgba(0,255,255,0.15)').attr('stroke-width', 1.5)
  })

  simulation.on('tick', () => {
    link
      .attr('x1', (d: GraphLink) => (d.source as GraphNode).x ?? 0)
      .attr('y1', (d: GraphLink) => (d.source as GraphNode).y ?? 0)
      .attr('x2', (d: GraphLink) => (d.target as GraphNode).x ?? 0)
      .attr('y2', (d: GraphLink) => (d.target as GraphNode).y ?? 0)

    linkLabel
      .attr('x', (d: GraphLink) => {
        const s = d.source as GraphNode
        const t = d.target as GraphNode
        return ((s.x ?? 0) + (t.x ?? 0)) / 2
      })
      .attr('y', (d: GraphLink) => {
        const s = d.source as GraphNode
        const t = d.target as GraphNode
        return ((s.y ?? 0) + (t.y ?? 0)) / 2
      })

    node.attr('transform', (d: GraphNode) => `translate(${d.x ?? 0},${d.y ?? 0})`)
  })
}

function destroyGraph() {
  if (simulation) {
    simulation.stop()
    simulation = null
  }
  if (containerRef.value) {
    d3.select(containerRef.value).selectAll('svg').remove()
  }
  zoomBehavior = null
}

watch(
  () => props.figures.length,
  () => {
    destroyGraph()
    runSimulation()
  }
)

onMounted(() => {
  runSimulation()
})

onUnmounted(() => {
  destroyGraph()
})
</script>

<template>
  <div class="figures-network-graph">
    <div class="graph-legend">
      <span class="legend-item primary">
        <span class="dot"></span>
        档案人物
      </span>
      <span class="legend-item external">
        <span class="dot external"></span>
        关系对象
      </span>
      <span class="legend-hint">拖拽节点移动 · 滚轮缩放 · 点击节点查看档案</span>
    </div>
    <div ref="containerRef" class="graph-container"></div>
  </div>
</template>

<style scoped>
.figures-network-graph {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 520px;
  background: radial-gradient(
    ellipse 120% 100% at 50% 50%,
    rgba(0, 20, 30, 0.6) 0%,
    rgba(0, 5, 10, 0.95) 100%
  );
  border: 1px solid rgba(0, 255, 255, 0.12);
  border-radius: 6px;
  overflow: hidden;
}

.graph-legend {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-family: monospace;
  font-size: 0.7rem;
  color: rgba(0, 255, 255, 0.7);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(0, 40, 50, 0.9);
  border: 1.5px solid #00ffff;
  box-shadow: 0 0 8px rgba(0, 255, 255, 0.5);
}

.legend-item .dot.external {
  background: rgba(40, 30, 0, 0.8);
  border-color: rgba(255, 180, 0, 0.6);
  box-shadow: 0 0 6px rgba(255, 180, 0, 0.3);
}

.legend-hint {
  margin-left: 0.5rem;
  color: rgba(255, 255, 255, 0.35);
  font-size: 0.65rem;
}

.graph-container {
  width: 100%;
  height: 100%;
  min-height: 480px;
}
</style>
