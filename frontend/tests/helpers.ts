/**
 * Test helpers for Vue components.
 */
import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'

// Global register Element Plus components for testing
config.global.plugins = [ElementPlus]
