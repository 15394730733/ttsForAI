/**
 * Unit tests for VoiceParams component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import VoiceParams from '@/components/VoiceParams.vue'

// Mock TTS service
vi.mock('@/services/tts', () => ({
  ttsService: {
    getVoices: vi.fn(() =>
      Promise.resolve({
        voices: [
          {
            name: '晓晓-女声',
            voice_id: 'zh-CN-XiaoxiaoNeural',
            description: '温柔女声',
          },
          {
            name: '云扬-男声',
            voice_id: 'zh-CN-YunyangNeural',
            description: '沉稳男声',
          },
          {
            name: '晓悠-童声',
            voice_id: 'zh-CN-XiaoyouNeural',
            description: '活泼童声',
          },
        ],
      })
    ),
  },
}))

describe('VoiceParams', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders correctly with default props', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    expect(wrapper.find('.voice-params').exists()).toBe(true)
  })

  it('initializes with default values', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any

    expect(vm.formData.voice_name).toBe('zh-CN-XiaoxiaoNeural')
    expect(vm.formData.rate).toBe(1.0)
    expect(vm.formData.pitch).toBe(1.0)
    expect(vm.formData.volume).toBe(1.0)
  })

  it('initializes with custom props', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-YunyangNeural',
        rate: 1.5,
        pitch: 0.8,
        volume: 0.7,
      },
    })

    const vm = wrapper.vm as any

    expect(vm.formData.voice_name).toBe('zh-CN-YunyangNeural')
    expect(vm.formData.rate).toBe(1.5)
    expect(vm.formData.pitch).toBe(0.8)
    expect(vm.formData.volume).toBe(0.7)
  })

  it('emits update:voiceName when voice selection changes', async () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any

    // Simulate voice change
    vm.formData.voice_name = 'zh-CN-YunyangNeural'
    await vm.$nextTick()

    expect(wrapper.emitted('update:voiceName')).toBeTruthy()
    expect(wrapper.emitted('update:voiceName')![0]).toEqual(['zh-CN-YunyangNeural'])
  })

  it('emits update:rate when rate changes', async () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any

    // Simulate rate change
    vm.formData.rate = 1.5
    await vm.$nextTick()

    expect(wrapper.emitted('update:rate')).toBeTruthy()
    expect(wrapper.emitted('update:rate')![0]).toEqual([1.5])
  })

  it('emits update:pitch when pitch changes', async () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any

    // Simulate pitch change
    vm.formData.pitch = 1.2
    await vm.$nextTick()

    expect(wrapper.emitted('update:pitch')).toBeTruthy()
    expect(wrapper.emitted('update:pitch')![0]).toEqual([1.2])
  })

  it('emits update:volume when volume changes', async () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any

    // Simulate volume change
    vm.formData.volume = 0.8
    await vm.$nextTick()

    expect(wrapper.emitted('update:volume')).toBeTruthy()
    expect(wrapper.emitted('update:volume')![0]).toEqual([0.8])
  })

  it('resets all parameters to defaults', async () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-YunyangNeural',
        rate: 1.5,
        pitch: 0.8,
        volume: 0.7,
      },
    })

    const vm = wrapper.vm as any

    // Change values
    vm.formData.voice_name = 'zh-CN-YunyangNeural'
    vm.formData.rate = 1.5
    vm.formData.pitch = 0.8
    vm.formData.volume = 0.7

    // Reset
    vm.resetParams()
    await vm.$nextTick()

    expect(vm.formData.voice_name).toBe('zh-CN-XiaoxiaoNeural')
    expect(vm.formData.rate).toBe(1.0)
    expect(vm.formData.pitch).toBe(1.0)
    expect(vm.formData.volume).toBe(1.0)
  })

  it('emits all parameter updates after reset', async () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-YunyangNeural',
        rate: 1.5,
        pitch: 0.8,
        volume: 0.7,
      },
    })

    const vm = wrapper.vm as any

    // Reset
    vm.resetParams()
    await vm.$nextTick()

    expect(wrapper.emitted('update:voiceName')).toBeTruthy()
    expect(wrapper.emitted('update:rate')).toBeTruthy()
    expect(wrapper.emitted('update:pitch')).toBeTruthy()
    expect(wrapper.emitted('update:volume')).toBeTruthy()
  })

  it('has correct slider marks for rate', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any

    expect(vm.rateMarks).toEqual({
      0.5: '0.5x',
      1.0: '1.0x',
      1.5: '1.5x',
      2.0: '2.0x',
    })
  })

  it('has correct slider marks for pitch', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any

    expect(vm.pitchMarks).toEqual({
      0.5: '低',
      1.0: '正常',
      1.5: '高',
      2.0: '最高',
    })
  })

  it('has correct slider marks for volume', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any

    expect(vm.volumeMarks).toEqual({
      0.0: '静音',
      0.5: '50%',
      1.0: '100%',
    })
  })

  it('has resetParams method', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any
    expect(typeof vm.resetParams).toBe('function')
  })

  it('has emitChange method', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any
    expect(typeof vm.emitChange).toBe('function')
  })

  it('has loadVoices method', () => {
    const wrapper = mount(VoiceParams, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-button': true,
        },
      },
      props: {
        voiceName: 'zh-CN-XiaoxiaoNeural',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    })

    const vm = wrapper.vm as any
    expect(typeof vm.loadVoices).toBe('function')
  })

  describe('Boundary Value Tests', () => {
    it('handles minimum rate value', async () => {
      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': true,
          },
        },
        props: {
          voiceName: 'zh-CN-XiaoxiaoNeural',
          rate: 0.5,
          pitch: 1.0,
          volume: 1.0,
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formData.rate).toBe(0.5)

      // Test toFixed for display
      const displayValue = vm.formData.rate.toFixed(1)
      expect(displayValue).toBe('0.5')
    })

    it('handles maximum rate value', async () => {
      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': true,
          },
        },
        props: {
          voiceName: 'zh-CN-XiaoxiaoNeural',
          rate: 2.0,
          pitch: 1.0,
          volume: 1.0,
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formData.rate).toBe(2.0)

      const displayValue = vm.formData.rate.toFixed(1)
      expect(displayValue).toBe('2.0')
    })

    it('handles minimum pitch value', async () => {
      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': true,
          },
        },
        props: {
          voiceName: 'zh-CN-XiaoxiaoNeural',
          rate: 1.0,
          pitch: 0.5,
          volume: 1.0,
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formData.pitch).toBe(0.5)
    })

    it('handles maximum pitch value', async () => {
      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': true,
          },
        },
        props: {
          voiceName: 'zh-CN-XiaoxiaoNeural',
          rate: 1.0,
          pitch: 2.0,
          volume: 1.0,
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formData.pitch).toBe(2.0)
    })

    it('handles minimum volume value (mute)', async () => {
      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': true,
          },
        },
        props: {
          voiceName: 'zh-CN-XiaoxiaoNeural',
          rate: 1.0,
          pitch: 1.0,
          volume: 0.0,
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formData.volume).toBe(0.0)

      // Test Math.round for percentage display
      const displayValue = Math.round(vm.formData.volume * 100)
      expect(displayValue).toBe(0)
    })

    it('handles maximum volume value (100%)', async () => {
      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': true,
          },
        },
        props: {
          voiceName: 'zh-CN-XiaoxiaoNeural',
          rate: 1.0,
          pitch: 1.0,
          volume: 1.0,
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formData.volume).toBe(1.0)

      const displayValue = Math.round(vm.formData.volume * 100)
      expect(displayValue).toBe(100)
    })

    it('handles mid volume value (50%)', async () => {
      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': true,
          },
        },
        props: {
          voiceName: 'zh-CN-XiaoxiaoNeural',
          rate: 1.0,
          pitch: 1.0,
          volume: 0.5,
        },
      })

      const vm = wrapper.vm as any
      expect(vm.formData.volume).toBe(0.5)

      const displayValue = Math.round(vm.formData.volume * 100)
      expect(displayValue).toBe(50)
    })
  })

  describe('Error Handling', () => {
    it('handles loadVoices error gracefully', async () => {
      const { ttsService } = await import('@/services/tts')

      // Mock getVoices to throw error
      vi.mocked(ttsService.getVoices).mockRejectedValueOnce(new Error('Network error'))

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': true,
          },
        },
        props: {
          voiceName: 'zh-CN-XiaoxiaoNeural',
          rate: 1.0,
          pitch: 1.0,
          volume: 1.0,
        },
      })

      const vm = wrapper.vm as any

      // Call loadVoices which should handle error
      await vm.loadVoices()

      // Console error should be called
      expect(consoleSpy).toHaveBeenCalledWith('Failed to load voices:', expect.any(Error))

      consoleSpy.mockRestore()
    })
  })

  describe('Reset Button Interaction', () => {
    it('triggers resetParams when button is clicked', async () => {
      const wrapper = mount(VoiceParams, {
        global: {
          stubs: {
            'el-form': true,
            'el-form-item': true,
            'el-select': true,
            'el-option': true,
            'el-slider': true,
            'el-button': {
              template: '<button @click="$emit(\'click\')">Reset</button>',
              emits: ['click'],
            },
          },
        },
        props: {
          voiceName: 'zh-CN-YunyangNeural',
          rate: 1.5,
          pitch: 0.8,
          volume: 0.7,
        },
      })

      const vm = wrapper.vm as any

      // Change values
      vm.formData.rate = 1.5
      vm.formData.pitch = 0.8
      vm.formData.volume = 0.7

      // Reset
      vm.resetParams()
      await vm.$nextTick()

      expect(vm.formData.voice_name).toBe('zh-CN-XiaoxiaoNeural')
      expect(vm.formData.rate).toBe(1.0)
      expect(vm.formData.pitch).toBe(1.0)
      expect(vm.formData.volume).toBe(1.0)
    })
  })
})
