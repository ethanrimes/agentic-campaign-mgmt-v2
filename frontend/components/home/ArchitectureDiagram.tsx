// frontend/components/home/ArchitectureDiagram.tsx

'use client'

import { useState, useCallback, useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  Position,
  Handle,
  MarkerType,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
} from '@xyflow/react'
import dagre from '@dagrejs/dagre'
import '@xyflow/react/dist/style.css'

// Node descriptions for modal
const nodeDescriptions: Record<string, { title: string; description: string; details: string[] }> = {
  'perplexity': {
    title: 'Perplexity Sonar Search',
    description: 'Advanced AI-powered search engine that discovers trending topics and breaking news across the internet.',
    details: [
      'Real-time web search with AI summarization',
      'Identifies emerging trends and viral content',
      'Provides source citations and context',
      'Feeds deduplicated events to the knowledge base'
    ]
  },
  'chatgpt': {
    title: 'ChatGPT o4-mini Deep Research',
    description: 'Leverages OpenAI\'s latest model for comprehensive research and analysis of complex topics.',
    details: [
      'Deep dive analysis on specific subjects',
      'Multi-step reasoning and research',
      'Contextual understanding and synthesis',
      'Generates comprehensive research reports'
    ]
  },
  'trend-researcher': {
    title: 'Social Media Trend Researcher',
    description: 'Analyzes social media data from multiple platforms to identify trending topics and content patterns.',
    details: [
      'Aggregates data from Instagram and Facebook',
      'Identifies viral content and trending hashtags',
      'Analyzes engagement patterns and metrics',
      'Updates knowledge base with current trends'
    ]
  },
  'creative-ideator': {
    title: 'Creative Ideation',
    description: 'Generates original, creative content ideas that aren\'t necessarily grounded in recent news or events.',
    details: [
      'Brainstorms unique content concepts',
      'Creates thematic content series',
      'Develops creative storytelling angles',
      'Explores conceptual and artistic directions'
    ]
  },
  'event-deduplicator': {
    title: 'Event Deduplicator',
    description: 'Intelligently processes incoming events from multiple sources to eliminate duplicates and consolidate information.',
    details: [
      'Identifies duplicate events across sources',
      'Merges related information',
      'Maintains source attribution',
      'Ensures data quality and consistency'
    ]
  },
  'instagram-api': {
    title: 'Instagram Data API',
    description: 'Meta\'s official API for accessing Instagram business account data and metrics.',
    details: [
      'Retrieves posts and engagement metrics',
      'Accesses audience insights',
      'Monitors content performance',
      'Provides trend data for analysis'
    ]
  },
  'facebook-api': {
    title: 'Facebook Data API',
    description: 'Meta\'s Graph API for accessing Facebook page data and analytics.',
    details: [
      'Fetches page posts and interactions',
      'Retrieves audience demographics',
      'Monitors engagement metrics',
      'Provides performance analytics'
    ]
  },
  'knowledge-base': {
    title: 'Living Knowledge Base',
    description: 'Central repository that stores and organizes all content seeds, trends, insights, and campaign data. This is the heart of the system.',
    details: [
      'Stores content ideas and trends',
      'Maintains campaign history',
      'Tracks performance insights',
      'Provides context for content generation',
      'Continuously updated with new information'
    ]
  },
  'insights-agent': {
    title: 'Insights Agent',
    description: 'Analyzes campaign performance data to generate actionable insights and recommendations.',
    details: [
      'Processes campaign metrics',
      'Identifies successful content patterns',
      'Generates performance reports',
      'Provides optimization recommendations',
      'Feeds insights back to knowledge base'
    ]
  },
  'planner-agent': {
    title: 'Planner Agent',
    description: 'Strategic planning agent that allocates content across time periods and platforms based on trends and insights.',
    details: [
      'Creates content calendars',
      'Allocates posts to optimal time slots',
      'Balances content types and themes',
      'Considers platform-specific strategies',
      'Validates plans through guardrails'
    ]
  },
  'content-creator': {
    title: 'Content Creator',
    description: 'AI-powered content generation engine that creates posts, captions, and media based on content seeds.',
    details: [
      'Generates post copy and captions',
      'Creates platform-optimized content',
      'Incorporates trending topics',
      'Maintains brand voice consistency',
      'Schedules content for publication'
    ]
  },
  'guardrails': {
    title: 'Guardrails',
    description: 'Safety and validation system that ensures content meets quality standards and budget constraints.',
    details: [
      'Validates content appropriateness',
      'Checks media generation budgets',
      'Ensures post frequency limits',
      'Verifies platform requirements',
      'Prevents policy violations'
    ]
  },
  'meta-graph-api': {
    title: 'Meta Graph API',
    description: 'Meta\'s unified API for publishing content and retrieving analytics across Facebook and Instagram.',
    details: [
      'Publishes scheduled posts',
      'Retrieves campaign metrics',
      'Manages media uploads',
      'Provides real-time performance data',
      'Handles platform-specific features'
    ]
  },
}

