"use client"

import { useState } from "react"
import Link from "next/link"
import { Heart, MessageCircle, Eye } from "lucide-react"
import { resolveMediaUrl, type CommunityPost } from "@/lib/api"

interface PostCardProps {
  post: CommunityPost
  onLike?: (id: string) => Promise<void>
}

const CATEGORY_COLORS: Record<string, string> = {
  pest_control: "bg-red-100 text-red-800",
  irrigation: "bg-blue-100 text-blue-800",
  soil_health: "bg-amber-100 text-amber-800",
  weather: "bg-cyan-100 text-cyan-800",
  crop_varieties: "bg-green-100 text-green-800",
  equipment: "bg-gray-100 text-gray-800",
  general: "bg-purple-100 text-purple-800",
}

const CATEGORY_ICONS: Record<string, string> = {
  pest_control: "🦗",
  irrigation: "💧",
  soil_health: "🌱",
  weather: "☀️",
  crop_varieties: "🌽",
  equipment: "🔧",
  general: "💬",
}

export function PostCard({ post, onLike }: PostCardProps) {
  const [isLiked, setIsLiked] = useState(post.is_liked || false)
  const [likeCount, setLikeCount] = useState(post.likes_count || 0)
  const [isLiking, setIsLiking] = useState(false)

  const categoryLabel = post.category
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")

  const truncatedContent =
    post.content.length > 200
      ? post.content.substring(0, 200) + "..."
      : post.content

  const mediaPreviews = post.media?.slice(0, 4) ?? []
  const hasMedia = mediaPreviews.length > 0
  const mediaGridCols =
    mediaPreviews.length === 1
      ? "grid-cols-1"
      : mediaPreviews.length === 2
        ? "grid-cols-2"
        : "grid-cols-2 md:grid-cols-3"
  const mediaHeight =
    mediaPreviews.length === 1 ? "h-64" : mediaPreviews.length === 2 ? "h-44" : "h-36"

  const handleLikeClick = async (e: React.MouseEvent) => {
    e.preventDefault()
    if (isLiking) return
    setIsLiking(true)
    try {
      const nextLiked = !isLiked
      setIsLiked(nextLiked)
      setLikeCount((prev) => prev + (nextLiked ? 1 : -1))
      await onLike?.(post.id)
    } catch (err) {
      // Revert on error
      setIsLiked(!isLiked)
      setLikeCount((prev) => prev + (isLiked ? 1 : -1))
      console.error("Failed to like post:", err)
    } finally {
      setIsLiking(false)
    }
  }

  return (
    <Link href={`/dashboard/community/${post.id}`}>
      <article className="group flex h-full flex-col overflow-hidden rounded-[28px] border border-border/70 bg-gradient-to-br from-card/80 via-background to-card/60 shadow-[0_10px_40px_-25px_rgba(16,185,129,0.6)] transition-all hover:-translate-y-1 hover:border-primary/60">
        {hasMedia && (
          <div className="relative bg-muted/40">
            <div className={`grid ${mediaGridCols} gap-2 p-2 sm:p-3`}>
              {mediaPreviews.map((media) => (
                <div
                  key={media.id}
                  className={`relative overflow-hidden rounded-2xl border border-white/60 ${mediaHeight}`}
                >
                  <img
                    src={resolveMediaUrl(media.url || media.file_name)}
                    alt={media.file_name}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-1 flex-col gap-4 p-6">
          <div className="flex items-center gap-3">
            <span
              className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold shadow-sm ${
                CATEGORY_COLORS[post.category] || "bg-gray-100 text-gray-800"
              }`}
            >
              <span>{CATEGORY_ICONS[post.category] || "🌾"}</span>
              {categoryLabel}
            </span>
            <span className="text-[11px] uppercase tracking-wide text-muted-foreground">
              {new Date(post.created_at).toLocaleDateString()}
            </span>
          </div>

          <div className="space-y-3">
            <h3 className="font-heading text-xl font-semibold text-foreground transition-colors group-hover:text-primary">
              {post.title}
            </h3>
            <p className="text-sm text-muted-foreground">{truncatedContent}</p>
          </div>

          <div className="mt-auto flex flex-wrap items-center gap-6 rounded-2xl border border-border/60 bg-background/60 px-4 py-3 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Eye className="h-3 w-3" />
              {post.views_count} views
            </div>
            <div className="flex items-center gap-1">
              <MessageCircle className="h-3 w-3" />
              {post.comments_count} comments
            </div>
            <div className="ml-auto">
              <button
                onClick={handleLikeClick}
                disabled={isLiking}
                className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs transition-colors ${
                  isLiked
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:text-primary"
                } disabled:opacity-50`}
              >
                <Heart
                  className="h-4 w-4"
                  fill={isLiked ? "currentColor" : "none"}
                />
                <span>{likeCount}</span>
              </button>
            </div>
          </div>
        </div>
      </article>
    </Link>
  )
}
