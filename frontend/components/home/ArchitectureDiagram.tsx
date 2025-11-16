// frontend/components/home/ArchitectureDiagram.tsx

'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Database, TrendingUp, Lightbulb, BarChart3, Calendar, Sparkles, Shield, Zap } from 'lucide-react'

interface NodeProps {
  id: string
  title: string
  description: string
  details: string
  color: string
  position: { x: number; y: number }
  icon: React.ElementType
  onClick: () => void
}

const Node = ({ title, description, color, position, icon: Icon, onClick }: NodeProps) => {
  return (
    <motion.div
      className={`absolute cursor-pointer group`}
      style={{ left: position.x, top: position.y }}
      whileHover={{ scale: 1.05 }}
      transition={{ duration: 0.2 }}
      onClick={onClick}
    >
      <div className={`relative px-6 py-4 rounded-xl ${color} shadow-lg border-2 border-white/20 backdrop-blur-sm hover:shadow-xl transition-all duration-300`}>
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5 text-white" />
          <div>
            <div className="font-bold text-white text-sm">{title}</div>
            <div className="text-xs text-white/80 mt-1 max-w-[200px]">{description}</div>
          </div>
        </div>
        <div className="absolute inset-0 rounded-xl bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      </div>
    </motion.div>
  )
}

const ConnectionLine = ({ from, to, animated = false }: { from: { x: number; y: number }, to: { x: number; y: number }, animated?: boolean }) => {
  return (
    <svg className="absolute inset-0 pointer-events-none" style={{ width: '100%', height: '100%' }}>
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon points="0 0, 10 3, 0 6" fill="#64748b" />
        </marker>
      </defs>
      <motion.line
        x1={from.x}
        y1={from.y}
        x2={to.x}
        y2={to.y}
        stroke="#64748b"
        strokeWidth="2"
        strokeDasharray={animated ? "5,5" : "0"}
        markerEnd="url(#arrowhead)"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1, ease: "easeInOut" }}
      />
    </svg>
  )
}

