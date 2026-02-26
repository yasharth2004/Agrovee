"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { createPortal } from "react-dom"
import { motion, AnimatePresence } from "framer-motion"
import { X, Mic, Volume2, VolumeX, Bot } from "lucide-react"

interface VoiceChatOverlayProps {
  open: boolean
  onClose: () => void
  /** Send a message and get a response. Return the assistant's reply text. */
  onSend: (message: string) => Promise<string>
  /** Whether the parent is currently loading a response */
  loading?: boolean
}

type VoiceState = "idle" | "listening" | "processing" | "speaking"

export function VoiceChatOverlay({ open, onClose, onSend, loading }: VoiceChatOverlayProps) {
  const [voiceState, setVoiceState] = useState<VoiceState>("idle")
  const [transcript, setTranscript] = useState("")
  const [response, setResponse] = useState("")
  const [ttsEnabled, setTtsEnabled] = useState(true)
  const [supported, setSupported] = useState(false)

  const recognitionRef = useRef<any>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)
  const activeRef = useRef(false) // track if overlay is active to avoid stale closures

  // Initialize speech APIs
  useEffect(() => {
    if (typeof window === "undefined") return

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    setSupported(!!SpeechRecognition)

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = true
      recognition.lang = "en-US"
      recognition.maxAlternatives = 1

      recognition.onresult = (event: any) => {
        let interimTranscript = ""
        let finalTranscript = ""
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const t = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += t
          } else {
            interimTranscript += t
          }
        }
        if (finalTranscript) {
          setTranscript(finalTranscript.trim())
          setVoiceState("processing")
        } else if (interimTranscript) {
          setTranscript(interimTranscript.trim())
        }
      }

      recognition.onerror = () => {
        if (activeRef.current) setVoiceState("idle")
      }

      recognition.onend = () => {
        // Will transition to processing if we got a transcript
      }

      recognitionRef.current = recognition
    }

    if ("speechSynthesis" in window) {
      synthRef.current = window.speechSynthesis
    }

    return () => {
      recognitionRef.current?.abort()
      synthRef.current?.cancel()
    }
  }, [])

  // When overlay opens, auto-start listening
  useEffect(() => {
    activeRef.current = open
    if (open) {
      setTranscript("")
      setResponse("")
      // Small delay so the overlay animation starts first
      const timer = setTimeout(() => startListening(), 400)
      return () => clearTimeout(timer)
    } else {
      recognitionRef.current?.abort()
      synthRef.current?.cancel()
      setVoiceState("idle")
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  // When state transitions to "processing", send the message
  useEffect(() => {
    if (voiceState === "processing" && transcript) {
      handleSend(transcript)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [voiceState])

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return
    synthRef.current?.cancel()
    setTranscript("")
    setResponse("")
    setVoiceState("listening")
    try {
      recognitionRef.current.start()
    } catch {
      // Already started
    }
  }, [])

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop()
  }, [])

  const speak = useCallback((text: string) => {
    if (!synthRef.current || !ttsEnabled) {
      setVoiceState("idle")
      return
    }
    synthRef.current.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = "en-US"
    utterance.rate = 1.0
    utterance.pitch = 1.0

    const voices = synthRef.current.getVoices()
    const preferred =
      voices.find((v) => v.lang.startsWith("en") && v.name.toLowerCase().includes("samantha")) ||
      voices.find((v) => v.lang.startsWith("en") && v.localService) ||
      voices.find((v) => v.lang.startsWith("en"))
    if (preferred) utterance.voice = preferred

    utterance.onstart = () => setVoiceState("speaking")
    utterance.onend = () => {
      if (activeRef.current) setVoiceState("idle")
    }
    utterance.onerror = () => {
      if (activeRef.current) setVoiceState("idle")
    }

    synthRef.current.speak(utterance)
  }, [ttsEnabled])

  const handleSend = async (text: string) => {
    try {
      const reply = await onSend(text)
      if (!activeRef.current) return
      setResponse(reply)
      speak(reply)
    } catch {
      if (!activeRef.current) return
      setResponse("Sorry, something went wrong. Tap the mic to try again.")
      setVoiceState("idle")
    }
  }

  const handleMicTap = () => {
    if (voiceState === "listening") {
      stopListening()
    } else if (voiceState === "speaking") {
      synthRef.current?.cancel()
      setVoiceState("idle")
      startListening()
    } else {
      startListening()
    }
  }

  const handleClose = () => {
    recognitionRef.current?.abort()
    synthRef.current?.cancel()
    setVoiceState("idle")
    onClose()
  }

  if (!supported) return null

  const overlay = (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
          className="fixed inset-0 z-[100] flex flex-col items-center justify-between bg-gradient-to-b from-gray-900 via-gray-950 to-black"
        >
          {/* Top bar */}
          <div className="flex w-full items-center justify-between px-6 py-4">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-emerald-400" />
              <span className="text-sm font-semibold text-white">Agrovee AI</span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setTtsEnabled(!ttsEnabled)}
                className="rounded-full p-2 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                title={ttsEnabled ? "Mute voice" : "Unmute voice"}
              >
                {ttsEnabled ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
              </button>
              <button
                onClick={handleClose}
                className="rounded-full p-2 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Center content */}
          <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
            {/* Status text */}
            <AnimatePresence mode="wait">
              {voiceState === "listening" && (
                <motion.div
                  key="listening"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mb-8"
                >
                  <p className="text-lg font-medium text-white/80">
                    {transcript || "Listening..."}
                  </p>
                  {transcript && (
                    <p className="mt-1 text-sm text-white/40">Keep speaking...</p>
                  )}
                </motion.div>
              )}

              {voiceState === "processing" && (
                <motion.div
                  key="processing"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mb-8"
                >
                  <p className="text-lg font-medium text-white/60">&quot;{transcript}&quot;</p>
                  <div className="mt-4 flex justify-center gap-1.5">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-400 [animation-delay:0ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-400 [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-400 [animation-delay:300ms]" />
                  </div>
                  <p className="mt-2 text-sm text-white/40">Thinking...</p>
                </motion.div>
              )}

              {(voiceState === "speaking" || (voiceState === "idle" && response)) && (
                <motion.div
                  key="response"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mb-8 max-h-[40vh] w-full max-w-lg overflow-y-auto"
                >
                  {transcript && (
                    <p className="mb-3 text-sm text-white/40">&quot;{transcript}&quot;</p>
                  )}
                  <div className="rounded-2xl bg-white/10 px-5 py-4 backdrop-blur-md">
                    <p className="text-left text-sm leading-relaxed text-white/90">{response}</p>
                  </div>
                  {voiceState === "idle" && (
                    <p className="mt-3 text-xs text-white/30">Tap mic to ask another question</p>
                  )}
                </motion.div>
              )}

              {voiceState === "idle" && !response && (
                <motion.div
                  key="idle"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mb-8"
                >
                  <p className="text-lg font-medium text-white/60">
                    Tap the mic to start speaking
                  </p>
                  <p className="mt-1 text-sm text-white/30">
                    Ask about your crop diagnosis, treatments, or farming advice
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Mic button */}
            <div className="relative">
              {/* Pulse rings when listening */}
              {voiceState === "listening" && (
                <>
                  <span className="absolute inset-0 animate-ping rounded-full bg-emerald-500/20" style={{ animationDuration: "1.5s" }} />
                  <span className="absolute -inset-3 animate-ping rounded-full bg-emerald-500/10" style={{ animationDuration: "2s" }} />
                </>
              )}
              {voiceState === "speaking" && (
                <>
                  <span className="absolute inset-0 animate-pulse rounded-full bg-blue-500/20" />
                </>
              )}
              <button
                onClick={handleMicTap}
                disabled={voiceState === "processing"}
                className={`relative z-10 flex h-20 w-20 items-center justify-center rounded-full shadow-2xl transition-all duration-300 ${
                  voiceState === "listening"
                    ? "bg-emerald-500 scale-110 shadow-emerald-500/30"
                    : voiceState === "processing"
                    ? "bg-gray-600 cursor-wait"
                    : voiceState === "speaking"
                    ? "bg-blue-500 shadow-blue-500/30"
                    : "bg-white hover:scale-105 hover:shadow-white/20"
                }`}
              >
                <Mic
                  className={`h-8 w-8 transition-colors ${
                    voiceState === "idle" ? "text-gray-900" : "text-white"
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Bottom hint */}
          <div className="px-6 pb-8">
            <p className="text-xs text-white/20">
              {voiceState === "listening"
                ? "Speak clearly • Tap mic to stop"
                : voiceState === "speaking"
                ? "Tap mic to interrupt and ask again"
                : "Voice powered by Web Speech API"}
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )

  if (typeof document === "undefined") return null
  return createPortal(overlay, document.body)
}
