// frontend/app/page.tsx

import Link from 'next/link'
import { ArrowRight, Database, TrendingUp, Lightbulb, BarChart3, Facebook, Instagram, Sparkles, Brain, Zap } from 'lucide-react'

export default function Home() {
  const sections = [
    {
      title: 'News Events',
      description: 'Canonical news event seeds from research agents',
      icon: Database,
      href: '/news-events',
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50',
    },
    {
      title: 'Trends',
      description: 'Discovered social media trends and patterns',
      icon: TrendingUp,
      href: '/trends',
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'from-purple-50 to-pink-50',
    },
    {
      title: 'Ungrounded',
      description: 'Creative content ideas not tied to news or trends',
      icon: Lightbulb,
      href: '/ungrounded',
      gradient: 'from-amber-500 to-orange-500',
      bgGradient: 'from-amber-50 to-orange-50',
    },
    {
      title: 'Insights',
      description: 'Engagement analysis and performance reports',
      icon: BarChart3,
      href: '/insights',
      gradient: 'from-green-500 to-emerald-500',
      bgGradient: 'from-green-50 to-emerald-50',
    },
    {
      title: 'Facebook',
      description: 'Published and pending Facebook content',
      icon: Facebook,
      href: '/facebook',
      gradient: 'from-blue-600 to-blue-700',
      bgGradient: 'from-blue-50 to-blue-100',
    },
    {
      title: 'Instagram',
      description: 'Published and pending Instagram content',
      icon: Instagram,
      href: '/instagram',
      gradient: 'from-pink-600 to-rose-600',
      bgGradient: 'from-pink-50 to-rose-50',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="relative mb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-100/50 via-secondary-100/30 to-accent-100/50 rounded-3xl blur-3xl"></div>
        <div className="relative text-center py-12 px-6">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="relative">
              <Brain className="w-12 h-12 text-primary-600 animate-pulse-slow" />
              <Sparkles className="absolute -top-1 -right-1 w-6 h-6 text-secondary-600 animate-bounce-slow" />
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-primary-600 via-secondary-600 to-accent-600 bg-clip-text text-transparent animate-gradient">
              Living Knowledge Database
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-700 max-w-3xl mx-auto mb-8 leading-relaxed">
            Explore content seeds, insights, and published posts from your
            <span className="font-semibold text-primary-600"> autonomous social media management framework</span>
          </p>
          <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2 glass px-4 py-2 rounded-full">
              <Zap className="w-4 h-4 text-amber-500" />
              <span>AI-Powered</span>
            </div>
            <div className="flex items-center gap-2 glass px-4 py-2 rounded-full">
              <Brain className="w-4 h-4 text-purple-500" />
              <span>Intelligent Agents</span>
            </div>
            <div className="flex items-center gap-2 glass px-4 py-2 rounded-full">
              <Sparkles className="w-4 h-4 text-primary-500" />
              <span>Real-time Insights</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {sections.map((section, index) => (
          <Link
            key={section.href}
            href={section.href}
            className="group relative block overflow-hidden bg-white rounded-2xl shadow-soft hover:shadow-glow transition-all duration-300 hover-lift border border-gray-100 animate-slide-up"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            {/* Background gradient on hover */}
            <div className={`absolute inset-0 bg-gradient-to-br ${section.bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>

            {/* Content */}
            <div className="relative p-6">
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${section.gradient} text-white shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300`}>
                  <section.icon className="w-7 h-7" />
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-2 transition-all duration-300" />
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                {section.title}
              </h2>
              <p className="text-gray-600 text-sm leading-relaxed">
                {section.description}
              </p>
            </div>

            {/* Shine effect on hover */}
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
            </div>
          </Link>
        ))}
      </div>

      {/* About Section */}
      <div className="relative overflow-hidden glass rounded-2xl shadow-soft border border-white/50 animate-slide-up">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-primary-200/30 to-secondary-200/30 rounded-full blur-3xl"></div>
        <div className="relative p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-primary-600" />
            About This System
          </h2>
          <p className="text-lg text-gray-700 mb-8 leading-relaxed">
            This Living Knowledge Database provides complete visibility into your autonomous social media management framework.
            The system leverages multiple AI agents to discover content opportunities, analyze engagement patterns, plan strategic content,
            create posts with AI-generated media, and seamlessly publish to Facebook and Instagram.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="group p-6 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-100 hover:shadow-lg transition-all duration-300">
              <Database className="w-8 h-8 text-blue-600 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="text-lg font-bold text-gray-900 mb-2">Content Seeds</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Browse news events, social media trends, and creative ideas that form the foundation for all content.
              </p>
            </div>
            <div className="group p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100 hover:shadow-lg transition-all duration-300">
              <Zap className="w-8 h-8 text-purple-600 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="text-lg font-bold text-gray-900 mb-2">Platform Posts</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                View created content for Facebook and Instagram, including publishing status and performance metrics.
              </p>
            </div>
            <div className="group p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-100 hover:shadow-lg transition-all duration-300">
              <BarChart3 className="w-8 h-8 text-green-600 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="text-lg font-bold text-gray-900 mb-2">Analytics</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Access insights reports that reveal what content resonates with your audience.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
