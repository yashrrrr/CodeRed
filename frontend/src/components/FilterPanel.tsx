'use client'

import { motion } from 'framer-motion'
import { Filter, RefreshCw, Users, AlertTriangle, TrendingUp, Target } from 'lucide-react'

interface FilterPanelProps {
  selectedRisk: string
  onRiskChange: (risk: string) => void
  onRefresh: () => void
}

const riskOptions = [
  { value: 'all', label: 'All Learners', icon: Users, color: 'text-gray-400' },
  { value: 'high', label: 'High Risk', icon: AlertTriangle, color: 'text-red-400' },
  { value: 'medium', label: 'Medium Risk', icon: TrendingUp, color: 'text-yellow-400' },
  { value: 'low', label: 'Low Risk', icon: Target, color: 'text-green-400' },
]

export function FilterPanel({ selectedRisk, onRiskChange, onRefresh }: FilterPanelProps) {
  return (
    <div className="glass-effect rounded-2xl p-6 border border-white/10">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-blue-500/20 border border-blue-500/30">
          <Filter className="h-5 w-5 text-blue-400" />
        </div>
        <h3 className="text-lg font-semibold text-white">Filters & Actions</h3>
      </div>

      {/* Risk Filter */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-300">Filter by Risk Level</h4>
        <div className="space-y-2">
          {riskOptions.map((option, index) => {
            const Icon = option.icon
            const isSelected = selectedRisk === option.value
            
            return (
              <motion.button
                key={option.value}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onRiskChange(option.value)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all duration-200 ${
                  isSelected
                    ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
                    : 'bg-gray-600/20 border-gray-600/50 text-gray-400 hover:border-gray-500/50 hover:text-gray-300'
                }`}
              >
                <Icon className={`h-4 w-4 ${isSelected ? 'text-blue-400' : option.color}`} />
                <span className="text-sm font-medium">{option.label}</span>
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="ml-auto w-2 h-2 rounded-full bg-blue-400"
                  />
                )}
              </motion.button>
            )
          })}
        </div>
      </div>

      {/* Divider */}
      <div className="my-6 border-t border-white/10" />

      {/* Quick Actions */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-300">Quick Actions</h4>
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onRefresh}
          className="w-full flex items-center gap-3 p-3 rounded-lg bg-green-600/20 border border-green-600/30 hover:bg-green-600/30 transition-colors text-green-300 hover:text-green-200"
        >
          <RefreshCw className="h-4 w-4" />
          <span className="text-sm font-medium">Refresh Data</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full flex items-center gap-3 p-3 rounded-lg bg-purple-600/20 border border-purple-600/30 hover:bg-purple-600/30 transition-colors text-purple-300 hover:text-purple-200"
        >
          <Users className="h-4 w-4" />
          <span className="text-sm font-medium">Export Data</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full flex items-center gap-3 p-3 rounded-lg bg-blue-600/20 border border-blue-600/30 hover:bg-blue-600/30 transition-colors text-blue-300 hover:text-blue-200"
        >
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm font-medium">Bulk Actions</span>
        </motion.button>
      </div>

      {/* Stats Summary */}
      <div className="mt-6 p-4 rounded-lg bg-gray-800/30 border border-gray-700/50">
        <h5 className="text-xs font-medium text-gray-400 mb-2">Current Filter</h5>
        <div className="text-sm text-white">
          {riskOptions.find(opt => opt.value === selectedRisk)?.label || 'All Learners'}
        </div>
      </div>
    </div>
  )
}
