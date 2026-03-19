"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, MessageCircle, Trash2 } from "lucide-react"
import { CategoryFilter } from "@/components/community/category-filter"
import {
  communityAPI,
  resolveMediaUrl,
  type CommunityPost,
  type CommunityComment,
} from "@/lib/api"

export default function CommunityPostDetailPage() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const [post, setPost] = useState<CommunityPost | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [commentText, setCommentText] = useState("")
  const [isSubmittingComment, setIsSubmittingComment] = useState(false)

  useEffect(() => {
    const fetchPost = async () => {
      setIsLoading(true)
      try {
        const response = await communityAPI.getPost(params.id)
        setPost(response.data)
      } catch (err) {
        console.error("Failed to fetch post:", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchPost()
  }, [params.id])

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!commentText.trim() || !post) return
    setIsSubmittingComment(true)
    try {
      const response = await communityAPI.createComment(
        post.id,
        commentText.trim()
      )
      setPost((prev) =>
        prev
          ? {
              ...prev,
              comments: [...(prev.comments || []), response.data],
              comments_count: (prev.comments_count || 0) + 1,
            }
          : null
      )
      setCommentText("")
    } catch (err) {
      console.error("Failed to add comment:", err)
      alert("Failed to add comment")
    } finally {
      setIsSubmittingComment(false)
    }
  }

  const handleDeleteComment = async (commentId: string) => {
    if (!post) return
    if (!confirm("Delete this comment?")) return
    try {
      await communityAPI.deleteComment(post.id, commentId)
      setPost((prev) =>
        prev
          ? {
              ...prev,
              comments: (prev.comments || []).filter(
                (c) => c.id !== commentId
              ),
              comments_count: Math.max(0, (prev.comments_count || 0) - 1),
            }
          : null
      )
    } catch (err) {
      console.error("Failed to delete comment:", err)
      alert("Failed to delete comment")
    }
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!post) {
    return (
      <div className="mx-auto max-w-5xl">
        <button
          onClick={() => router.push("/dashboard/community")}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Community
        </button>
        <div className="mt-8 text-center">
          <p className="text-muted-foreground">Post not found</p>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <button
        onClick={() => router.push("/dashboard/community")}
        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Community
      </button>

      <div className="grid gap-6 lg:grid-cols-[260px,1fr]">
        <aside className="rounded-2xl bg-card p-4 shadow-sm">
          <CategoryFilter
            selectedCategory={post.category as any}
            // read-only in detail view
            onSelectCategory={() => {}}
          />
        </aside>

        <article className="space-y-6 rounded-2xl bg-card p-6 shadow-sm">
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">
              {new Date(post.created_at).toLocaleString()}
            </p>
            <h1 className="font-heading text-2xl font-bold text-foreground">
              {post.title}
            </h1>
            <p className="whitespace-pre-line text-sm text-foreground">
              {post.content}
            </p>
            <div className="flex gap-4 text-xs text-muted-foreground pt-2">
              <span>{post.views_count} views</span>
              <span>{(post.comments || []).length} comments</span>
              <span>{post.likes_count} likes</span>
            </div>
          </div>

          {post.media && post.media.length > 0 && (
            <section className="space-y-3 rounded-xl border border-border bg-background/40 p-4">
              <h2 className="font-heading text-sm font-semibold text-foreground">
                Field Photos ({post.media.length})
              </h2>
              <div className="grid gap-3 sm:grid-cols-2">
                {post.media.map((media) => (
                  <div
                    key={media.id}
                    className="relative overflow-hidden rounded-lg border border-border/60"
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
            </section>
          )}

          <section className="space-y-4 border-t border-border pt-4">
            <h2 className="flex items-center gap-2 font-heading text-sm font-semibold text-foreground">
              <MessageCircle className="h-4 w-4" />
              Comments ({(post.comments || []).length})
            </h2>

            <form onSubmit={handleAddComment} className="space-y-3">
              <textarea
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Share your thoughts or experience..."
                rows={3}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder-muted-foreground focus:border-primary focus:outline-none"
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isSubmittingComment || !commentText.trim()}
                  className="rounded-lg bg-primary px-4 py-2 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                >
                  {isSubmittingComment ? "Posting..." : "Post Comment"}
                </button>
              </div>
            </form>

            {(post.comments || []).length === 0 ? (
              <p className="text-xs text-muted-foreground">
                No comments yet. Be the first to comment!
              </p>
            ) : (
              <ul className="space-y-3 text-sm">
                {(post.comments || []).map((comment) => (
                  <li
                    key={comment.id}
                    className="rounded-lg border border-border bg-background p-3"
                  >
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>User #{comment.user_id}</span>
                      <div className="flex items-center gap-2">
                        <span>
                          {new Date(comment.created_at).toLocaleString()}
                        </span>
                        <button
                          onClick={() => handleDeleteComment(comment.id)}
                          className="text-destructive hover:opacity-70"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                    <p className="mt-1 text-foreground">{comment.content}</p>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </article>
      </div>
    </div>
  )
}
