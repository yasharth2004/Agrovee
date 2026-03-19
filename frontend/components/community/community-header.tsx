"use client"

import { useState } from "react"
import { Search, Plus, Menu, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface CommunityHeaderProps {
  onSearch: (query: string) => void
  onCreatePost: () => void
}

export function CommunityHeader({
  onSearch,
  onCreatePost,
}: CommunityHeaderProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setSearchQuery(query)
    onSearch(query)
  }

  return (
    <header className="border-b border-border bg-card shadow-sm">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 py-4 md:flex-row md:items-center md:justify-between">
          <div className="flex w-full flex-1 items-center">
            <div className="relative w-full max-w-xl">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search posts..."
                value={searchQuery}
                onChange={handleSearch}
                className="w-full rounded-lg border border-input bg-background py-2 pl-10 pr-4 text-sm placeholder-muted-foreground focus:border-primary focus:outline-none"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              onClick={onCreatePost}
              className="hidden gap-2 sm:flex"
              size="sm"
            >
              <Plus className="h-4 w-4" />
              New Post
            </Button>

            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {isMobileMenuOpen && (
          <div className="border-t border-border py-4 md:hidden">
            <Button
              onClick={() => {
                onCreatePost()
                setIsMobileMenuOpen(false)
              }}
              className="w-full gap-2"
              size="sm"
            >
              <Plus className="h-4 w-4" />
              New Post
            </Button>
          </div>
        )}
      </div>
    </header>
  )
}
