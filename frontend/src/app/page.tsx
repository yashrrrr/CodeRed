'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  AlertTriangle, 
  TrendingUp, 
  Brain, 
  MessageSquare, 
  Mail, 
  Smartphone,
  RefreshCw,
  Filter,
  BarChart3,
  Target,
  Zap
} from 'lucide-react'

import { DashboardHeader } from '../components/DashboardHeader'
import { MetricCard } from '../components/MetricCard'
import { LearnerCard } from '../components/LearnerCard'
import { NudgeGenerator } from '../components/NudgeGenerator'
import { RiskChart } from '../components/RiskChart'
import { FilterPanel } from '../components/FilterPanel'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { api } from '../lib/api'
import { Learner, NudgeRequest } from '../types'

export default function Dashboard() {
  const [learners, setLearners] = useState<Learner[]>([])
  const [filteredLearners, setFilteredLearners] = useState<Learner[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRisk, setSelectedRisk] = useState<string>('all')
  const [generatingNudge, setGeneratingNudge] = useState<string | null>(null)

  useEffect(() => {
    fetchLearners()
  }, [])

  useEffect(() => {
    filterLearners()
  }, [learners, selectedRisk])

  const fetchLearners = async () => {
    try {
      setLoading(true)
      const data = await api.getLearners(selectedRisk === 'all' ? undefined : selectedRisk)
      setLearners(data)
    } catch (error) {
      console.error('Failed to fetch learners:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterLearners = () => {
    if (selectedRisk === 'all') {
      setFilteredLearners(learners)
    } else {
      setFilteredLearners(learners.filter(learner => learner.risk_label === selectedRisk))
    }
  }

  const generateNudge = async (learnerId: string, channel: string) => {
    try {
      setGeneratingNudge(learnerId)
      const nudgeRequest: NudgeRequest = { channel }
      const result = await api.generateNudge(learnerId, nudgeRequest)
      
      // Show success notification
      console.log('Nudge generated:', result)
      
      // Refresh learners data
      await fetchLearners()
    } catch (error) {
      console.error('Failed to generate nudge:', error)
    } finally {
      setGeneratingNudge(null)
    }
  }

  const metrics = {
    total: learners.length,
    highRisk: learners.filter(l => l.risk_label === 'high').length,
    mediumRisk: learners.filter(l => l.risk_label === 'medium').length,
    lowRisk: learners.filter(l => l.risk_label === 'low').length,
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <DashboardHeader onRefresh={fetchLearners} />
      
      <div className="container mx-auto px-4 py-8">
        {/* Metrics Overview */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <MetricCard
            title="Total Learners"
            value={metrics.total}
            icon={Users}
            color="blue"
            trend="+12%"
          />
          <MetricCard
            title="High Risk"
            value={metrics.highRisk}
            icon={AlertTriangle}
            color="red"
            trend={`${((metrics.highRisk / metrics.total) * 100).toFixed(1)}%`}
          />
          <MetricCard
            title="Medium Risk"
            value={metrics.mediumRisk}
            icon={TrendingUp}
            color="yellow"
            trend={`${((metrics.mediumRisk / metrics.total) * 100).toFixed(1)}%`}
          />
          <MetricCard
            title="Low Risk"
            value={metrics.lowRisk}
            icon={Target}
            color="green"
            trend={`${((metrics.lowRisk / metrics.total) * 100).toFixed(1)}%`}
          />
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Risk Distribution Chart */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="glass-effect rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-6">
                <BarChart3 className="h-6 w-6 text-blue-400" />
                <h2 className="text-xl font-semibold text-white">Risk Distribution</h2>
              </div>
              <RiskChart data={metrics} />
            </motion.div>

            {/* Learners Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Learners</h2>
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-400">
                    {filteredLearners.length} of {learners.length} learners
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredLearners.map((learner, index) => (
                  <motion.div
                    key={learner.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <LearnerCard
                      learner={learner}
                      onGenerateNudge={generateNudge}
                      isGenerating={generatingNudge === learner.id}
                    />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Filter Panel */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <FilterPanel
                selectedRisk={selectedRisk}
                onRiskChange={setSelectedRisk}
                onRefresh={fetchLearners}
              />
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="glass-effect rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-6">
                <Zap className="h-6 w-6 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">Quick Actions</h3>
              </div>
              
              <div className="space-y-3">
                <button
                  onClick={fetchLearners}
                  className="w-full flex items-center gap-3 p-3 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 transition-colors text-blue-300 hover:text-blue-200"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Refresh Data</span>
                </button>
                
                <button className="w-full flex items-center gap-3 p-3 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 transition-colors text-purple-300 hover:text-purple-200">
                  <Brain className="h-4 w-4" />
                  <span>Generate All Nudges</span>
                </button>
                
                <button className="w-full flex items-center gap-3 p-3 rounded-lg bg-green-600/20 hover:bg-green-600/30 transition-colors text-green-300 hover:text-green-200">
                  <MessageSquare className="h-4 w-4" />
                  <span>Send Bulk Messages</span>
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
