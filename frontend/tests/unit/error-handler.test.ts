/**
 * Error handling utility tests.
 */

import { describe, it, expect } from 'vitest'
import { showError, getErrorMessage, ApiError } from '@/utils/error-handler'

describe('Error Handler', () => {
  describe('getErrorMessage', () => {
    it('should extract message from Error object', () => {
      const error = new Error('Test error message')
      expect(getErrorMessage(error)).toBe('Test error message')
    })

    it('should handle string errors', () => {
      expect(getErrorMessage('String error')).toBe('String error')
    })

    it('should handle unknown errors', () => {
      expect(getErrorMessage(null)).toBe('An unknown error occurred')
      expect(getErrorMessage(undefined)).toBe('An unknown error occurred')
      expect(getErrorMessage(12345)).toBe('An unknown error occurred')
    })

    it('should extract message from Axios error with response', () => {
      const axiosError = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Server error message',
            error: 'ErrorType',
          },
        },
      }
      expect(getErrorMessage(axiosError)).toBe('Server error message')
    })

    it('should handle Axios error without response', () => {
      const axiosError = {
        isAxiosError: true,
        request: {},
      }
      expect(getErrorMessage(axiosError)).toBe('Network error: Unable to connect to server')
    })

    it('should handle Axios error with request only', () => {
      const axiosError = {
        isAxiosError: true,
        request: {},
        message: 'Request failed',
      }
      expect(getErrorMessage(axiosError)).toBe('Network error: Unable to connect to server')
    })
  })

  describe('showError', () => {
    it('should show user-friendly message for network errors', () => {
      const error = 'Network error: Unable to connect to server'
      expect(showError(error)).toBe('无法连接到服务器，请检查网络连接')
    })

    it('should show user-friendly message for text length error', () => {
      const error = 'text must be 1-5000 characters'
      expect(showError(error)).toBe('文本长度必须在1-5000字符之间')
    })

    it('should show user-friendly message for path traversal', () => {
      const error = 'Text contains path traversal patterns'
      expect(showError(error)).toBe('输入包含非法字符')
    })

    it('should show user-friendly message for queue full error', () => {
      const error = 'QueueFull'
      expect(showError(error)).toBe('任务队列已满，请稍后重试')
    })

    it('should show user-friendly message for task not found', () => {
      const error = 'Task not found'
      expect(showError(error)).toBe('任务不存在')
    })

    it('should show user-friendly message for task not ready', () => {
      const error = 'TaskNotReady'
      expect(showError(error)).toBe('任务尚未完成')
    })

    it('should return original message for unmapped errors', () => {
      const error = 'Some unmapped error message'
      expect(showError(error)).toBe('Some unmapped error message')
    })

    it('should handle Error objects', () => {
      const error = new Error('Network error: test')
      expect(showError(error)).toBe('无法连接到服务器，请检查网络连接')
    })
  })

  describe('ApiError', () => {
    it('should create ApiError with message', () => {
      const error = new ApiError('Test error')
      expect(error.message).toBe('Test error')
      expect(error.name).toBe('ApiError')
    })

    it('should create ApiError with status', () => {
      const error = new ApiError('Test error', 404)
      expect(error.status).toBe(404)
    })

    it('should create ApiError with details', () => {
      const details = { field: 'value' }
      const error = new ApiError('Test error', 500, details)
      expect(error.details).toEqual(details)
    })

    it('should handle ApiError without status', () => {
      const error = new ApiError('Test error')
      expect(error.status).toBeUndefined()
    })

    it('should handle ApiError without details', () => {
      const error = new ApiError('Test error', 500)
      expect(error.details).toBeUndefined()
    })
  })

  describe('Error Integration', () => {
    it('should handle Axios error with showError', () => {
      const axiosError = {
        isAxiosError: true,
        response: {
          data: {
            message: 'Network error: Connection timeout',
          },
        },
      }
      expect(showError(axiosError)).toBe('无法连接到服务器，请检查网络连接')
    })

    it('should handle multiple error types consistently', () => {
      const error1 = new Error('Network error: test')
      const error2 = 'Network error: test'
      const error3 = {
        isAxiosError: true,
        response: {
          data: { message: 'Network error: test' },
        },
      }

      expect(showError(error1)).toBe('无法连接到服务器，请检查网络连接')
      expect(showError(error2)).toBe('无法连接到服务器，请检查网络连接')
      expect(showError(error3)).toBe('无法连接到服务器，请检查网络连接')
    })

    it('should preserve error details in ApiError', () => {
      const details = {
        validation_errors: [
          { field: 'text', message: 'Text is required' },
          { field: 'voice', message: 'Invalid voice' },
        ],
      }
      const error = new ApiError('Validation failed', 422, details)
      expect(error.details).toEqual(details)
      expect(showError(error)).toBe('Validation failed')
    })
  })
})
