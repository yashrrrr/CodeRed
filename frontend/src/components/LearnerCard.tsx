'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { 
  User, 
  Mail, 
  Phone, 
  GraduationCap, 
  TrendingUp, 
  Clock,
  MessageSquare,
  Mail as MailIcon,
  Smartphone,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

import { Learner } from '../types'
import { formatDate, formatRiskScore, getRiskColor, getRiskBgColor } from '../lib/utils'
import { NudgeGenerator } from './NudgeGenerator'

interface LearnerCardProps {
  learner: Learner
  onGenerateNudge: (learnerId: string, channel: string) => void
  isGenerating?: boolean
}

export function LearnerCard({ learner, onGenerateNudge, isGenerating }: LearnerCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const riskColor = getRiskColor(learner.risk_label)
  const riskBgColor = getRiskBgColor(learner.risk_label)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className="glass-effect rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all duration-300"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-lg">
              {learner.name.charAt(0).toUpperCase()}
            </div>
            <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${riskBgColor}`} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{learner.name}</h3>
            <p className="text-sm text-gray-400">{learner.program}</p>
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-2 rounded-lg bg-gray-600/20 hover:bg-gray-600/30 transition-colors text-gray-300 hover:text-white"
        >
          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </motion.button>
      </div>

      {/* Risk Badge */}
      <div className="flex items-center justify-between mb-4">
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${riskBgColor}`}>
          <span className={riskColor}>
            {learner.risk_label.toUpperCase()} RISK
          </span>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-400">Risk Score</div>
          <div className={`text-lg font-bold ${riskColor}`}>
            {formatRiskScore(learner.risk_score)}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
          <div className="text-2xl font-bold text-blue-400">
            {learner.completed_percent.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-400">Completion</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-green-500/10 border border-green-500/20">
          <div className="text-2xl font-bold text-green-400">
            {learner.avg_quiz_score.toFixed(1)}
          </div>
          <div className="text-xs text-gray-400">Quiz Score</div>
        </div>
      </div>

      {/* Contact Info */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Mail className="h-4 w-4" />
          <span className="truncate">{learner.email}</span>
        </div>
        {learner.phone && (
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Phone className="h-4 w-4" />
            <span>{learner.phone}</span>
          </div>
        )}
        {learner.last_login && (
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Clock className="h-4 w-4" />
            <span>Last login: {formatDate(learner.last_login)}</span>
          </div>
        )}
      </div>

      {/* Expandable Content */}
      <motion.div
        initial={false}
        animate={{ height: isExpanded ? 'auto' : 0 }}
        transition={{ duration: 0.3 }}
        className="overflow-hidden"
      >
        <div className="pt-4 border-t border-white/10">
          {/* Additional Metrics */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="text-center p-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
              <div className="text-lg font-bold text-yellow-400">
                {learner.consecutive_missed_sessions}
              </div>
              <div className="text-xs text-gray-400">Missed Sessions</div>
            </div>
            <div className="text-center p-2 rounded-lg bg-purple-500/10 border border-purple-500/20">
              <div className="text-lg font-bold text-purple-400">
                {learner.nudges?.length || 0}
              </div>
              <div className="text-xs text-gray-400">Nudges Sent</div>
            </div>
          </div>

          {/* Nudge Generator */}
          <NudgeGenerator
            learner={learner}
            onGenerateNudge={onGenerateNudge}
            isGenerating={isGenerating}
          />
        </div>
      </motion.div>
    </motion.div>
  )
}
