import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatRiskScore(score: number): string {
  return score.toFixed(3)
}

export function getRiskColor(riskLabel: string): string {
  switch (riskLabel.toLowerCase()) {
    case 'high':
      return 'text-red-400'
    case 'medium':
      return 'text-yellow-400'
    case 'low':
      return 'text-green-400'
    default:
      return 'text-gray-400'
  }
}

export function getRiskBgColor(riskLabel: string): string {
  switch (riskLabel.toLowerCase()) {
    case 'high':
      return 'risk-high'
    case 'medium':
      return 'risk-medium'
    case 'low':
      return 'risk-low'
    default:
      return 'bg-gray-100 dark:bg-gray-800'
  }
}

export function getChannelIcon(channel: string) {
  switch (channel) {
    case 'email':
      return '📧'
    case 'whatsapp':
      return '📱'
    case 'in-app':
      return '💬'
    default:
      return '📢'
  }
}

export function getChannelColor(channel: string): string {
  switch (channel) {
    case 'email':
      return 'text-blue-400'
    case 'whatsapp':
      return 'text-green-400'
    case 'in-app':
      return 'text-purple-400'
    default:
      return 'text-gray-400'
  }
}
