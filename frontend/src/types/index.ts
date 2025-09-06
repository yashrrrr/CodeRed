export interface Learner {
  id: string
  name: string
  email: string
  phone?: string
  program: string
  last_login?: string
  completed_percent: number
  avg_quiz_score: number
  consecutive_missed_sessions: number
  risk_score: number
  risk_label: 'low' | 'medium' | 'high'
  nudges?: Nudge[]
  events?: Event[]
}

export interface Nudge {
  id: string
  learner_id: string
  channel: 'in-app' | 'whatsapp' | 'email'
  type: string
  content: string
  gpt_prompt_version?: string
  gpt_fallback: boolean
  status: string
  created_at: string
}

export interface Event {
  id: string
  learner_id: string
  type: string
  event_metadata?: Record<string, any>
  timestamp: string
}

export interface NudgeRequest {
  channel: 'in-app' | 'whatsapp' | 'email'
}

export interface NudgeResponse {
  id: string
  content: string
  channel: string
  prompt_version?: string
  gptFallback: boolean
  learner_id: string
}

export interface ApiError {
  message: string
  status: number
}
