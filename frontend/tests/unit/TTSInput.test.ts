/**
 * Unit tests for TTSInput component.
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TTSInput from '@/components/TTSInput.vue'

describe('TTSInput', () => {
  it('renders correctly with initial value', () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: 'Hello world',
      },
    })

    expect(wrapper.find('textarea').element.value).toBe('Hello world')
    expect(wrapper.find('.char-count').text()).toBe('11 / 5000 字符')
  })

  it('updates modelValue when text changes', async () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: '',
      },
    })

    const textarea = wrapper.find('textarea')
    await textarea.setValue('New text')

    // Wait for watch to trigger
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['New text'])
  })

  it('displays character count correctly', async () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: '',
      },
    })

    const textarea = wrapper.find('textarea')

    // Test empty text
    expect(wrapper.find('.char-count span').text()).toBe('0 / 5000 字符')

    // Test with text
    await textarea.setValue('Hello')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.char-count span').text()).toBe('5 / 5000 字符')

    // Test with 5000 characters (max)
    const longText = 'a'.repeat(5000)
    await textarea.setValue(longText)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.char-count span').text()).toBe('5000 / 5000 字符')
  })

  it('shows error message when text exceeds limit', async () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: '',
      },
    })

    const textarea = wrapper.find('textarea')

    // Set text over limit
    const longText = 'a'.repeat(5001)
    await textarea.setValue(longText)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.char-count span').classes()).toContain('error')

    const alert = wrapper.find('.el-alert')
    expect(alert.exists()).toBe(true)
    expect(alert.text()).toContain('文本长度不能超过5000字符')
  })

  it('does not show error for valid length', async () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: '',
      },
    })

    const textarea = wrapper.find('textarea')

    // Valid length (1-5000)
    await textarea.setValue('Valid text')
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.char-count span').classes()).not.toContain('error')
    expect(wrapper.find('.el-alert').exists()).toBe(false)
  })

  it('computes isValidLength correctly', async () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: '',
      },
    })

    const textarea = wrapper.find('textarea')

    // Empty text - not valid
    expect(wrapper.vm.isValidLength).toBe(false)

    // Valid text
    await textarea.setValue('Hello')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.isValidLength).toBe(true)

    // Over limit - not valid
    await textarea.setValue('a'.repeat(5001))
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.isValidLength).toBe(false)
  })

  it('respects maxlength attribute', () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: '',
      },
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.attributes('maxlength')).toBe('5000')
  })

  it('updates internal state when modelValue prop changes', async () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: 'Initial',
      },
    })

    expect(wrapper.find('textarea').element.value).toBe('Initial')

    await wrapper.setProps({ modelValue: 'Updated' })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('textarea').element.value).toBe('Updated')
  })

  it('displays placeholder text correctly', () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: '',
      },
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.attributes('placeholder')).toBe('请输入要转换为语音的文字内容（1-5000字符）')
  })

  it('has correct number of rows', () => {
    const wrapper = mount(TTSInput, {
      props: {
        modelValue: '',
      },
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.attributes('rows')).toBe('8')
  })
})
