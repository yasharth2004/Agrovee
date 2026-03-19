"use client"

import { useEffect, useMemo, useState } from "react"
import { CommunityHeader } from "@/components/community/community-header"
import { CategoryFilter, type CommunityCategoryId } from "@/components/community/category-filter"
import { PostList } from "@/components/community/post-list"
import { CreatePostModal } from "@/components/community/create-post-modal"
import type { CommunityPost } from "@/components/community/post-card"
import { communityAPI } from "@/lib/api"

export default function CommunityPage() {
  const [selectedCategory, setSelectedCategory] = useState<CommunityCategoryId>("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [posts, setPosts] = useState<CommunityPost[]>([])
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Fetch posts whenever category or search changes
  useEffect(() => {
    const fetchPosts = async () => {
      setIsLoading(true)
      try {
        const response = await communityAPI.listPosts(
          selectedCategory === "all" ? "" : selectedCategory,
          searchQuery,
          0,
          50
        )
        setPosts(response.data || [])
      } catch (err) {
        console.error("Failed to fetch posts:", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchPosts()
  }, [selectedCategory, searchQuery])

  const filteredPosts = useMemo(() => {
    return posts
  }, [posts])

  const handleCreatePost = async (data: {
    title: string
    content: string
    category: CommunityCategoryId
    mediaFiles?: File[]
  }) => {
    try {
      const response = await communityAPI.createPost(
        {
          title: data.title,
          content: data.content,
          category: data.category,
        },
        data.mediaFiles
      )
      setPosts((prev) => [response.data, ...prev])
    } catch (err: any) {
      console.error("Failed to create post:", err)
      console.error("Error details:", err.response?.data)
      const errorMsg = err.response?.data?.detail || "Failed to create post"
      alert(Array.isArray(errorMsg) ? JSON.stringify(errorMsg) : errorMsg)
    }
  }

  return (
    <div className="flex h-full flex-col rounded-2xl border border-border/60 bg-muted/40">
      <CommunityHeader
        onSearch={setSearchQuery}
        onCreatePost={() => setIsCreateOpen(true)}
      />

      <div className="flex flex-1 flex-col gap-6 p-4 lg:flex-row lg:p-6">
        <aside className="w-full max-w-xs flex-shrink-0 rounded-2xl bg-background p-4 shadow-sm lg:h-[calc(100vh-10rem)] lg:overflow-y-auto">
          <CategoryFilter
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />
        </aside>

        <section className="flex-1 rounded-2xl bg-background p-4 shadow-sm lg:h-[calc(100vh-10rem)] lg:overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : (
            <PostList posts={filteredPosts} />
          )}
        </section>
      </div>

      <CreatePostModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreate={handleCreatePost}
      />
    </div>
  )
}
