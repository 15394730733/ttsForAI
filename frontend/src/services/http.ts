/**
 * HTTP client configuration with Axios.
 *
 * Provides configured axios instance with interceptors for error handling
 * and request/response transformation.
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// Create axios instance
const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
http.interceptors.request.use(
  (config) => {
    // Add auth token if available (future)
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
http.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      const { status, data } = error.response

      // Server responded with error status
      switch (status) {
        case 400:
          console.error('Bad Request:', data?.message || 'Invalid request')
          break
        case 401:
          console.error('Unauthorized: Authentication required')
          // Future: redirect to login
          break
        case 403:
          console.error('Forbidden: Insufficient permissions')
          break
        case 404:
          console.error('Not Found:', data?.message || 'Resource not found')
          break
        case 422:
          console.error('Validation Error:', data?.details || 'Invalid input')
          break
        case 429:
          console.error('Too Many Requests:', data?.message || 'Rate limit exceeded')
          break
        case 500:
          console.error('Internal Server Error:', data?.message || 'Server error')
          break
        default:
          console.error(`HTTP Error ${status}:`, data?.message || 'Unknown error')
      }

      return Promise.reject({
        status,
        message: data?.message || data?.error || 'An error occurred',
        details: data?.details || null,
      })
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error: No response from server')
      return Promise.reject({
        message: 'Network error: Unable to connect to server',
        details: null,
      })
    } else {
      // Error setting up request
      console.error('Request Error:', error.message)
      return Promise.reject({
        message: error.message || 'Failed to make request',
        details: null,
      })
    }
  }
)

export default http
