// frontend/app/page.tsx

import { Brain, Network, TrendingUp, Target, Users, RefreshCw } from 'lucide-react'
import ArchitectureDiagram from '@/components/home/ArchitectureDiagram'

export default function Home() {
  const contributions = [
    {
      title: 'Fully Autonomous Multi-Agent Pipeline',
      description:
        'A coordinated network of specialized agents handles ingestion, planning, creation, and publishing — turning social media management into a true end-to-end autonomous system.',
      icon: Brain,
      color: 'from-blue-600 to-cyan-600',
    },
    {
      title: 'Closed-Loop Learning System',
      description:
        'The Insights Agent continuously evaluates real campaign results and feeds structured insight reports back into planning and ideation, making each cycle smarter than the last.',
      icon: RefreshCw,
      color: 'from-purple-600 to-pink-600',
    },
    {
      title: 'High-Fidelity Cross-Platform Intelligence',
      description:
        'Unifies data from Facebook and Instagram into a single knowledge layer, enabling platform-aware strategy, richer analytics, and more effective content decisions.',
      icon: TrendingUp,
      color: 'from-green-600 to-emerald-600',
    },
    {
      title: 'Scalable Parallel Campaigns',
      description:
        'Designed for multi-brand and multi-campaign operation, with content seeds, plans, and content lifecycles that can be segmented and scaled with minimal additional overhead.',
      icon: Target,
      color: 'from-orange-600 to-red-600',
    },
    {
      title: 'Transparent Human-In-The-Loop Control',
      description:
        'The Living Knowledge Base UI exposes every seed, decision, and output so humans can audit, override, or co-create with the agents at any point in the workflow.',
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
              <Network className="w-16 h-16 text-cyan-600" />
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

      {/* High Level Overview */}
      <section className="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
        <h2 className="text-3xl font-bold text-slate-900 mb-8 text-center">High-Level Overview</h2>
        <div className="prose prose-slate max-w-none">
          <div className="text-slate-700 leading-relaxed space-y-6">
            {/* Description */}
            <div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Description</h3>
              <p>
                This system is a <strong className="font-bold text-slate-950">fully autonomous, end-to-end agentic framework</strong> that continuously ingests knowledge, learns from outcomes, and produces high-performance, cross-platform social media campaigns with minimal human intervention.
              </p>
              <p>
                Each agent in the system optimizes for <strong className="font-bold text-slate-950">maximum user engagement</strong> within a defined target audience and is instructed to execute its specialized task at the highest possible level to support this overall goal.
              </p>
            </div>

            {/* Living Knowledge Base */}
            <div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Living Knowledge Base</h3>
              <p>
                At the center of the system is the <strong className="font-bold text-slate-950">Living Knowledge Base</strong> — a continuously updated, fully inspectable record of every content seed, data source, insight, post, and decision made by the framework. It provides complete transparency into agent reasoning, supports human-in-the-loop collaboration, and serves as the core intelligence source powering all downstream decision-making.
              </p>
            </div>

            {/* Knowledge Ingestion & Ideation */}
            <div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Knowledge Ingestion & Ideation</h3>
              <p>
                All posts produced by the system originate from "content seeds." These seeds exist in three categories, each with its own ingestion pipeline.
              </p>
              <ul className="list-disc pl-6 space-y-3 text-slate-950">
                <li className="text-slate-950">
                  <strong className="font-bold text-slate-950">News Event Seeds</strong> are derived from contemporary events relevant to the target audience. They originate from deep internet research performed by <strong className="font-bold text-slate-950">Perplexity Sonar</strong> and <strong className="font-bold text-slate-950">ChatGPT Deep Research</strong> agents, which surface emerging stories, consolidate sources, and generate high-quality structured event objects.
                </li>
                <li className="text-slate-950">
                  <strong className="font-bold text-slate-950">Trend Seeds</strong> capture viral formats, hashtags, patterns, and content archetypes from Facebook and Instagram. The <strong className="font-bold text-slate-950">Trend Research Agent</strong>, equipped with high-volume scraping and exploration tools, analyzes real-time social data to identify platform-native trends and opportunities.
                </li>
                <li className="text-slate-950">
                  <strong className="font-bold text-slate-950">Ungrounded Seeds</strong> are creative, non-news, non-trend conceptual prompts generated by a dedicated ideation agent. These seeds broaden the creative landscape and enable content that is not dependent on external events.
                </li>
              </ul>
              <p>
                All seeds undergo <strong className="font-bold text-slate-950">deduplication, consolidation, and validation</strong> before entering the knowledge base.
              </p>
            </div>

            {/* Adaptive Learning */}
            <div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Adaptive Learning</h3>
              <p>
                The <strong className="font-bold text-slate-950">Insights Agent</strong> periodically analyzes engagement metrics and audience behavior from live posts. It reviews comments, performance data, and platform interactions to produce structured, timestamped insight reports. These insights directly shape future strategy, ensuring the system continuously adapts and improves.
              </p>
            </div>

            {/* Planning & Publishing Pipeline */}
            <div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Planning & Publishing Pipeline</h3>
              <p>
                The <strong className="font-bold text-slate-950">Planner Agent</strong> synthesizes seeds, insights, and budget constraints to generate a weekly content plan. It determines:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-primary-950">
                <li className="text-slate-700">which seeds to activate</li>
                <li className="text-slate-700">how many posts to produce per seed</li>
                <li className="text-slate-700">media distribution across videos, images, reels, carousels, and text posts</li>
                <li className="text-slate-700">whether the plan meets global constraints and platform requirements</li>
              </ul>
              <p>
                Once the plan is finalized, multiple <strong className="font-bold text-slate-950">Content Creation Agents</strong> collaboratively produce all required media and copy, drawing context directly from the Living Knowledge Base. Media is generated through image/video production services, stored in Supabase, and prepared in platform-specific formats.
              </p>
              <p>
                Before publishing, all completed posts pass through the <strong className="font-bold text-slate-950">Content Verifier Agent</strong>. This safety verification layer reviews each post's text and generated media, comparing against source materials to ensure:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-primary-950">
                <li className="text-slate-700">no offensive content (hate speech, slurs, explicit material)</li>
                <li className="text-slate-700">factual accuracy for news-based posts against original sources</li>
              </ul>
              <p>
                Only verified posts proceed to the <strong className="font-bold text-slate-950">automated publishers</strong> for Instagram and Facebook, which post the content according to schedule. All resulting performance data is fed back into the knowledge base, enabling <strong className="font-bold text-slate-950">continuous closed-loop strategic refinement</strong>.
              </p>
            </div>

            {/* Interactive Comment Responding */}
            <div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Interactive Comment Responding</h3>
              <p>
                A <strong className="font-bold text-slate-950">Facebook Webhook</strong> monitors comment activity on the page's feed. When a comment is posted, it is logged and forwarded to the <strong className="font-bold text-slate-950">Comment Responder Agent</strong>.
              </p>
              <p>
                Instagram, rather than a webhook, uses periodic polling to detect new comments, which are similarly logged and routed.
              </p>
              <p>
                The <strong className="font-bold text-slate-950">Comment Responder Agent</strong> considers the comment, the corresponding post's content and metadata, and any prior discussion on the thread, then generates a thoughtful and contextually relevant response for the user.
              </p>
            </div>
          </div>
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