// Category colors
const categoryColors = {
  Ideation: {
    bg: 'bg-blue-100',
    border: 'border-blue-500',
    text: 'text-blue-900',
    edgeColor: '#3b82f6',
  },
  Utilities: {
    bg: 'bg-slate-200',
    border: 'border-slate-600',
    text: 'text-slate-900',
    edgeColor: '#64748b',
  },
  'API Integrations': {
    bg: 'bg-green-100',
    border: 'border-green-600',
    text: 'text-green-900',
    edgeColor: '#16a34a',
  },
  Generation: {
    bg: 'bg-yellow-100',
    border: 'border-yellow-500',
    text: 'text-yellow-900',
    edgeColor: '#eab308',
  },
  Analysis: {
    bg: 'bg-orange-100',
    border: 'border-orange-500',
    text: 'text-orange-900',
    edgeColor: '#f97316',
  },
  'Knowledge Base': {
    bg: 'bg-gradient-to-br from-purple-100 to-pink-100',
    border: 'border-purple-500',
    text: 'text-purple-900',
    edgeColor: '#8b5cf6',
  },
}

// Modal component
function NodeModal({ 
  isOpen, 
  onClose, 
  nodeData 
}: { 
  isOpen: boolean
  onClose: () => void
  nodeData: { title: string; description: string; details: string[] } | null
}) {
  if (!isOpen || !nodeData) return null

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-2xl font-bold text-slate-900">{nodeData.title}</h2>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <p className="text-slate-700 mb-6 leading-relaxed">
            {nodeData.description}
          </p>
          
          <div>
            <h3 className="text-lg font-semibold text-slate-900 mb-3">Key Features</h3>
            <ul className="space-y-2">
              {nodeData.details.map((detail, index) => (
                <li key={index} className="flex items-start">
                  <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-slate-600">{detail}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

// Custom node component
function CustomNode({ data, id }: { data: any; id: string }) {
  const colors = categoryColors[data.category as keyof typeof categoryColors]

  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-xl border-2 ${colors.bg} ${colors.border} min-w-[180px] transition-all hover:shadow-xl cursor-pointer hover:scale-105`}
      onClick={() => data.onClick?.(id)}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555' }}
      />
      
      <div className={`text-sm font-bold ${colors.text} text-center`}>
        {data.label}
      </div>
      {data.subtitle && (
        <div className="text-xs text-slate-600 text-center mt-1 italic">
          {data.subtitle}
        </div>
      )}
      
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555' }}
      />
    </div>
  )
}

const nodeTypes = {
  custom: CustomNode,
}

// Initial nodes with rank for spatial grouping
const createInitialNodes = (onNodeClick: (id: string) => void): Node[] => [
  // Rank 0: Data Sources (APIs)
  {
    id: 'instagram-api',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Instagram data API', category: 'API Integrations', onClick: onNodeClick },
  },
  {
    id: 'facebook-api',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Facebook data API', category: 'API Integrations', onClick: onNodeClick },
  },
  
  // Rank 1: Research Tools
  {
    id: 'perplexity',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Perplexity Sonar Search', category: 'Ideation', onClick: onNodeClick },
  },
  {
    id: 'chatgpt',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'ChatGPT o4-mini Deep Research', category: 'Ideation', onClick: onNodeClick },
  },
  
  // Rank 2: Processors
  {
    id: 'trend-researcher',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Social Media Trend Researcher', category: 'Ideation', onClick: onNodeClick },
  },
  {
    id: 'creative-ideator',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Creative Ideation', category: 'Ideation', onClick: onNodeClick },
  },
  {
    id: 'event-deduplicator',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Event Deduplicator', category: 'Utilities', onClick: onNodeClick },
  },
  
  // Rank 3: Knowledge Base (Center)
  {
    id: 'knowledge-base',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: {
      label: 'Living Knowledge Base',
      subtitle: '(you are here)',
      category: 'Knowledge Base',
      onClick: onNodeClick
    },
  },
  
  // Rank 4: Generation & Analysis
  {
    id: 'planner-agent',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Planner Agent', category: 'Generation', onClick: onNodeClick },
  },
  {
    id: 'guardrails',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Guardrails', category: 'Utilities', onClick: onNodeClick },
  },
  
  // Rank 5: Content Creation
  {
    id: 'content-creator',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Content Creator', category: 'Generation', onClick: onNodeClick },
  },
  
  // Rank 6: Output & Analytics
  {
    id: 'meta-graph-api',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Meta Graph API', category: 'API Integrations', onClick: onNodeClick },
  },
  {
    id: 'insights-agent',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Insights Agent', category: 'Analysis', onClick: onNodeClick },
  },
]

// Standardized grey color for all edges
const EDGE_COLOR = '#64748b'
const EDGE_STYLE = { strokeWidth: 2.5, stroke: EDGE_COLOR }
const EDGE_MARKER = { type: MarkerType.ArrowClosed, color: EDGE_COLOR }
const EDGE_LABEL_STYLE = {
  labelStyle: { fontSize: 10, fill: '#1e293b', fontWeight: 600 },
  labelBgStyle: { fill: '#ffffff', fillOpacity: 0.95 },
  labelBgPadding: [6, 3] as [number, number],
  labelBgBorderRadius: 3,
}

const initialEdges: Edge[] = [
  // API Integrations → Trend Researcher
  {
    id: 'e-instagram-trend',
    source: 'instagram-api',
    target: 'trend-researcher',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
  },
  {
    id: 'e-facebook-trend',
    source: 'facebook-api',
    target: 'trend-researcher',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
  },
  
  // Research Tools → Event Deduplicator
  {
    id: 'e-perplexity-dedup',
    source: 'perplexity',
    target: 'event-deduplicator',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
  },
  {
    id: 'e-chatgpt-dedup',
    source: 'chatgpt',
    target: 'event-deduplicator',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
  },
  
  // Processors → Knowledge Base
  {
    id: 'e-trend-kb',
    source: 'trend-researcher',
    target: 'knowledge-base',
    label: 'Current Social Media Trends',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
  {
    id: 'e-creative-kb',
    source: 'creative-ideator',
    target: 'knowledge-base',
    label: 'Conceptual ideas not "grounded" in science',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
  {
    id: 'e-dedup-kb',
    source: 'event-deduplicator',
    target: 'knowledge-base',
    label: 'New relevant news events',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
  
  // Knowledge Base ↔ Planner Agent
  {
    id: 'e-kb-planner',
    source: 'knowledge-base',
    target: 'planner-agent',
    label: 'Content seeds',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
  {
    id: 'e-planner-kb',
    source: 'planner-agent',
    target: 'knowledge-base',
    label: 'Period post allocation',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
  
  // Planner ↔ Guardrails
  {
    id: 'e-planner-guardrails',
    source: 'planner-agent',
    target: 'guardrails',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
  },
  {
    id: 'e-guardrails-planner',
    source: 'guardrails',
    target: 'planner-agent',
    label: 'Media generation & post budget validation',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
  
  // Knowledge Base → Content Creator
  {
    id: 'e-kb-creator',
    source: 'knowledge-base',
    target: 'content-creator',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
  },
  
  // Content Creator → Meta Graph API
  {
    id: 'e-creator-meta',
    source: 'content-creator',
    target: 'meta-graph-api',
    label: 'Scheduled posts',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
  
  // Meta Graph API → Insights Agent
  {
    id: 'e-meta-insights',
    source: 'meta-graph-api',
    target: 'insights-agent',
    label: 'Current campaign metrics',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
  
  // Insights Agent → Knowledge Base
  {
    id: 'e-insights-kb',
    source: 'insights-agent',
    target: 'knowledge-base',
    label: 'In-depth insights reports',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },
]

// Layout with spatial grouping and reduced edge overlapping
const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  dagreGraph.setGraph({
    rankdir: 'TB',
    ranksep: 120,      // Increased vertical spacing between ranks
    nodesep: 150,      // Increased horizontal spacing between nodes
    edgesep: 60,       // Increased edge separation
    marginx: 60,
    marginy: 60,
  })

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 220, height: 80 })
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 110,
        y: nodeWithPosition.y - 40,
      },
    }
  })

  return { nodes: layoutedNodes, edges }
}

export default function ArchitectureDiagram() {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleNodeClick = useCallback((nodeId: string) => {
    setSelectedNode(nodeId)
    setIsModalOpen(true)
  }, [])

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false)
    setSelectedNode(null)
  }, [])

  const initialNodesWithHandlers = useMemo(
    () => createInitialNodes(handleNodeClick),
    [handleNodeClick]
  )

  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(
    () => getLayoutedElements(initialNodesWithHandlers, initialEdges),
    [initialNodesWithHandlers]
  )

  const [nodes, setNodes] = useState<Node[]>(layoutedNodes)
  const [edges, setEdges] = useState<Edge[]>(layoutedEdges)

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  )

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  )

  const selectedNodeData = selectedNode ? nodeDescriptions[selectedNode] : null

  return (
    <>
      <div className="relative w-full bg-white rounded-2xl shadow-xl p-6 border border-slate-200">
        <h3 className="text-2xl font-bold text-slate-900 mb-4 text-center">System Architecture</h3>

        {/* Legend */}
        <div className="flex flex-wrap gap-3 mb-4 justify-center">
          {Object.entries(categoryColors).map(([category, colors]) => (
            <div key={category} className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded border-2 ${colors.bg} ${colors.border}`}></div>
              <span className="text-xs text-slate-600">{category}</span>
            </div>
          ))}
        </div>

        {/* Instruction */}
        <p className="text-center text-sm text-slate-500 mb-4">
          Click on any node to learn more about it
        </p>

        {/* ReactFlow Diagram */}
        <div className="w-full h-[900px] border-2 border-slate-200 rounded-xl overflow-hidden bg-gradient-to-br from-slate-50 to-white">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.15 }}
            attributionPosition="bottom-left"
            proOptions={{ hideAttribution: true }}
            minZoom={0.4}
            maxZoom={1.5}
            defaultEdgeOptions={{
              style: {
                strokeWidth: 2.5,
                stroke: '#64748b',
              },
            }}
            edgesReconnectable={false}
            nodesDraggable={true}
            nodesConnectable={false}
            elementsSelectable={true}
          >
            <Background color="#cbd5e1" gap={16} size={1} />
            <Controls />
          </ReactFlow>
        </div>
      </div>

      <NodeModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        nodeData={selectedNodeData}
      />
    </>
  )
}