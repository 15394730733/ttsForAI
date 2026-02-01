/**
 * API type definitions.
 *
 * Provides TypeScript interfaces for all API requests and responses
 * based on OpenAPI specification.
 */

/**
 * Task status enumeration
 */
export enum TaskStatus {
  QUEUED = 'queued',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

/**
 * Task create request
 */
export interface TaskCreateRequest {
  text: string
  voice_name?: string
  rate?: number
  pitch?: number
  volume?: number
  filename?: string
}

/**
 * Task response
 */
export interface Task {
  task_id: string
  text: string
  voice_name: string
  rate: number
  pitch: number
  volume: number
  status: TaskStatus
  progress: number
  file_path: string | null
  filename: string | null  // Actual filename used (without extension)
  error_message: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

/**
 * Queue status response
 */
export interface QueueStatus {
  queued_count: number
  processing_count: number
  completed_count: number
  current_task: Task | null
  max_queue_size: number
}

/**
 * History record
 */
export interface HistoryRecord {
  id: number
  task_id: string
  text_summary: string
  voice_params: VoiceParams
  created_at: string
  file_path: string
  file_size: number
  status: string
}

/**
 * Voice parameters
 */
export interface VoiceParams {
  voice_name: string
  voice_id?: string
  rate: number
  pitch: number
  volume: number
}

/**
 * Voice info
 */
export interface VoiceInfo {
  name: string
  voice_id: string
  description: string
  default: boolean
}

/**
 * Voices list response
 */
export interface VoicesResponse {
  voices: VoiceInfo[]
}

/**
 * Health check response
 */
export interface HealthResponse {
  status: string
  version: string
  service: string
  database?: {
    status: string
    message?: string
  }
  tts_engine?: {
    status: string
    name: string
  }
}

/**
 * Error response
 */
export interface ErrorResponse {
  error: string
  message: string
  details?: Record<string, unknown>
}
