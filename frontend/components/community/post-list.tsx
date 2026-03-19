"use client"

import { PostCard } from "./post-card"
import type { CommunityPost } from "@/lib/api"
import { communityAPI } from "@/lib/api"

interface PostListProps {
  posts: CommunityPost[]
}

export function PostList({ posts }: PostListProps) {
  const handleLike = async (postId: string) => {
    try {
      // Check if already liked and toggle appropriately
      const post = posts.find((p) => p.id === postId)
      if (post?.is_liked) {
        await communityAPI.unlikePost(postId)
      } else {
        await communityAPI.likePost(postId)
      }
    } catch (err) {
      console.error("Failed to update like:", err)
    }
  }

  if (posts.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-dashed border-border/60 py-12 text-center">
        <p className="text-sm font-medium text-muted-foreground">
          No posts found. Be the first to share!
        </p>
      </div>
    )
  }

  return (
    <div className="grid gap-8 xl:grid-cols-2">
      {posts.map((post) => (
        <PostCard key={post.id} post={post} onLike={handleLike} />
      ))}
    </div>
  )
}