export default function ArchitectureDiagram() {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const nodes = {
    // Ideation & Information Ingestion (Left)
    perplexity: {
      id: 'perplexity',
      title: 'Perplexity Search',
      description: 'Deep research agent',
      details: 'Uses Perplexity AI to conduct deep research on relevant topics, news events, and trending subjects to identify content opportunities.',
      color: 'bg-blue-600',
      position: { x: 50, y: 100 },
      icon: Database,
    },
    chatgpt: {
      id: 'chatgpt',
      title: 'ChatGPT Research',
      description: 'Additional context',
      details: 'Provides supplementary research and contextual understanding to enrich content seeds with diverse perspectives.',
      color: 'bg-blue-500',
      position: { x: 50, y: 200 },
      icon: Sparkles,
    },
    trendResearcher: {
      id: 'trendResearcher',
      title: 'Trend Researcher',
      description: 'Social media trends',
      details: 'Monitors and analyzes current social media trends across platforms to identify viral content patterns and emerging topics.',
      color: 'bg-purple-600',
      position: { x: 50, y: 300 },
      icon: TrendingUp,
    },
    instagram: {
      id: 'instagram',
      title: 'Instagram API',
      description: 'Platform data',
      details: 'Retrieves Instagram-specific trends, hashtags, and engagement metrics to inform content strategy.',
      color: 'bg-pink-600',
      position: { x: 50, y: 400 },
      icon: Zap,
    },
    facebook: {
      id: 'facebook',
      title: 'Facebook API',
      description: 'Platform data',
      details: 'Gathers Facebook trends, audience insights, and engagement data to optimize content performance.',
      color: 'bg-blue-700',
      position: { x: 50, y: 500 },
      icon: Zap,
    },
    creative: {
      id: 'creative',
      title: 'Creative Ideation',
      description: 'Ungrounded ideas',
      details: 'Generates original creative content ideas not tied to specific news events or trends, driven by pure creative thinking.',
      color: 'bg-amber-600',
      position: { x: 50, y: 600 },
      icon: Lightbulb,
    },

    // Central Knowledge Base
    knowledgeBase: {
      id: 'knowledgeBase',
      title: 'Living Knowledge Base',
      description: 'Central repository',
      details: 'A centralized, interactive information repository that stores all content seeds, posts, insights, and campaign data. Enables human-in-the-loop oversight and deep understanding of agent logic.',
      color: 'bg-gradient-to-br from-purple-600 to-pink-600',
      position: { x: 450, y: 300 },
      icon: Database,
    },

    // Analysis & Analytics (Top)
    insights: {
      id: 'insights',
      title: 'Insights Agent',
      description: 'Performance analysis',
      details: 'The learning element of the system. Analyzes campaign performance, synthesizes detailed reports, and informs future decision-making with data-driven insights.',
      color: 'bg-green-600',
      position: { x: 500, y: 50 },
      icon: BarChart3,
    },

    // Planning & Generation (Right)
    planner: {
      id: 'planner',
      title: 'Planner Agent',
      description: 'Content strategy',
      details: 'Selects content seeds for the current period, determines post allocation, and plans media generation while validating against guardrails to ensure budget compliance.',
      color: 'bg-yellow-500',
      position: { x: 850, y: 300 },
      icon: Calendar,
    },
    guardrails: {
      id: 'guardrails',
      title: 'Guardrails',
      description: 'Validation layer',
      details: 'Ensures that all content plans comply with budget constraints, posting frequency limits, and brand guidelines before execution.',
      color: 'bg-slate-600',
      position: { x: 850, y: 200 },
      icon: Shield,
    },
    contentCreator: {
      id: 'contentCreator',
      title: 'Content Creator',
      description: 'Media generation',
      details: 'Brings together diverse tools to create original content including images, videos, and copy as directed by the planner agent.',
      color: 'bg-orange-600',
      position: { x: 850, y: 500 },
      icon: Sparkles,
    },
    metaGraph: {
      id: 'metaGraph',
      title: 'Meta Graph API',
      description: 'Publishing platform',
      details: 'Handles the automated publishing of created content to Facebook and Instagram according to the scheduled plan.',
      color: 'bg-blue-800',
      position: { x: 1100, y: 300 },
      icon: Zap,
    },
  }

  const connections = [
    // Research to KB
    { from: { x: 250, y: 120 }, to: { x: 450, y: 280 } },
    { from: { x: 250, y: 220 }, to: { x: 450, y: 290 } },
    { from: { x: 250, y: 320 }, to: { x: 450, y: 310 } },
    { from: { x: 250, y: 420 }, to: { x: 450, y: 330 } },
    { from: { x: 250, y: 520 }, to: { x: 450, y: 350 } },
    { from: { x: 250, y: 620 }, to: { x: 450, y: 370 } },

    // KB to Insights
    { from: { x: 650, y: 280 }, to: { x: 580, y: 120 } },

    // Insights to Planner
    { from: { x: 700, y: 70 }, to: { x: 850, y: 280 } },

    // KB to Planner
    { from: { x: 650, y: 320 }, to: { x: 850, y: 320 } },

    // Planner to Guardrails
    { from: { x: 950, y: 280 }, to: { x: 950, y: 230 } },

    // Planner to Content Creator
    { from: { x: 950, y: 340 }, to: { x: 950, y: 480 } },

    // Content Creator to Meta Graph
    { from: { x: 1050, y: 520 }, to: { x: 1100, y: 350 } },
  ]

  const selectedNodeData = selectedNode ? nodes[selectedNode as keyof typeof nodes] : null

  return (
    <div className="relative w-full bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
      <h3 className="text-2xl font-bold text-slate-900 mb-6 text-center">System Architecture</h3>

      {/* Diagram Container */}
      <div className="relative w-full h-[700px] bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border-2 border-slate-200 overflow-hidden">
        {/* Section Labels */}
        <div className="absolute top-4 left-4 text-sm font-semibold text-slate-600">
          Ideation & Information<br/>Ingestion
        </div>
        <div className="absolute top-4 left-1/2 -translate-x-1/2 text-sm font-semibold text-slate-600">
          Analysis & Analytics
        </div>
        <div className="absolute top-4 right-4 text-sm font-semibold text-slate-600 text-right">
          Planning &<br/>Generation
        </div>

        {/* Connection Lines */}
        {connections.map((conn, i) => (
          <ConnectionLine key={i} from={conn.from} to={conn.to} animated={i % 3 === 0} />
        ))}

        {/* Nodes */}
        {Object.entries(nodes).map(([key, node]) => (
          <Node
            key={key}
            {...node}
            onClick={() => setSelectedNode(node.id)}
          />
        ))}
      </div>

      {/* Modal for Node Details */}
      <AnimatePresence>
        {selectedNodeData && (
          <motion.div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedNode(null)}
          >
            <motion.div
              className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 p-8"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-xl ${selectedNodeData.color}`}>
                    <selectedNodeData.icon className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="text-2xl font-bold text-slate-900">{selectedNodeData.title}</h4>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <p className="text-slate-600 text-sm mb-4 font-medium">{selectedNodeData.description}</p>
              <p className="text-slate-700 leading-relaxed">{selectedNodeData.details}</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
