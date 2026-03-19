"use client"

import { useState, useRef, useCallback, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Camera,
  Upload,
  X,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  Leaf,
  Droplets,
  Thermometer,
  Wind,
  FileText,
  ChevronDown,
  ChevronUp,
  Image as ImageIcon,
  MessageCircle,
  Send,
  Bot,
  User,
  Minimize2,
  Maximize2,
  Mic,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { diagnosisAPI, chatAPI, type DiagnosisResponse } from "@/lib/api"
import { VoiceChatOverlay } from "@/components/voice-chat-overlay"

/** Format disease names: "Apple___Apple_Scab" → "Apple Scab" */
function formatDisease(name: string | null | undefined): string {
  if (!name) return "Unknown"
  // Split on ___ to get disease part
  let disease = name
  if (name.includes("___")) {
    disease = name.split("___")[1]
  }
  // Clean up: remove underscores, trailing underscores, extra spaces
  return disease
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    // Title-case each word
    .split(" ")
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ")
}

/** Format crop name: "Corn_(maize)" → "Corn", "Pepper,_bell" → "Bell Pepper", "Cherry_(including_sour)" → "Cherry" */
function formatCrop(name: string | null | undefined): string {
  if (!name) return ""
  // Strip parenthetical suffixes like _(maize), _(including_sour)
  let crop = name.replace(/[_(].*\)/, "").replace(/,_/g, " ").replace(/_/g, " ").trim()
  // Title-case
  crop = crop.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ")
  // Special mappings for readability
  const cleanMap: Record<string, string> = {
    "Corn": "Corn (Maize)",
    "Pepper Bell": "Bell Pepper",
    "Pepper, Bell": "Bell Pepper",
    "Cherry": "Cherry",
  }
  return cleanMap[crop] || crop
}

type UploadState = "idle" | "preview" | "uploading" | "result"

export default function DiagnosePage() {
  const [state, setState] = useState<UploadState>("idle")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [soilType, setSoilType] = useState("")
  const [location, setLocation] = useState("")
  const [season, setSeason] = useState("")
  const [result, setResult] = useState<DiagnosisResponse | null>(null)
  const [error, setError] = useState("")
  const [showDetails, setShowDetails] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Chat widget state
  const [chatOpen, setChatOpen] = useState(false)
  const [chatMessages, setChatMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([])
  const [chatInput, setChatInput] = useState("")
  const [chatLoading, setChatLoading] = useState(false)
  const [chatSessionId, setChatSessionId] = useState<number | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const [voiceOpen, setVoiceOpen] = useState(false)

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [chatMessages, chatLoading])

  /** Send a voice message — used by the voice overlay */
  async function handleVoiceSend(message: string): Promise<string> {
    // Add user message to chat history
    setChatMessages((prev) => [...prev, { role: "user", content: message }])

    const context = buildDiagnosisContext()
    const res = await chatAPI.sendMessage(message, chatSessionId || undefined, context)
    const data = res.data
    if (data.session_id && !chatSessionId) {
      setChatSessionId(data.session_id)
    }
    // Add assistant message to chat history
    setChatMessages((prev) => [
      ...prev,
      { role: "assistant", content: data.content },
    ])
    return data.content
  }

  /** Build context object from current diagnosis result */
  function buildDiagnosisContext() {
    if (!result) return {}
    return {
      crop: result.crop_type || "",
      disease: result.predicted_disease || "",
      confidence: result.confidence_score,
      risk: result.risk_assessment || "",
      weather: result.weather_data
        ? `${result.weather_data.temperature?.toFixed(0)}°C, ${result.weather_data.humidity?.toFixed(0)}% humidity, ${result.weather_data.wind_speed?.toFixed(1)} m/s wind`
        : "",
      treatments:
        result.recommendations?.treatments
          ?.map((t: any) => t.name || t.type || "")
          .filter(Boolean)
          .join(", ") || "",
      prevention:
        result.recommendations?.prevention?.join("; ") || "",
    }
  }

  /** Send a chat message with diagnosis context */
  async function handleChatSend() {
    const msg = chatInput.trim()
    if (!msg || chatLoading) return

    setChatInput("")
    setChatMessages((prev) => [...prev, { role: "user", content: msg }])
    setChatLoading(true)

    try {
      const context = buildDiagnosisContext()
      const res = await chatAPI.sendMessage(msg, chatSessionId || undefined, context)
      const data = res.data
      if (data.session_id && !chatSessionId) {
        setChatSessionId(data.session_id)
      }
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.content },
      ])
    } catch {
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I couldn't process your question. Please try again.",
        },
      ])
    } finally {
      setChatLoading(false)
    }
  }

  const handleFileSelect = useCallback((file: File) => {
    if (!file.type.startsWith("image/")) {
      setError("Please select an image file (JPG, PNG)")
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File too large. Maximum size is 10MB")
      return
    }
    setError("")
    setSelectedFile(file)
    setPreview(URL.createObjectURL(file))
    setState("preview")
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      const file = e.dataTransfer.files[0]
      if (file) handleFileSelect(file)
    },
    [handleFileSelect]
  )

  const handleUpload = async () => {
    if (!selectedFile) return
    setState("uploading")
    setError("")

    const formData = new FormData()
    formData.append("image", selectedFile)
    if (soilType) formData.append("soil_type", soilType)
    if (location) formData.append("location", location)
    if (season) formData.append("season", season)

    try {
      const res = await diagnosisAPI.create(formData)
      setResult(res.data)
      setState("result")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Diagnosis failed. Please try again.")
      setState("preview")
    }
  }

  const reset = () => {
    setState("idle")
    setSelectedFile(null)
    setPreview(null)
    setResult(null)
    setError("")
    setSoilType("")
    setLocation("")
    setSeason("")
    setShowDetails(false)
    // Reset chat
    setChatOpen(false)
    setChatMessages([])
    setChatInput("")
    setChatSessionId(null)
  }

  const riskColor = (risk: string | null) => {
    switch (risk) {
      case "CRITICAL":
        return "bg-red-100 text-red-700 border-red-200"
      case "HIGH":
        return "bg-orange-100 text-orange-700 border-orange-200"
      case "MEDIUM":
        return "bg-amber-100 text-amber-700 border-amber-200"
      case "LOW":
        return "bg-green-100 text-green-700 border-green-200"
      default:
        return "bg-gray-100 text-gray-700 border-gray-200"
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold text-foreground">
          Crop Disease Diagnosis
        </h1>
        <p className="mt-1 text-muted-foreground">
          Upload a photo of your crop leaf for instant AI-powered disease detection.
        </p>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* IDLE STATE - Drag & Drop */}
        {state === "idle" && (
          <motion.div
            key="idle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="group cursor-pointer rounded-2xl border-2 border-dashed border-border/80 bg-card/50 p-12 text-center transition-all hover:border-primary/50 hover:bg-primary/5"
            >
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 transition-transform group-hover:scale-110">
                <Upload className="h-7 w-7 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">
                Upload Crop Image
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Drag & drop or click to select a photo of your crop leaf
              </p>
              <p className="mt-1 text-xs text-muted-foreground/70">
                Supports JPG, PNG (max 10MB)
              </p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/jpg"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleFileSelect(file)
              }}
            />
          </motion.div>
        )}

        {/* PREVIEW STATE */}
        {state === "preview" && preview && (
          <motion.div
            key="preview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="overflow-hidden rounded-2xl border border-border/60 bg-card shadow-sm">
              <div className="relative aspect-video w-full bg-muted">
                <img
                  src={preview}
                  alt="Selected crop"
                  className="h-full w-full object-contain"
                />
                <button
                  onClick={reset}
                  className="absolute right-3 top-3 rounded-full bg-black/50 p-1.5 text-white backdrop-blur-sm hover:bg-black/70"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="p-5">
                <h3 className="mb-4 text-sm font-semibold text-foreground">
                  Optional: Add Environmental Context
                </h3>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="space-y-2">
                    <Label className="text-xs">Soil Type</Label>
                    <Select value={soilType} onValueChange={setSoilType}>
                      <SelectTrigger className="h-9">
                        <SelectValue placeholder="Select..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="clay">Clay</SelectItem>
                        <SelectItem value="sandy">Sandy</SelectItem>
                        <SelectItem value="loamy">Loamy</SelectItem>
                        <SelectItem value="silt">Silt</SelectItem>
                        <SelectItem value="peaty">Peaty</SelectItem>
                        <SelectItem value="chalky">Chalky</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-xs">Location</Label>
                    <Input
                      placeholder="City or region"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="h-9"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="text-xs">Season</Label>
                    <Select value={season} onValueChange={setSeason}>
                      <SelectTrigger className="h-9">
                        <SelectValue placeholder="Select..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="spring">Spring</SelectItem>
                        <SelectItem value="summer">Summer</SelectItem>
                        <SelectItem value="monsoon">Monsoon</SelectItem>
                        <SelectItem value="autumn">Autumn</SelectItem>
                        <SelectItem value="winter">Winter</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </div>

            {error && (
              <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <div className="flex gap-3">
              <Button variant="outline" className="flex-1" onClick={reset}>
                Cancel
              </Button>
              <Button className="flex-1 gap-2" onClick={handleUpload}>
                <Camera className="h-4 w-4" />
                Analyze Image
              </Button>
            </div>
          </motion.div>
        )}

        {/* UPLOADING STATE */}
        {state === "uploading" && (
          <motion.div
            key="uploading"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center rounded-2xl border border-border/60 bg-card py-16 text-center shadow-sm"
          >
            <div className="relative mb-6">
              <div className="h-16 w-16 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />
              <Leaf className="absolute left-1/2 top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 text-primary" />
            </div>
            <h3 className="text-lg font-semibold text-foreground">
              Analyzing your crop...
            </h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Our AI is processing your image with multimodal analysis.
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2 text-xs text-muted-foreground">
              <span className="rounded-full bg-muted px-3 py-1">
                🔍 Vision Analysis
              </span>
              <span className="rounded-full bg-muted px-3 py-1">
                🌤️ Weather Context
              </span>
              <span className="rounded-full bg-muted px-3 py-1">
                🧬 Multimodal Fusion
              </span>
              <span className="rounded-full bg-muted px-3 py-1">
                💊 Treatment Plan
              </span>
            </div>
          </motion.div>
        )}

        {/* RESULT STATE */}
        {state === "result" && result && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            {/* Main result card */}
            <div className="overflow-hidden rounded-2xl border border-border/60 bg-card shadow-sm">
              <div className="grid md:grid-cols-2">
                {/* Image side */}
                <div className="relative aspect-square bg-muted md:aspect-auto">
                  {preview && (
                    <img
                      src={preview}
                      alt="Analyzed crop"
                      className="h-full w-full object-cover"
                    />
                  )}
                  <div className="absolute bottom-3 left-3 right-3 flex flex-wrap gap-2">
                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-semibold backdrop-blur-md ${riskColor(
                        result.risk_assessment
                      )}`}
                    >
                      {result.risk_assessment || "N/A"} Risk
                    </span>
                    <span className="rounded-full border border-white/20 bg-black/50 px-3 py-1 text-xs font-semibold text-white backdrop-blur-md">
                      {result.status}
                    </span>
                  </div>
                </div>

                {/* Result side */}
                <div className="p-6">
                  <div className="mb-4 flex items-start gap-3">
                    {result.predicted_disease
                      ?.toLowerCase()
                      .includes("healthy") ? (
                      <CheckCircle2 className="mt-0.5 h-6 w-6 text-green-600" />
                    ) : (
                      <AlertTriangle className="mt-0.5 h-6 w-6 text-amber-600" />
                    )}
                    <div>
                      <h2 className="font-heading text-xl font-bold text-foreground">
                        {formatDisease(result.predicted_disease)}
                      </h2>
                      {result.crop_type && (
                        <p className="text-sm text-muted-foreground">
                          Crop: {formatCrop(result.crop_type)}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Confidence */}
                  <div className="mb-5 space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">
                        AI Confidence
                      </span>
                      <span className="font-semibold text-foreground">
                        {result.confidence_score
                          ? `${result.confidence_score.toFixed(1)}%`
                          : "N/A"}
                      </span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{
                          width: `${Math.min(result.confidence_score ?? 0, 100)}%`,
                        }}
                      />
                    </div>
                    {result.fusion_confidence != null && (
                      <p className="text-xs text-muted-foreground">
                        Multimodal fusion confidence:{" "}
                        {result.fusion_confidence.toFixed(1)}%
                      </p>
                    )}
                  </div>

                  {/* Weather data */}
                  {result.weather_data && (
                    <div className="mb-5 rounded-lg bg-muted/50 p-3">
                      <p className="mb-2 text-xs font-semibold text-muted-foreground">
                        Weather Conditions
                      </p>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className="flex items-center gap-1">
                          <Thermometer className="h-3 w-3 text-orange-500" />
                          <span>
                            {result.weather_data.temperature?.toFixed(0)}°C
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Droplets className="h-3 w-3 text-blue-500" />
                          <span>
                            {result.weather_data.humidity?.toFixed(0)}%
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Wind className="h-3 w-3 text-teal-500" />
                          <span>
                            {result.weather_data.wind_speed?.toFixed(1)} m/s
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Top predictions toggle */}
                  {result.all_predictions && result.all_predictions.length > 0 && (
                    <button
                      onClick={() => setShowDetails(!showDetails)}
                      className="flex w-full items-center justify-between rounded-lg border border-border/60 px-3 py-2 text-sm text-muted-foreground hover:bg-muted"
                    >
                      <span>All Predictions</span>
                      {showDetails ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </button>
                  )}

                  <AnimatePresence>
                    {showDetails && result.all_predictions && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="mt-2 space-y-1 overflow-hidden"
                      >
                        {result.all_predictions.map((p: any, i: number) => (
                          <div
                            key={i}
                            className="flex items-center justify-between rounded px-3 py-1.5 text-xs"
                          >
                            <span className="text-foreground">
                              {formatDisease(p.disease || p.class_name || `Class ${i}`)}
                              <span className="ml-1.5 text-muted-foreground/60">
                                ({formatCrop(p.crop || (p.disease || "").split("___")[0])})
                              </span>
                            </span>
                            <span className="font-mono text-muted-foreground">
                              {(p.probability || p.confidence || 0).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {result.recommendations && (
              <div className="rounded-2xl border border-border/60 bg-card p-6 shadow-sm">
                <div className="mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  <h3 className="font-heading text-lg font-semibold text-foreground">
                    Treatment Recommendations
                  </h3>
                </div>

                {result.recommendations.treatments && (
                  <div className="space-y-3">
                    {(result.recommendations.treatments as any[]).map(
                      (t: any, i: number) => (
                        <div
                          key={i}
                          className="rounded-lg border border-border/40 bg-muted/30 p-4"
                        >
                          <h4 className="text-sm font-semibold text-foreground">
                            {t.name || t.type || `Treatment ${i + 1}`}
                          </h4>
                          <p className="mt-1 text-sm text-muted-foreground">
                            {t.description || t.details || "Follow recommended agricultural practices."}
                          </p>
                          {t.products && (
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {(t.products as string[]).map((p, j) => (
                                <span
                                  key={j}
                                  className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
                                >
                                  {p}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      )
                    )}
                  </div>
                )}

                {result.recommendations.prevention && (
                  <div className="mt-4">
                    <h4 className="mb-2 text-sm font-semibold text-foreground">
                      Prevention Tips
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {(result.recommendations.prevention as string[]).map(
                        (tip, i) => (
                          <li key={i} className="flex gap-2">
                            <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-green-500" />
                            {tip}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <Button onClick={reset} variant="outline" className="w-full gap-2">
              <Camera className="h-4 w-4" />
              Analyze Another Image
            </Button>

            {/* ── Diagnosis Chatbot Widget ── */}
            <div className="overflow-hidden rounded-2xl border border-border/60 bg-card shadow-sm">
              {/* Chat header - always visible */}
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="flex w-full items-center justify-between p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10">
                    <MessageCircle className="h-4.5 w-4.5 text-primary" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-sm font-semibold text-foreground">
                      Ask Agrovee AI
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      Ask follow-up questions about this diagnosis
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {chatOpen ? (
                    <Minimize2 className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Maximize2 className="h-4 w-4 text-muted-foreground" />
                  )}
                </div>
              </button>

              <AnimatePresence>
                {chatOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    className="overflow-hidden"
                  >
                    <div className="border-t border-border/40">
                      {/* Messages area */}
                      <div className="h-72 overflow-y-auto p-4 space-y-3">
                        {chatMessages.length === 0 && (
                          <div className="flex h-full flex-col items-center justify-center text-center">
                            <Bot className="mb-3 h-10 w-10 text-muted-foreground/40" />
                            <p className="text-sm font-medium text-muted-foreground">
                              Ask anything about your diagnosis
                            </p>
                            <div className="mt-3 flex flex-wrap justify-center gap-1.5">
                              {[
                                `How do I treat ${formatDisease(result.predicted_disease)}?`,
                                "What caused this disease?",
                                "Is my crop salvageable?",
                              ].map((q) => (
                                <button
                                  key={q}
                                  onClick={() => {
                                    setChatInput(q)
                                  }}
                                  className="rounded-full border border-border/60 bg-muted/50 px-3 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                                >
                                  {q}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}

                        {chatMessages.map((msg, i) => (
                          <div
                            key={i}
                            className={`flex gap-2 ${
                              msg.role === "user" ? "justify-end" : "justify-start"
                            }`}
                          >
                            {msg.role === "assistant" && (
                              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-primary/10">
                                <Bot className="h-3.5 w-3.5 text-primary" />
                              </div>
                            )}
                            <div
                              className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
                                msg.role === "user"
                                  ? "bg-primary text-primary-foreground"
                                  : "bg-muted text-foreground"
                              }`}
                            >
                              {msg.content}
                            </div>
                            {msg.role === "user" && (
                              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-muted">
                                <User className="h-3.5 w-3.5 text-muted-foreground" />
                              </div>
                            )}
                          </div>
                        ))}

                        {chatLoading && (
                          <div className="flex gap-2">
                            <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-primary/10">
                              <Bot className="h-3.5 w-3.5 text-primary" />
                            </div>
                            <div className="rounded-2xl bg-muted px-4 py-2.5">
                              <div className="flex gap-1">
                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground/50 [animation-delay:0ms]" />
                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground/50 [animation-delay:150ms]" />
                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground/50 [animation-delay:300ms]" />
                              </div>
                            </div>
                          </div>
                        )}
                        <div ref={chatEndRef} />
                      </div>

                      {/* Chat input */}
                      <div className="border-t border-border/40 p-3">
                        <form
                          onSubmit={(e) => {
                            e.preventDefault()
                            handleChatSend()
                          }}
                          className="flex gap-2"
                        >
                          <Input
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            placeholder="Ask about this diagnosis..."
                            className="h-9 flex-1 text-sm"
                            disabled={chatLoading}
                          />
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            className="h-9 w-9 p-0"
                            onClick={() => setVoiceOpen(true)}
                            disabled={chatLoading}
                            title="Voice chat"
                          >
                            <Mic className="h-4 w-4" />
                          </Button>
                          <Button
                            type="submit"
                            size="sm"
                            className="h-9 w-9 p-0"
                            disabled={!chatInput.trim() || chatLoading}
                          >
                            <Send className="h-4 w-4" />
                          </Button>
                        </form>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Voice Chat Overlay */}
      <VoiceChatOverlay
        open={voiceOpen}
        onClose={() => setVoiceOpen(false)}
        onSend={handleVoiceSend}
        loading={chatLoading}
      />
    </div>
  )
}
