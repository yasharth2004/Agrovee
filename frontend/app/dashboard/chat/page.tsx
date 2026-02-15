"use client"

import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Send,
  Plus,
  MessageSquare,
  Loader2,
  Trash2,
  Leaf,
  Bot,
  User as UserIcon,
  ChevronLeft,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  chatAPI,
  type ChatMessage,
  type ChatSession,
  type ChatSessionDetail,
} from "@/lib/api"

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [activeSession, setActiveSession] = useState<ChatSessionDetail | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [showSidebar, setShowSidebar] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    fetchSessions()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchSessions = async () => {
    setIsLoading(true)
    try {
      const res = await chatAPI.sessions()
      setSessions(res.data.sessions)
    } catch (err) {
      console.error("Failed to fetch sessions:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const loadSession = async (sessionId: number) => {
    try {
      const res = await chatAPI.session(sessionId)
      setActiveSession(res.data)
      setMessages(res.data.messages)
      setShowSidebar(false)
    } catch (err) {
      console.error("Failed to load session:", err)
    }
  }

  const startNewChat = () => {
    setActiveSession(null)
    setMessages([])
    setShowSidebar(false)
  }

  const deleteSession = async (sessionId: number) => {
    try {
      await chatAPI.deleteSession(sessionId)
      setSessions((prev) => prev.filter((s) => s.id !== sessionId))
      if (activeSession?.id === sessionId) {
        setActiveSession(null)
        setMessages([])
      }
    } catch (err) {
      console.error("Failed to delete session:", err)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isSending) return

    const content = input.trim()
    setInput("")
    setIsSending(true)

    // Optimistic add user message
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      session_id: activeSession?.id || 0,
      role: "user",
      content,
      sources: null,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempUserMsg])

    try {
      const res = await chatAPI.sendMessage(content, activeSession?.id || undefined)
      const assistantMsg = res.data

      // Update session id if new
      if (!activeSession) {
        setActiveSession({
          id: assistantMsg.session_id,
          user_id: 0,
          title: content.slice(0, 50),
          is_active: true,
          message_count: 2,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          messages: [],
        })
        fetchSessions()
      }

      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      console.error("Failed to send message:", err)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          session_id: activeSession?.id || 0,
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
          sources: null,
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const suggestedQuestions = [
    "What causes tomato leaf blight?",
    "How to prevent fungal diseases in rice?",
    "Best organic pesticides for small farms",
    "How does weather affect crop diseases?",
  ]

  return (
    <div className="flex h-[calc(100vh-theme(spacing.14)-theme(spacing.12))] lg:h-[calc(100vh-theme(spacing.16))] overflow-hidden rounded-xl border border-border/60 bg-card shadow-sm">
      {/* Sessions sidebar */}
      <AnimatePresence>
        {showSidebar && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="flex w-[280px] flex-shrink-0 flex-col border-r border-border/60 bg-card/50"
          >
            <div className="flex items-center justify-between border-b border-border/60 px-4 py-3">
              <h3 className="text-sm font-semibold text-foreground">
                Conversations
              </h3>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={startNewChat}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-2">
              {sessions.length === 0 ? (
                <div className="py-8 text-center text-xs text-muted-foreground">
                  No conversations yet
                </div>
              ) : (
                <div className="space-y-1">
                  {sessions.map((s) => (
                    <div
                      key={s.id}
                      className={`group flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                        activeSession?.id === s.id
                          ? "bg-primary/10 text-primary"
                          : "text-muted-foreground hover:bg-muted hover:text-foreground"
                      }`}
                      onClick={() => loadSession(s.id)}
                    >
                      <MessageSquare className="h-3.5 w-3.5 flex-shrink-0" />
                      <span className="min-w-0 flex-1 truncate">{s.title}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteSession(s.id)
                        }}
                        className="hidden flex-shrink-0 text-muted-foreground hover:text-destructive group-hover:block"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat area */}
      <div className="flex flex-1 flex-col">
        {/* Chat header */}
        <div className="flex items-center gap-3 border-b border-border/60 px-4 py-3">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="text-muted-foreground hover:text-foreground"
          >
            {showSidebar ? (
              <ChevronLeft className="h-5 w-5" />
            ) : (
              <MessageSquare className="h-5 w-5" />
            )}
          </button>
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-sm font-semibold text-foreground">
                AgriVision AI Assistant
              </p>
              <p className="text-xs text-muted-foreground">
                Agricultural knowledge powered by RAG
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
                <Leaf className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">
                Ask me anything about farming
              </h3>
              <p className="mt-1 max-w-md text-sm text-muted-foreground">
                I can help with crop diseases, pest control, soil management,
                weather impacts, and more.
              </p>

              <div className="mt-6 grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
                {suggestedQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => {
                      setInput(q)
                    }}
                    className="rounded-lg border border-border/60 px-3 py-2.5 text-left text-xs text-muted-foreground transition-colors hover:border-primary/30 hover:bg-primary/5 hover:text-foreground"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-3 ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {msg.role === "assistant" && (
                    <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-primary/10">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div
                    className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    {msg.sources && (
                      <p className="mt-2 border-t border-current/10 pt-2 text-xs opacity-70">
                        Sources: {msg.sources}
                      </p>
                    )}
                  </div>
                  {msg.role === "user" && (
                    <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-muted">
                      <UserIcon className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                </motion.div>
              ))}

              {isSending && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-3"
                >
                  <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="rounded-2xl bg-muted px-4 py-3">
                    <div className="flex gap-1">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/50" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/50 [animation-delay:0.15s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/50 [animation-delay:0.3s]" />
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-border/60 p-4">
          <div className="flex gap-2">
            <Input
              placeholder="Ask about crop diseases, treatments, farming advice..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isSending}
              className="flex-1"
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || isSending}
              size="icon"
              className="flex-shrink-0"
            >
              {isSending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
