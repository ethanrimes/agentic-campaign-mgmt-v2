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
  perplexity: {
    title: 'Perplexity Sonar (News Research Ingestion)',
    description:
      'Runs structured, high-depth internet scans to discover emerging news events and produce machine-parseable event objects that feed the News Event Seed pipeline.',
    details: [
      'Executes wide-coverage internet discovery with rich source citations',
      'Captures breaking events, ongoing narratives, and emerging topics',
      'Outputs structured event objects ready for downstream ingestion',
      'Forms one half of the news ingestion pipeline',
    ],
  },
  chatgpt: {
    title: 'ChatGPT o4-mini Deep Research',
    description:
      'Performs multi-step deep research on targeted topics using OpenAI’s Deep Research capabilities, generating high-context reports that are parsed into structured news events.',
    details: [
      'Conducts multi-hop reasoning over complex, multi-source topics',
      'Produces rich explanatory research with supporting sources',
      'Parsed by a secondary model into standardized event objects',
      'Completes the second half of the news ingestion pipeline',
    ],
  },
  'trend-researcher': {
    title: 'Trend Research Agent',
    description:
      'Synthesizes real-time social media data using Instagram and Facebook scraping tools to produce Trend Seeds representing high-performing formats, hashtags, and behaviors.',
    details: [
      'Integrates multiple high-volume social scraper utilities',
      'Identifies trending hashtags, viral formats, and content patterns',
      'Surfaces influential users and content archetypes',
      'Writes structured Trend Seeds into the Living Knowledge Base',
    ],
  },
  'creative-ideator': {
    title: 'Ungrounded Creative Seed Generator',
    description:
      'A creativity-focused agent that generates unbounded content concepts not tied to news or social signals, expanding the system’s creative search space.',
    details: [
      'Produces open-ended content ideas with explicit formats (image, video, reel, carousel, text, etc.)',
      'Leverages the knowledge base and insight reports as optional context',
      'Explores highly diverse and experimental content directions',
      'Prevents overfitting to short-lived trends by injecting novel ideas',
    ],
  },
  'event-deduplicator': {
    title: 'Event Deduplication & Consolidation',
    description:
      'Compares newly ingested events from Perplexity and ChatGPT with existing News Event Seeds to detect duplicates, merge sources, and maintain canonical records.',
    details: [
      'Uses LLM-based semantic comparison to detect overlapping events',
      'Merges descriptions and consolidates source lists for the same event',
      'Maintains a clean, canonical set of News Event Seeds',
      'Reduces noise and prevents knowledge base fragmentation',
    ],
  },
  'instagram-api': {
    title: 'Instagram Metrics & Data Tools',
    description:
      'Provides structured access to Instagram account data and engagement metrics, primarily used by the Insights Agent to compute performance and audience understanding.',
    details: [
      'Retrieves post-level metrics such as likes, comments, shares, and reach',
      'Exposes audience insights and behavior over time',
      'Supports reels, carousels, and feed post analysis',
      'Supplies raw data into the closed-loop learning pipeline',
    ],
  },
  'facebook-api': {
    title: 'Facebook Metrics & Data Tools',
    description:
      'Supplies Facebook page and post analytics, enabling the Insights Agent to analyze performance across another major distribution channel.',
    details: [
      'Fetches engagement metrics such as reactions, comments, and shares',
      'Retrieves page-level analytics and audience trends',
      'Supports video and feed post performance tracking',
      'Complements Instagram data for cross-platform insight generation',
    ],
  },
  'knowledge-base': {
    title: 'Living Knowledge Base',
    description:
      'Central, continuously updated repository for all content seeds, insight reports, content tasks, completed posts, and their relationships. This is the system’s memory and inspection surface.',
    details: [
      'Stores News, Trend, and Ungrounded Seeds in a unified schema',
      'Tracks the full lifecycle from idea → plan → post → performance',
      'Continuously updated by ingestion, planning, creation, and insights agents',
      'Backed by a Next.js UI for full human-in-the-loop visibility',
      'Provides rich context to every agent via shared tools and APIs',
    ],
  },
  'insights-agent': {
    title: 'Insights Agent',
    description:
      'Analyzes cross-platform engagement metrics to generate timestamped insight reports that directly inform future planning and ideation.',
    details: [
      'Calls Facebook and Instagram metric tools to gather performance data',
      'Identifies patterns in what worked, what failed, and why',
      'Summarizes audience behavior, content archetype performance, and timing effects',
      'Writes structured insight reports back into the knowledge base',
      'Closes the feedback loop for continuous strategic refinement',
    ],
  },
  'planner-agent': {
    title: 'Planner Agent',
    description:
      'Transforms content seeds and insights into a weekly content plan, allocating posts and media types while respecting global guardrails.',
    details: [
      'Selects which seeds to activate in the upcoming period',
      'Allocates counts for posts, images, and videos per seed and platform',
      'Balances news-driven, trend-driven, and ungrounded creative content',
      'Produces structured Content Creation Tasks for downstream agents',
      'Runs under strict min/max constraints enforced by guardrails',
    ],
  },
  'content-creator': {
    title: 'Content Creation Agent',
    description:
      'Executes the approved content plan by generating all required media and copy, pulling contextual grounding directly from the Living Knowledge Base.',
    details: [
      'Consumes Content Creation Tasks created by the planner',
      'Generates images and videos via connected media generation services',
      'Writes captions and post text that reference the appropriate seed and sources',
      'Stores generated media in Supabase and records Completed Post objects',
      'Prepares platform-ready assets for automated publishing',
    ],
  },
  guardrails: {
    title: 'Guardrail Validation System',
    description:
      'Validates planner outputs against global constraints and budgets, ensuring the system stays within strategic and operational limits.',
    details: [
      'Enforces min/max posts per week',
      'Enforces min/max content seeds per week',
      'Enforces image and video generation budgets',
      'Rejects invalid plans and triggers planner retries when needed',
      'Helps maintain predictable cost and content cadence',
    ],
  },
  'meta-graph-api': {
    title: 'Meta Graph API (Publishing Layer)',
    description:
      'Responsible for publishing completed content to Facebook and Instagram and returning early-stage performance data.',
    details: [
      'Uploads media and publishes posts to Facebook and Instagram',
      'Supports reels, videos, carousels, and standard feed posts',
      'Returns initial performance metrics post-publish',
      'Connects the Content Creation Agent to real-world distribution',
      'Feeds data back into the Insights Agent to close the loop',
    ],
  },
  'facebook-webhook': {
    title: 'Facebook Webhook',
    description:
      'Real-time monitoring system that captures comment activity on Facebook posts as soon as they occur, enabling immediate response capabilities.',
    details: [
      'Receives real-time notifications when comments are posted on Facebook',
      'Logs all comment activity with full context and metadata',
      'Forwards comment data to the Living Knowledge Base for processing',
      'Enables rapid response times for audience engagement',
      'Implementation: @fb-webhook/index.js',
    ],
  },
  'instagram-comment-checker': {
    title: 'Instagram Comment Checker',
    description:
      'Periodic polling service that monitors Instagram posts for new comments, capturing engagement activity that is then logged and processed.',
    details: [
      'Polls Instagram posts at regular intervals to detect new comments',
      'Extracts comment content, author information, and timestamps',
      'Logs discovered comments into the Living Knowledge Base',
      'Complements Facebook webhook with Instagram engagement tracking',
      'Implementation: @backend/services/meta/instagram_comment_checker.py',
    ],
  },
  'comment-responder': {
    title: 'Comment Responder Agent',
    description:
      'AI-powered agent that generates contextually relevant, thoughtful responses to user comments on both Facebook and Instagram.',
    details: [
      'Analyzes incoming comments alongside post content and metadata',
      'Reviews full thread history to maintain conversational context',
      'Generates natural, on-brand responses tailored to each comment',
      'Supports engagement across both Facebook and Instagram platforms',
      'Implementation: @backend/agents/comment_responder/',
    ],
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
  
  // Rank 2: Processors & Comment Monitoring
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
  {
    id: 'facebook-webhook',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Facebook Webhook', category: 'Utilities', onClick: onNodeClick },
  },
  {
    id: 'instagram-comment-checker',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Instagram Comment Checker', category: 'Utilities', onClick: onNodeClick },
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
  
  // Rank 5: Content Creation & Comment Response
  {
    id: 'content-creator',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Content Creator', category: 'Generation', onClick: onNodeClick },
  },
  {
    id: 'comment-responder',
    type: 'custom',
    position: { x: 0, y: 0 },
    data: { label: 'Comment Responder', category: 'Generation', onClick: onNodeClick },
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

  // Facebook Webhook → Knowledge Base
  {
    id: 'e-fb-webhook-kb',
    source: 'facebook-webhook',
    target: 'knowledge-base',
    label: 'Facebook comment activity',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },

  // Instagram Comment Checker → Knowledge Base
  {
    id: 'e-ig-checker-kb',
    source: 'instagram-comment-checker',
    target: 'knowledge-base',
    label: 'Instagram comment activity',
    type: 'smoothstep',
    style: EDGE_STYLE,
    markerEnd: EDGE_MARKER,
    ...EDGE_LABEL_STYLE,
  },

  // Knowledge Base → Comment Responder
  {
    id: 'e-kb-comment-responder',
    source: 'knowledge-base',
    target: 'comment-responder',
    label: 'Comment context & thread history',
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