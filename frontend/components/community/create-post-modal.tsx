"use client"

import { useEffect, useRef, useState } from "react"
import { ImagePlus, Send, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { CommunityCategoryId } from "./category-filter"

const CATEGORIES: { id: CommunityCategoryId; label: string }[] = [
  { id: "pest_control", label: "Pest Control" },
  { id: "irrigation", label: "Irrigation" },
  { id: "soil_health", label: "Soil Health" },
  { id: "weather", label: "Weather & Climate" },
  { id: "crop_varieties", label: "Crop Varieties" },
  { id: "equipment", label: "Equipment & Tools" },
  { id: "general", label: "General Discussion" },
]

interface CreatePostModalProps {
  isOpen: boolean
  onClose: () => void
  onCreate: (data: {
    title: string
    content: string
    category: CommunityCategoryId
    mediaFiles?: File[]
  }) => Promise<void> | void
}

export function CreatePostModal({
  isOpen,
  onClose,
  onCreate,
}: CreatePostModalProps) {
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [category, setCategory] = useState<CommunityCategoryId>("general")
  const [attachments, setAttachments] = useState<{
    file: File
    url: string
  }[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const MAX_ATTACHMENTS = 4

  useEffect(() => {
    return () => {
      attachments.forEach((attachment) => URL.revokeObjectURL(attachment.url))
    }
  }, [attachments])

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return
    const selected = Array.from(fileList)
    setAttachments((prev) => {
      const next = [...prev]
      selected.forEach((file) => {
        if (next.length >= MAX_ATTACHMENTS) return
        next.push({ file, url: URL.createObjectURL(file) })
      })
      return next
    })
  }

  const removeAttachment = (index: number) => {
    setAttachments((prev) => {
      const next = [...prev]
      const [removed] = next.splice(index, 1)
      if (removed) URL.revokeObjectURL(removed.url)
      return next
    })
  }

  const resetForm = () => {
    setTitle("")
    setContent("")
    setCategory("general")
    attachments.forEach((attachment) => URL.revokeObjectURL(attachment.url))
    setAttachments([])
  }

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!title.trim() || !content.trim()) return

    const mediaFiles = attachments.map((attachment) => attachment.file)

    try {
      setIsSubmitting(true)
      await Promise.resolve(
        onCreate({
          title: title.trim(),
          content: content.trim(),
          category,
          mediaFiles: mediaFiles.length ? mediaFiles : undefined,
        })
      )
      resetForm()
      onClose()
    } catch (error) {
      console.error("Failed to submit community post", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-2xl rounded-lg bg-card shadow-xl">
        <div className="flex items-center justify-between border-b border-border p-6">
          <h2 className="font-heading text-2xl font-bold text-foreground">
            Create a New Post
          </h2>
          <button
            onClick={onClose}
            className="rounded-lg p-2 hover:bg-muted"
            disabled={isSubmitting}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-foreground">
                Category
              </label>
              <select
                value={category}
                onChange={(e) =>
                  setCategory(e.target.value as CommunityCategoryId)
                }
                className="mt-2 w-full rounded-lg border border-input bg-background px-4 py-2 focus:border-primary focus:outline-none"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-foreground">
                Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="What's your question or insight?"
                className="mt-2 w-full rounded-lg border border-input bg-background px-4 py-2 placeholder-muted-foreground focus:border-primary focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-foreground">
                Photos (optional)
              </label>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={(e) => handleFiles(e.target.files)}
              />
              <div className="mt-2 rounded-lg border border-dashed border-input bg-muted/30 p-4 text-center">
                <p className="text-xs text-muted-foreground">
                  You can attach up to {MAX_ATTACHMENTS} photos (JPG or PNG, max 10MB each).
                </p>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  className="mt-3 gap-2"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <ImagePlus className="h-4 w-4" />
                  Upload photos
                </Button>
              </div>

              {attachments.length > 0 && (
                <div className="mt-3 grid grid-cols-2 gap-3">
                  {attachments.map((attachment, index) => (
                    <div
                      key={attachment.url}
                      className="relative overflow-hidden rounded-lg border border-border/60"
                    >
                      <button
                        type="button"
                        onClick={() => removeAttachment(index)}
                        className="absolute right-2 top-2 rounded-full bg-background/80 p-1 text-foreground shadow"
                      >
                        <X className="h-3 w-3" />
                      </button>
                      <img
                        src={attachment.url}
                        alt={`Attachment ${index + 1}`}
                        className="h-32 w-full object-cover"
                        loading="lazy"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-foreground">
                Description
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Share your experience, ask questions, or discuss farming practices..."
                rows={6}
                className="mt-2 w-full rounded-lg border border-input bg-background px-4 py-2 placeholder-muted-foreground focus:border-primary focus:outline-none"
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-3 border-t border-border pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting} className="gap-2">
              <Send className="h-4 w-4" />
              {isSubmitting ? "Posting..." : "Post"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
