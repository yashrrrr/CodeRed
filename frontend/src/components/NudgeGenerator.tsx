'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { 
  MessageSquare, 
  Mail, 
  Smartphone, 
  Sparkles, 
  Copy, 
  Check,
  AlertCircle,
  Brain
} from 'lucide-react'

import { Learner } from '../types'
import { getChannelIcon, getChannelColor } from '../lib/utils'

interface NudgeGeneratorProps {
  learner: Learner
  onGenerateNudge: (learnerId: string, channel: string) => void
  isGenerating?: boolean
}

const channels = [
  { id: 'in-app', label: 'In-App', icon: MessageSquare, color: 'text-purple-400' },
  { id: 'whatsapp', label: 'WhatsApp', icon: Smartphone, color: 'text-green-400' },
  { id: 'email', label: 'Email', icon: Mail, color: 'text-blue-400' },
]

export function NudgeGenerator({ learner, onGenerateNudge, isGenerating }: NudgeGeneratorProps) {
  const [selectedChannel, setSelectedChannel] = useState('in-app')
  const [generatedNudge, setGeneratedNudge] = useState<string | null>(null)
  const [isFallback, setIsFallback] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleGenerateNudge = async () => {
    try {
      await onGenerateNudge(learner.id, selectedChannel)
      // In a real app, you'd get the actual nudge content from the API response
      // For now, we'll simulate it
      setGeneratedNudge(`Hi ${learner.name}! I noticed you haven't logged in for a while. Your progress is at ${learner.completed_percent.toFixed(1)}% completion. Let's get you back on track! 🚀`)
      setIsFallback(Math.random() > 0.7) // Simulate fallback mode
    } catch (error) {
      console.error('Failed to generate nudge:', error)
    }
  }

  const handleCopy = async () => {
    if (generatedNudge) {
      await navigator.clipboard.writeText(generatedNudge)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-4">
      {/* Channel Selection */}
      <div>
        <h4 className="text-sm font-medium text-white mb-3">Select Channel</h4>
        <div className="grid grid-cols-3 gap-2">
          {channels.map((channel) => {
            const Icon = channel.icon
            const isSelected = selectedChannel === channel.id
            
            return (
              <motion.button
                key={channel.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedChannel(channel.id)}
                className={`p-3 rounded-lg border transition-all duration-200 ${
                  isSelected
                    ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
                    : 'bg-gray-600/20 border-gray-600/50 text-gray-400 hover:border-gray-500/50 hover:text-gray-300'
                }`}
              >
                <Icon className={`h-4 w-4 mx-auto mb-1 ${isSelected ? 'text-blue-400' : channel.color}`} />
                <div className="text-xs font-medium">{channel.label}</div>
              </motion.button>
            )
          })}
        </div>
      </div>

      {/* Generate Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleGenerateNudge}
        disabled={isGenerating}
        className="w-full flex items-center justify-center gap-2 p-3 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-white font-medium"
      >
        {isGenerating ? (
          <>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              <Sparkles className="h-4 w-4" />
            </motion.div>
            <span>Generating...</span>
          </>
        ) : (
          <>
            <Brain className="h-4 w-4" />
            <span>Generate Nudge</span>
          </>
        )}
      </motion.button>

      {/* Generated Nudge Display */}
      {generatedNudge && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-3"
        >
          {/* Status Indicator */}
          <div className="flex items-center gap-2">
            {isFallback ? (
              <>
                <AlertCircle className="h-4 w-4 text-yellow-400" />
                <span className="text-sm text-yellow-400 font-medium">Fallback Mode</span>
                <span className="text-xs text-gray-400">(AI unavailable)</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 text-green-400" />
                <span className="text-sm text-green-400 font-medium">AI Generated</span>
                <span className="text-xs text-gray-400">(OpenAI powered)</span>
              </>
            )}
          </div>

          {/* Nudge Content */}
          <div className="relative">
            <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-700/50">
              <div className="flex items-start gap-3">
                <div className="text-lg">{getChannelIcon(selectedChannel)}</div>
                <div className="flex-1">
                  <div className="text-sm text-gray-300 leading-relaxed">
                    {generatedNudge}
                  </div>
                </div>
              </div>
            </div>

            {/* Copy Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleCopy}
              className="absolute top-2 right-2 p-2 rounded-lg bg-gray-700/50 hover:bg-gray-600/50 transition-colors text-gray-300 hover:text-white"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-400" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </motion.button>
          </div>

          {/* Channel Info */}
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span>Channel:</span>
            <span className={`font-medium ${getChannelColor(selectedChannel)}`}>
              {channels.find(c => c.id === selectedChannel)?.label}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  )
}
