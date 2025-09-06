import axios from 'axios'
import { Learner, NudgeRequest, NudgeResponse } from '../types'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const apiClient = {
  // Health check
  async healthCheck(): Promise<{ status: string; time: string; service: string }> {
    const response = await api.get('/api/health')
    return response.data
  },

  // Get all learners with optional risk filter
  async getLearners(risk?: string): Promise<Learner[]> {
    const params = risk ? { risk } : {}
    const response = await api.get('/api/learners', { params })
    return response.data
  },

  // Get a specific learner
  async getLearner(id: string): Promise<Learner> {
    const response = await api.get(`/api/learners/${id}`)
    return response.data
  },

  // Generate a nudge for a learner
  async generateNudge(learnerId: string, nudgeRequest: NudgeRequest): Promise<NudgeResponse> {
    const response = await api.post(`/api/learners/${learnerId}/nudge`, nudgeRequest)
    return response.data
  },

  // Get learner's nudges
  async getLearnerNudges(learnerId: string): Promise<NudgeResponse[]> {
    const response = await api.get(`/api/learners/${learnerId}/nudges`)
    return response.data
  },

  // Get learner's events
  async getLearnerEvents(learnerId: string): Promise<any[]> {
    const response = await api.get(`/api/learners/${learnerId}/events`)
    return response.data
  },

  // Compute risk scores for all learners
  async computeRiskScores(): Promise<void> {
    await api.post('/api/learners/compute-risk')
  },
}

export { api }
