'use client'

import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

interface RiskChartProps {
  data: {
    total: number
    highRisk: number
    mediumRisk: number
    lowRisk: number
  }
}

const COLORS = {
  high: '#ef4444',    // red-500
  medium: '#f59e0b',  // amber-500
  low: '#10b981',     // emerald-500
}

export function RiskChart({ data }: RiskChartProps) {
  const chartData = [
    {
      name: 'High Risk',
      value: data.highRisk,
      color: COLORS.high,
      percentage: ((data.highRisk / data.total) * 100).toFixed(1)
    },
    {
      name: 'Medium Risk',
      value: data.mediumRisk,
      color: COLORS.medium,
      percentage: ((data.mediumRisk / data.total) * 100).toFixed(1)
    },
    {
      name: 'Low Risk',
      value: data.lowRisk,
      color: COLORS.low,
      percentage: ((data.lowRisk / data.total) * 100).toFixed(1)
    }
  ].filter(item => item.value > 0)

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-gray-800/90 backdrop-blur-sm border border-gray-700/50 rounded-lg p-3 shadow-lg">
          <div className="flex items-center gap-2 mb-1">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: data.color }}
            />
            <span className="text-white font-medium">{data.name}</span>
          </div>
          <div className="text-sm text-gray-300">
            <div>Count: <span className="text-white font-semibold">{data.value}</span></div>
            <div>Percentage: <span className="text-white font-semibold">{data.percentage}%</span></div>
          </div>
        </div>
      )
    }
    return null
  }

  const CustomLegend = ({ payload }: any) => {
    return (
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {payload.map((entry: any, index: number) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="flex items-center gap-2"
          >
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm text-gray-300">{entry.value}</span>
            <span className="text-xs text-gray-500">
              ({chartData.find(d => d.name === entry.value)?.percentage}%)
            </span>
          </motion.div>
        ))}
      </div>
    )
  }

  if (data.total === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <div className="text-center">
          <div className="text-4xl mb-2">📊</div>
          <div>No data available</div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.color}
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
