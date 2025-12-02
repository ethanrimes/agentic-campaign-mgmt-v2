// frontend/app/page.tsx

'use client'

import { Brain, Network, TrendingUp, Target, Users, RefreshCw, ArrowRight, Sparkles } from 'lucide-react'
import ArchitectureDiagram from '@/components/home/ArchitectureDiagram'
import { motion } from 'framer-motion'

export default function Home() {
  const contributions = [
    {
      title: 'Autonomous Pipeline',
      description:
        'End-to-end agents handle ingestion, planning, creation, and publishing.',
      icon: Brain,
      color: 'text-blue-600',
      bg: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      title: 'Closed-Loop Learning',
      description:
        'Insights Agent evaluates real performance to refine future strategy.',
      icon: RefreshCw,
      color: 'text-green-600',
      bg: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      title: 'Cross-Platform',
      description:
        'Unified intelligence across Facebook and Instagram.',
      icon: TrendingUp,
      color: 'text-purple-600',
      bg: 'bg-purple-50 dark:bg-purple-900/20',
    },
    {
      title: 'Scalable Campaigns',
      description:
        'Multi-brand operation with segmented content seeds and plans.',
      icon: Target,
      color: 'text-orange-600',
      bg: 'bg-orange-50 dark:bg-orange-900/20',
    },
    {
      title: 'Human-in-the-Loop',
      description:
        'Complete visibility into end-to-end operations, allowing humans to inspect, audit, and guide agent decisions at every step.',
      icon: Users,
      color: 'text-cyan-600',
      bg: 'bg-cyan-50 dark:bg-cyan-900/20',
    },
  ]

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <div className="space-y-24 pb-20 pt-12">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        {/* Animated Background Blobs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div 
            animate={{ 
              x: [0, 100, 0],
              y: [0, -50, 0],
              scale: [1, 1.2, 1]
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute -top-[20%] -left-[10%] w-[600px] h-[600px] bg-primary-200/30 dark:bg-primary-900/20 rounded-full blur-3xl" 
          />
          <motion.div 
            animate={{ 
              x: [0, -100, 0],
              y: [0, 50, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            className="absolute top-[20%] -right-[10%] w-[500px] h-[500px] bg-purple-200/30 dark:bg-purple-900/20 rounded-full blur-3xl" 
          />
        </div>

        <div className="relative container mx-auto px-4 text-center max-w-4xl">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-6xl md:text-7xl font-bold tracking-tight mb-6 text-slate-900 dark:text-white"
          >
            Socially Automated
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-2xl md:text-3xl font-light text-foreground mb-8"
          >
            An Agentic Engagement Engine
          </motion.p>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-lg text-muted-foreground leading-relaxed max-w-2xl mx-auto"
          >
            An adaptive, learning, end-to-end framework for managing cross-platform social media campaigns
            with intelligent automation, strategic insights, and seamless execution.
          </motion.p>
        </div>
      </section>

      {/* System Architecture */}
      <section className="container mx-auto px-4">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">System Architecture</h2>
        </div>
        
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="relative"
        >
          {/* Glow effect behind diagram */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 blur-3xl -z-10"></div>
          
          <ArchitectureDiagram />
        </motion.div>
      </section>

      {/* Key Features Grid */}
      <section className="container mx-auto px-4">
        <div className="flex items-center gap-4 mb-12">
          <div className="w-1 h-8 bg-gradient-to-b from-green-500 to-cyan-500 rounded-full"></div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Core Capabilities</h2>
        </div>

        <motion.div 
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {contributions.map((feature, index) => (
            <motion.div
              key={index}
              variants={item}
              className="glass-panel p-6 hover:border-primary/30 group bg-white/80 dark:bg-slate-900/80"
            >
              <div className={`w-12 h-12 rounded-2xl ${feature.bg} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className={`w-6 h-6 ${feature.color}`} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Technical Overview */}
      <section className="container mx-auto px-4">
         <div className="glass-panel p-8 md:p-12 bg-white/90 dark:bg-slate-900/90">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-8 text-center">How It Works</h2>
            
            <div className="space-y-12">
              <div className="flex flex-col md:flex-row gap-8 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 font-bold text-xl">1</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Knowledge Ingestion</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    The system starts by absorbing the world. <strong>Perplexity Sonar</strong> and <strong>Deep Research</strong> agents scour the web for news events, while <strong>Trend Researchers</strong> analyze social platforms for viral patterns. All of this is deduplicated and stored in the Living Knowledge Base.
                  </p>
                </div>
              </div>

              <div className="flex flex-col md:flex-row gap-8 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 font-bold text-xl">2</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Strategic Planning</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    The <strong>Planner Agent</strong> acts as the editor-in-chief. It reviews available content seeds, checks budget constraints, and consults past performance insights to build a balanced weekly content calendar that maximizes engagement.
                  </p>
                </div>
              </div>

              <div className="flex flex-col md:flex-row gap-8 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center text-pink-600 font-bold text-xl">3</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Creation & Verification</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Specialized <strong>Content Creator Agents</strong> generate high-fidelity media and copy. Before anything goes live, the <strong>Verifier Agent</strong> performs a rigorous multimodal safety check to ensure brand safety and factual accuracy.
                  </p>
                </div>
              </div>

              <div className="flex flex-col md:flex-row gap-8 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 font-bold text-xl">4</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Active Engagement</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Post-publishing, the system stays awake. Webhooks and pollers detect user comments immediately, and the <strong>Comment Responder Agent</strong> engages with the community in real-time, driving further reach and loyalty.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
