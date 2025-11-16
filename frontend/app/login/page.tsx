// frontend/app/login/page.tsx

'use client'

import { LogIn, Zap } from 'lucide-react'

export default function LoginPage() {
  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="max-w-md w-full">
        {/* Login Card */}
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-100/30 via-blue-100/20 to-slate-100/30 rounded-3xl blur-3xl"></div>
          <div className="relative bg-white rounded-2xl p-8 border border-slate-200 shadow-xl">
            {/* Logo */}
            <div className="flex items-center justify-center mb-8">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <div className="absolute inset-0 bg-cyan-500 rounded-2xl blur-xl opacity-30 animate-pulse-slow"></div>
              </div>
            </div>

            {/* Title */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-slate-900 mb-2">
                Socially Automated
              </h1>
              <p className="text-slate-600">
                Sign in to manage your campaigns
              </p>
            </div>

            {/* Login Message */}
            <div className="space-y-4">
              <div className="p-6 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200 text-center">
                <LogIn className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                <h2 className="text-lg font-semibold text-slate-900 mb-2">
                  Authentication Coming Soon
                </h2>
                <p className="text-sm text-slate-600 leading-relaxed">
                  User authentication and authorization features are currently under development.
                  For now, you can explore the application freely.
                </p>
              </div>

              {/* Back to Home Button */}
              <a
                href="/"
                className="block w-full px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-center font-medium rounded-lg hover:from-cyan-700 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Back to Home
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
