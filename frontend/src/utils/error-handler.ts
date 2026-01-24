/**
 * Error handling utilities.
 *
 * Provides functions for error handling and user-friendly error messages.
 */
import type { ErrorResponse } from '@/types/api'

/**
 * API error class
 */
export class ApiError extends Error {
  status?: number
  details?: Record<string, unknown>

  constructor(message: string, status?: number, details?: Record<string, unknown>) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }
}

/**
 * Extract error message from error object
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    // Axios error
    if (error.response) {
      const data = error.response.data as ErrorResponse
      return data.message || data.error || 'An error occurred'
    } else if (error.request) {
      return 'Network error: Unable to connect to server'
    }
  }

  if (error instanceof Error) {
    return error.message
  }

  if (typeof error === 'string') {
    return error
  }

  return 'An unknown error occurred'
}

/**
 * Show user-friendly error message
 */
export function showError(error: unknown): string {
  const message = getErrorMessage(error)

  // Map common errors to user-friendly messages
  const errorMap: Record<string, string> = {
    'Network error': '无法连接到服务器，请检查网络连接',
    'text must be 1-5000 characters': '文本长度必须在1-5000字符之间',
    'Text contains path traversal patterns': '输入包含非法字符',
    'QueueFull': '任务队列已满，请稍后重试',
    'Task not found': '任务不存在',
    'TaskNotReady': '任务尚未完成',
  }

  for (const [key, value] of Object.entries(errorMap)) {
    if (message.includes(key)) {
      return value
    }
  }

  return message
}

// Import axios for type checking
import axios from 'axios'
