// frontend/app/page.tsx

import Link from 'next/link'
import { ArrowRight, Database, TrendingUp, Lightbulb, BarChart3, Facebook, Instagram } from 'lucide-react'

export default function Home() {
  const sections = [
    {
      title: 'News Events',
      description: 'Canonical news event seeds from research agents',
      icon: Database,
      href: '/news-events',
      color: 'bg-blue-500',
    },
    {
      title: 'Trends',
      description: 'Discovered social media trends and patterns',
      icon: TrendingUp,
      href: '/trends',
      color: 'bg-purple-500',
    },
    {
      title: 'Ungrounded',
      description: 'Creative content ideas not tied to news or trends',
      icon: Lightbulb,
      href: '/ungrounded',
      color: 'bg-yellow-500',
    },
    {
      title: 'Insights',
      description: 'Engagement analysis and performance reports',
      icon: BarChart3,
      href: '/insights',
      color: 'bg-green-500',
    },
    {
      title: 'Facebook',
      description: 'Published and pending Facebook content',
      icon: Facebook,
      href: '/facebook',
      color: 'bg-blue-600',
    },
    {
      title: 'Instagram',
      description: 'Published and pending Instagram content',
      icon: Instagram,
      href: '/instagram',
      color: 'bg-pink-600',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Living Knowledge Database
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Explore content seeds, insights, and published posts from your autonomous social media management framework
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sections.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="group block p-6 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`${section.color} p-3 rounded-lg text-white`}>
                <section.icon className="w-6 h-6" />
              </div>
              <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {section.title}
            </h2>
            <p className="text-gray-600">
              {section.description}
            </p>
          </Link>
        ))}
      </div>

      <div className="mt-12 p-6 bg-white rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          About This System
        </h2>
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-600">
            This Living Knowledge Database provides visibility into the entire autonomous social media management framework.
            The system uses multiple AI agents to discover content opportunities, analyze engagement, plan weekly content,
            create posts with AI-generated media, and publish to Facebook and Instagram.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Content Seeds</h3>
              <p className="text-sm text-gray-600">
                Browse news events, social media trends, and creative ideas that form the foundation for all content.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Platform Posts</h3>
              <p className="text-sm text-gray-600">
                View created content for Facebook and Instagram, including publishing status and performance.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Analytics</h3>
              <p className="text-sm text-gray-600">
                Access insights reports that analyze what content works with your audience.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
