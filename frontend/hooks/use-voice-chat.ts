"use client"

import { useState, useRef, useCallback, useEffect } from "react"

interface UseVoiceChatOptions {
  /** Called when speech recognition produces a final transcript */
  onTranscript?: (text: string) => void
  /** Language for recognition (default: "en-US") */
  lang?: string
  /** Auto-speak assistant responses (default: true) */
  autoSpeak?: boolean
}

interface UseVoiceChatReturn {
  /** Whether the browser supports speech APIs */
  supported: boolean
  /** Whether the mic is currently listening */
  isListening: boolean
  /** Whether TTS is currently speaking */
  isSpeaking: boolean
  /** Whether TTS auto-read is enabled */
  ttsEnabled: boolean
  /** Start listening for voice input */
  startListening: () => void
  /** Stop listening */
  stopListening: () => void
  /** Toggle mic on/off */
  toggleListening: () => void
  /** Read text aloud */
  speak: (text: string) => void
  /** Stop speaking */
  stopSpeaking: () => void
  /** Toggle TTS on/off */
  toggleTts: () => void
}

// Extend Window for SpeechRecognition
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList
  resultIndex: number
}

export function useVoiceChat(options: UseVoiceChatOptions = {}): UseVoiceChatReturn {
  const { onTranscript, lang = "en-US", autoSpeak = true } = options

  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [ttsEnabled, setTtsEnabled] = useState(autoSpeak)
  const [supported, setSupported] = useState(false)

  const recognitionRef = useRef<any>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)
  const onTranscriptRef = useRef(onTranscript)

  // Keep callback ref in sync
  useEffect(() => {
    onTranscriptRef.current = onTranscript
  }, [onTranscript])

  // Check browser support on mount
  useEffect(() => {
    if (typeof window === "undefined") return

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    const hasSpeech = !!SpeechRecognition
    const hasSynth = "speechSynthesis" in window

    setSupported(hasSpeech || hasSynth)

    if (hasSpeech) {
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = lang
      recognition.maxAlternatives = 1

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0]?.[0]?.transcript?.trim()
        if (transcript && onTranscriptRef.current) {
          onTranscriptRef.current(transcript)
        }
      }

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition error:", event.error)
        setIsListening(false)
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognitionRef.current = recognition
    }

    if (hasSynth) {
      synthRef.current = window.speechSynthesis
    }

    return () => {
      recognitionRef.current?.abort()
      synthRef.current?.cancel()
    }
  }, [lang])

  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return
    // Stop any ongoing TTS so mic doesn't pick it up
    synthRef.current?.cancel()
    setIsSpeaking(false)
    try {
      recognitionRef.current.start()
      setIsListening(true)
    } catch (e) {
      console.warn("Failed to start recognition:", e)
    }
  }, [isListening])

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return
    recognitionRef.current.stop()
    setIsListening(false)
  }, [])

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }, [isListening, startListening, stopListening])

  const speak = useCallback((text: string) => {
    if (!synthRef.current || !ttsEnabled) return
    // Cancel any in-progress speech
    synthRef.current.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang
    utterance.rate = 1.0
    utterance.pitch = 1.0

    // Try to pick a natural-sounding English voice
    const voices = synthRef.current.getVoices()
    const preferred = voices.find(
      (v) => v.lang.startsWith("en") && v.name.toLowerCase().includes("samantha")
    ) || voices.find(
      (v) => v.lang.startsWith("en") && v.localService
    ) || voices.find(
      (v) => v.lang.startsWith("en")
    )
    if (preferred) utterance.voice = preferred

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    synthRef.current.speak(utterance)
  }, [lang, ttsEnabled])

  const stopSpeaking = useCallback(() => {
    synthRef.current?.cancel()
    setIsSpeaking(false)
  }, [])

  const toggleTts = useCallback(() => {
    setTtsEnabled((prev) => {
      if (prev) {
        // Turning off — stop any current speech
        synthRef.current?.cancel()
        setIsSpeaking(false)
      }
      return !prev
    })
  }, [])

  return {
    supported,
    isListening,
    isSpeaking,
    ttsEnabled,
    startListening,
    stopListening,
    toggleListening,
    speak,
    stopSpeaking,
    toggleTts,
  }
}
