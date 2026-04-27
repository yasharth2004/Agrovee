"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import {
  Users,
  FileText,
  MessageSquare,
  TrendingUp,
  BarChart3,
  Trash2,
  AlertTriangle,
  Check,
  X,
  Loader2,
  Search,
  Filter,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAuth } from "@/lib/auth-context"
import { adminAPI, type AdminStats, type AdminPost, type AdminUser } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function AdminDashboardPage() {
  const router = useRouter()
  const { user } = useAuth()
  const { toast } = useToast()
  
  // Redirects
  useEffect(() => {
    if (user && !user.is_admin) {
      router.push("/dashboard")
    }
  }, [user, router])

  if (!user?.is_admin) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-red-600 mb-4" />
          <h1 className="text-2xl font-bold text-foreground">Access Denied</h1>
          <p className="text-muted-foreground mt-2">You do not have admin privileges.</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <AdminDashboardContent />
    </>
  )
}

function AdminDashboardContent() {
  const { toast } = useToast()
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [posts, setPosts] = useState<AdminPost[]>([])
  const [users, setUsers] = useState<AdminUser[]>([])
  const [isLoadingStats, setIsLoadingStats] = useState(true)
  const [isLoadingPosts, setIsLoadingPosts] = useState(false)
  const [isLoadingUsers, setIsLoadingUsers] = useState(false)
  const [activeTab, setActiveTab] = useState("stats")

  // Filters
  const [postsSearch, setPostsSearch] = useState("")
  const [postsCategory, setPostsCategory] = useState("all")
  const [postsSortBy, setPostsSortBy] = useState("recent")
  const [postsPage, setPostsPage] = useState(0)
  const [postsTotalCount, setPostsTotalCount] = useState(0)

  const [usersSearch, setUsersSearch] = useState("")
  const [usersPage, setUsersPage] = useState(0)
  const [usersTotalCount, setUsersTotalCount] = useState(0)

  const ITEMS_PER_PAGE = 20

  useEffect(() => {
    fetchStats()
  }, [])

  useEffect(() => {
    if (activeTab === "posts") {
      fetchPosts()
    }
  }, [activeTab, postsSearch, postsCategory, postsSortBy, postsPage])

  useEffect(() => {
    if (activeTab === "users") {
      fetchUsers()
    }
  }, [activeTab, usersSearch, usersPage])

  const fetchStats = async () => {
    try {
      setIsLoadingStats(true)
      const res = await adminAPI.stats()
      setStats(res.data)
    } catch (err) {
      console.error("Failed to fetch stats:", err)
      toast({
        title: "Error",
        description: "Failed to load dashboard statistics",
        variant: "destructive",
      })
    } finally {
      setIsLoadingStats(false)
    }
  }

  const fetchPosts = async () => {
    try {
      setIsLoadingPosts(true)
      const res = await adminAPI.listPosts(
        postsCategory,
        postsSearch,
        postsPage * ITEMS_PER_PAGE,
        ITEMS_PER_PAGE,
        postsSortBy
      )
      setPosts(res.data.posts)
      setPostsTotalCount(res.data.total)
    } catch (err) {
      console.error("Failed to fetch posts:", err)
      toast({
        title: "Error",
        description: "Failed to load community posts",
        variant: "destructive",
      })
    } finally {
      setIsLoadingPosts(false)
    }
  }

  const fetchUsers = async () => {
    try {
      setIsLoadingUsers(true)
      const res = await adminAPI.listUsers(
        usersPage * ITEMS_PER_PAGE,
        ITEMS_PER_PAGE,
        usersSearch
      )
      setUsers(res.data.users)
      setUsersTotalCount(res.data.total)
    } catch (err) {
      console.error("Failed to fetch users:", err)
      toast({
        title: "Error",
        description: "Failed to load users",
        variant: "destructive",
      })
    } finally {
      setIsLoadingUsers(false)
    }
  }

  const handleDeletePost = async (postId: string, title: string) => {
    if (!window.confirm(`Delete post "${title}"? This action cannot be undone.`)) {
      return
    }

    const previousPosts = posts
    const previousTotal = postsTotalCount

    // Optimistic UI update so the row disappears immediately
    setPosts((current) => current.filter((p) => p.id !== postId))
    setPostsTotalCount((count) => Math.max(0, count - 1))

    try {
      await adminAPI.deletePost(postId, "Admin moderation")
      toast({
        title: "Success",
        description: "Post deleted successfully",
      })
    } catch (err: any) {
      const isNetworkError = err?.message === "Network Error"

      if (isNetworkError) {
        // Backend already processed the delete, but the client lost the response
        toast({
          title: "Post deleted",
          description: "Lost connection to the server while confirming, but the post was removed.",
        })
      } else {
        // True failure – put the post back so UI stays consistent
        setPosts(previousPosts)
        setPostsTotalCount(previousTotal)
        toast({
          title: "Error",
          description: err.response?.data?.detail || "Failed to delete post",
          variant: "destructive",
        })
        return
      }
    } finally {
      // Refresh server data so pagination & stats stay accurate
      fetchPosts()
      fetchStats()
    }
  }

  const handleToggleUserActive = async (userId: number, currentStatus: boolean) => {
    try {
      await adminAPI.toggleUserActive(userId)
      toast({
        title: "Success",
        description: `User ${currentStatus ? "deactivated" : "activated"} successfully`,
      })
      fetchUsers()
    } catch (err) {
      console.error("Failed to toggle user active:", err)
      toast({
        title: "Error",
        description: "Failed to update user status",
        variant: "destructive",
      })
    }
  }

  const totalPostsPages = Math.ceil(postsTotalCount / ITEMS_PER_PAGE)
  const totalUsersPages = Math.ceil(usersTotalCount / ITEMS_PER_PAGE)

  return (
    <div className="space-y-6 pb-20 px-4 sm:px-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mx-auto mb-8 w-full max-w-6xl">
          <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">Manage community posts and users</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mx-auto space-y-6 w-full max-w-6xl">
          <TabsList className="grid w-full max-w-2xl grid-cols-3">
            <TabsTrigger value="stats" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Statistics</span>
              <span className="sm:hidden">Stats</span>
            </TabsTrigger>
            <TabsTrigger value="posts" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline">Community Posts</span>
              <span className="sm:hidden">Posts</span>
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">Users</span>
            </TabsTrigger>
          </TabsList>

          {/* Statistics Tab */}
          <TabsContent value="stats" className="space-y-6">
            {isLoadingStats ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : stats ? (
              <>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  <StatCard
                    title="Total Users"
                    value={stats.total_users}
                    icon={Users}
                    color="bg-blue-50"
                    textColor="text-blue-600"
                  />
                  <StatCard
                    title="Active Users"
                    value={stats.active_users}
                    icon={Check}
                    color="bg-green-50"
                    textColor="text-green-600"
                  />
                  <StatCard
                    title="Total Posts"
                    value={stats.total_posts}
                    icon={FileText}
                    color="bg-purple-50"
                    textColor="text-purple-600"
                  />
                  <StatCard
                    title="Total Comments"
                    value={stats.total_comments}
                    icon={MessageSquare}
                    color="bg-orange-50"
                    textColor="text-orange-600"
                  />
                </div>

                <div className="mt-8 space-y-4">
                  <h3 className="text-lg font-semibold text-foreground">Posts by Category</h3>
                  <div className="space-y-3">
                    {stats.posts_by_category.length > 0 ? (
                      stats.posts_by_category.map((cat) => (
                        <div key={cat.category} className="flex items-center justify-between rounded-lg border p-4">
                          <span className="font-medium text-foreground capitalize">{cat.category}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary transition-all"
                                style={{
                                  width: `${Math.min(
                                    (cat.count / Math.max(...stats.posts_by_category.map((c) => c.count))) * 100,
                                    100
                                  )}%`,
                                }}
                              ></div>
                            </div>
                            <span className="w-8 text-right font-semibold text-primary">{cat.count}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-muted-foreground">No posts yet</p>
                    )}
                  </div>
                </div>
              </>
            ) : null}
          </TabsContent>

          {/* Community Posts Tab */}
          <TabsContent value="posts" className="space-y-6">
            <div className="space-y-4">
              <div className="flex flex-col gap-4 sm:flex-row">
                <div className="flex-1">
                  <Input
                    placeholder="Search posts..."
                    value={postsSearch}
                    onChange={(e) => {
                      setPostsSearch(e.target.value)
                      setPostsPage(0)
                    }}
                    className="w-full"
                  />
                </div>
                <Select value={postsCategory} onValueChange={(val) => {
                  setPostsCategory(val)
                  setPostsPage(0)
                }}>
                  <SelectTrigger className="w-full sm:w-40">
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    <SelectItem value="pest_control">Pest Control</SelectItem>
                    <SelectItem value="irrigation">Irrigation</SelectItem>
                    <SelectItem value="crop_disease">Crop Disease</SelectItem>
                    <SelectItem value="soil_management">Soil Management</SelectItem>
                    <SelectItem value="general">General</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={postsSortBy} onValueChange={(val) => {
                  setPostsSortBy(val)
                  setPostsPage(0)
                }}>
                  <SelectTrigger className="w-full sm:w-40">
                    <SelectValue placeholder="Sort" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="recent">Recent</SelectItem>
                    <SelectItem value="oldest">Oldest</SelectItem>
                    <SelectItem value="popular">Popular</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {isLoadingPosts ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : posts.length > 0 ? (
                <>
                  <div className="space-y-3">
                    {posts.map((post) => (
                      <motion.div
                        key={post.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="rounded-lg border p-4 hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex gap-4">
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-foreground truncate">{post.title}</h3>
                            <p className="text-sm text-muted-foreground truncate">{post.content}</p>
                            <div className="flex flex-wrap gap-2 mt-2 text-xs text-muted-foreground">
                              <span className="bg-muted px-2 py-1 rounded capitalize">{post.category}</span>
                              <span>By {post.user_name} ({post.user_email})</span>
                              <span>{post.views} views</span>
                              <span>{post.likes_count} likes</span>
                              <span>{post.comments_count} comments</span>
                              <span>{new Date(post.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeletePost(post.id, post.title)}
                            className="ml-2 shrink-0"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  {/* Pagination */}
                  <div className="flex items-center justify-between gap-4 mt-6">
                    <p className="text-sm text-muted-foreground">
                      Page {postsPage + 1} of {totalPostsPages} • Total: {postsTotalCount} posts
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPostsPage(Math.max(0, postsPage - 1))}
                        disabled={postsPage === 0}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPostsPage(postsPage + 1)}
                        disabled={postsPage >= totalPostsPages - 1}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-12">
                  <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No posts found</p>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            <div className="space-y-4">
              <div className="flex-1">
                <Input
                  placeholder="Search users by email or name..."
                  value={usersSearch}
                  onChange={(e) => {
                    setUsersSearch(e.target.value)
                    setUsersPage(0)
                  }}
                  className="w-full"
                />
              </div>

              {isLoadingUsers ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : users.length > 0 ? (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 font-semibold">Email</th>
                          <th className="text-left py-3 px-4 font-semibold">Name</th>
                          <th className="text-left py-3 px-4 font-semibold">Role</th>
                          <th className="text-left py-3 px-4 font-semibold">Status</th>
                          <th className="text-left py-3 px-4 font-semibold">Joined</th>
                          <th className="text-left py-3 px-4 font-semibold">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((u) => (
                          <tr key={u.id} className="border-b hover:bg-muted/50">
                            <td className="py-3 px-4 font-mono text-xs">{u.email}</td>
                            <td className="py-3 px-4">{u.full_name || "-"}</td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                u.is_admin ? "bg-red-100 text-red-800" : "bg-blue-100 text-blue-800"
                              }`}>
                                {u.is_admin ? "Admin" : "User"}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              {u.is_active ? (
                                <span className="flex items-center gap-1 text-green-600">
                                  <Check className="h-4 w-4" />
                                  Active
                                </span>
                              ) : (
                                <span className="flex items-center gap-1 text-red-600">
                                  <X className="h-4 w-4" />
                                  Inactive
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-xs text-muted-foreground">
                              {new Date(u.created_at).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4">
                              <Button
                                variant={u.is_active ? "destructive" : "outline"}
                                size="sm"
                                onClick={() => handleToggleUserActive(u.id, u.is_active)}
                              >
                                {u.is_active ? "Deactivate" : "Activate"}
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination */}
                  <div className="flex items-center justify-between gap-4 mt-6">
                    <p className="text-sm text-muted-foreground">
                      Page {usersPage + 1} of {totalUsersPages} • Total: {usersTotalCount} users
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setUsersPage(Math.max(0, usersPage - 1))}
                        disabled={usersPage === 0}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setUsersPage(usersPage + 1)}
                        disabled={usersPage >= totalUsersPages - 1}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-12">
                  <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No users found</p>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  color: string
  textColor: string
}

function StatCard({ title, value, icon: Icon, color, textColor }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`rounded-lg ${color} p-6`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${textColor}`}>{value}</p>
        </div>
        <Icon className={`h-8 w-8 ${textColor} opacity-50`} />
      </div>
    </motion.div>
  )
}
