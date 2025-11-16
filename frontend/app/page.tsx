// frontend/app/page.tsx

import { Brain, Zap, TrendingUp, Target, Users, RefreshCw } from 'lucide-react'
import ArchitectureDiagram from '@/components/home/ArchitectureDiagram'

export default function Home() {
  const keyTerms = [
    {
      term: 'Content Seeds',
      definition: 'Ideas for posts derived from news events, social media trends, or creative brainstorming that form the foundation for all content.',
    },
    {
      term: 'Living Knowledge Base',
      definition: 'A centralized, interactive repository storing all campaign data, enabling human oversight and deep understanding of agent decision-making.',
    },
    {
      term: 'Insights Agent',
      definition: 'An AI agent that analyzes campaign performance and synthesizes reports to inform future strategic decisions.',
    },
    {
      term: 'Guardrails',
      definition: 'Validation mechanisms that ensure content plans comply with budget constraints, posting frequency, and brand guidelines.',
    },
  ]

  const contributions = [
    {
      title: 'True End-to-End Agentic Solution',
      description: 'A fully autonomous system that handles everything from content ideation to publishing, with intelligent agents orchestrating each step of the campaign lifecycle.',
      icon: Brain,
      color: 'from-blue-600 to-cyan-600',
    },
    {
      title: 'Adaptive Learning & Strategic Refinement',
      description: 'Continuously analyzes performance metrics and audience engagement to refine content strategy, improving effectiveness over time through data-driven insights.',
      icon: RefreshCw,
      color: 'from-purple-600 to-pink-600',
    },
    {
      title: 'Real Impact & Engagement',
      description: 'Delivers measurable results with content that resonates with target audiences, driving meaningful engagement across social media platforms.',
      icon: TrendingUp,
      color: 'from-green-600 to-emerald-600',
    },
    {
      title: 'Easy Parallel Deployment',
      description: 'Designed for scalability, enabling simultaneous management of multiple campaigns with minimal overhead and configuration.',
      icon: Target,
      color: 'from-orange-600 to-red-600',
    },
    {
      title: 'Cross-Platform Synthesized Insights',
      description: 'Unifies data from Facebook and Instagram to provide holistic analytics and strategic recommendations across all platforms.',
      icon: Users,
      color: 'from-cyan-600 to-blue-600',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto space-y-16">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
        <div className="relative text-center py-16 px-6">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="relative">
              <Zap className="w-16 h-16 text-cyan-600" />
              <div className="absolute inset-0 blur-xl bg-cyan-400 opacity-40 animate-pulse-slow"></div>
            </div>
          </div>
          <h1 className="text-6xl md:text-7xl font-bold mb-6 text-slate-900">
            Socially Automated
          </h1>
          <p className="text-2xl font-semibold text-slate-700 mb-4">
            An Agentic Engagement Engine
          </p>
          <p className="text-lg md:text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed">
            An adaptive, learning, end-to-end agentic framework for managing cross-platform social media campaigns
            with intelligent automation, strategic insights, and seamless execution.
          </p>
        </div>
      </div>

      {/* Architecture Diagram */}
      <section>
        <ArchitectureDiagram />
      </section>

      {/* Key Terms & Definitions */}
      <section className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
        <h2 className="text-3xl font-bold text-slate-900 mb-8 text-center">Key Terms & Definitions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {keyTerms.map((item, index) => (
            <div
              key={index}
              className="p-6 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200 hover:shadow-lg transition-all duration-300"
            >
              <h3 className="text-xl font-bold text-slate-900 mb-3">{item.term}</h3>
              <p className="text-slate-700 leading-relaxed">{item.definition}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Important Contributions */}
      <section className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl shadow-2xl p-12 border border-slate-700">
        <h2 className="text-4xl font-bold text-white mb-4 text-center">Important Contributions</h2>
        <p className="text-slate-300 text-center mb-12 text-lg max-w-3xl mx-auto">
          This system represents a significant advancement in autonomous social media management,
          combining cutting-edge AI agents with strategic analytics and seamless platform integration.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {contributions.slice(0, 3).map((contribution, index) => (
            <div
              key={index}
              className="group p-6 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 hover:border-cyan-500 transition-all duration-300 hover:shadow-xl hover:shadow-cyan-500/20"
            >
              <div className={`inline-flex p-4 rounded-xl bg-gradient-to-br ${contribution.color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
                <contribution.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{contribution.title}</h3>
              <p className="text-slate-300 leading-relaxed">{contribution.description}</p>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8 max-w-4xl mx-auto">
          {contributions.slice(3).map((contribution, index) => (
            <div
              key={index}
              className="group p-6 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 hover:border-cyan-500 transition-all duration-300 hover:shadow-xl hover:shadow-cyan-500/20"
            >
              <div className={`inline-flex p-4 rounded-xl bg-gradient-to-br ${contribution.color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
                <contribution.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{contribution.title}</h3>
              <p className="text-slate-300 leading-relaxed">{contribution.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
