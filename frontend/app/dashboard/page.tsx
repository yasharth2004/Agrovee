"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { motion } from "framer-motion"
import {
  Camera,
  MessageSquare,
  Activity,
  TrendingUp,
  Leaf,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowRight,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/auth-context"
import { usersAPI, diagnosisAPI, type UserStats, type DiagnosisResponse } from "@/lib/api"

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [recentDiagnoses, setRecentDiagnoses] = useState<DiagnosisResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, recentRes] = await Promise.all([
          usersAPI.stats(),
          diagnosisAPI.recent(5),
        ])
        setStats(statsRes.data)
        setRecentDiagnoses(recentRes.data)
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [])

  const greeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return "Good morning"
    if (hour < 18) return "Good afternoon"
    return "Good evening"
  }

  const statCards = [
    {
      title: "Total Scans",
      value: stats?.total_diagnoses ?? 0,
      icon: Camera,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      title: "Healthy Crops",
      value: stats?.healthy_count ?? 0,
      icon: CheckCircle2,
      color: "text-green-600",
      bg: "bg-green-50",
    },
    {
      title: "Diseases Found",
      value: stats?.diseased_count ?? 0,
      icon: AlertTriangle,
      color: "text-amber-600",
      bg: "bg-amber-50",
    },
    {
      title: "Avg. Confidence",
      value: `${(stats?.average_confidence ?? 0).toFixed(0)}%`,
      icon: TrendingUp,
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
  ]

  const quickActions = [
    {
      title: "New Diagnosis",
      description: "Upload a crop image for instant AI analysis",
      href: "/dashboard/diagnose",
      icon: Camera,
      color: "bg-primary",
    },
    {
      title: "AI Chat",
      description: "Ask the AI assistant about crop diseases",
      href: "/dashboard/chat",
      icon: MessageSquare,
      color: "bg-blue-600",
    },
  ]

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="font-heading text-2xl font-bold text-foreground md:text-3xl">
          {greeting()}, {user?.full_name?.split(" ")[0] || "Farmer"} 👋
        </h1>
        <p className="mt-1 text-muted-foreground">
          Here&apos;s an overview of your crop health monitoring.
        </p>
      </motion.div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {statCards.map((card, i) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="rounded-xl border border-border/60 bg-card p-5 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <p className="text-xs font-medium text-muted-foreground">
                {card.title}
              </p>
              <div className={`rounded-lg p-2 ${card.bg}`}>
                <card.icon className={`h-4 w-4 ${card.color}`} />
              </div>
            </div>
            <p className="mt-2 text-2xl font-bold text-foreground">
              {card.value}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        {quickActions.map((action, i) => (
          <motion.div
            key={action.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + i * 0.1 }}
          >
            <Link href={action.href}>
              <div className="group flex items-center gap-4 rounded-xl border border-border/60 bg-card p-5 shadow-sm transition-all hover:border-primary/30 hover:shadow-md">
                <div className={`rounded-xl p-3 ${action.color}`}>
                  <action.icon className="h-6 w-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-foreground">
                    {action.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {action.description}
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      {/* Recent Diagnoses */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <h2 className="font-heading text-lg font-semibold text-foreground">
            Recent Diagnoses
          </h2>
          <Link href="/dashboard/diagnose">
            <Button variant="ghost" size="sm" className="gap-1 text-primary">
              View all <ArrowRight className="h-3 w-3" />
            </Button>
          </Link>
        </div>

        {recentDiagnoses.length === 0 ? (
          <div className="mt-4 flex flex-col items-center rounded-xl border border-dashed border-border/60 py-12 text-center">
            <Leaf className="mb-3 h-10 w-10 text-muted-foreground/50" />
            <p className="text-sm font-medium text-muted-foreground">
              No diagnoses yet
            </p>
            <p className="mt-1 text-xs text-muted-foreground/70">
              Upload your first crop image to get started
            </p>
            <Link href="/dashboard/diagnose">
              <Button size="sm" className="mt-4 gap-2">
                <Camera className="h-4 w-4" />
                Start Diagnosis
              </Button>
            </Link>
          </div>
        ) : (
          <div className="mt-4 space-y-3">
            {recentDiagnoses.map((d) => (
              <div
                key={d.id}
                className="flex items-center gap-4 rounded-xl border border-border/60 bg-card p-4 shadow-sm"
              >
                <div
                  className={`rounded-lg p-2 ${
                    d.risk_assessment === "HIGH" || d.risk_assessment === "CRITICAL"
                      ? "bg-red-50"
                      : d.predicted_disease?.toLowerCase().includes("healthy")
                      ? "bg-green-50"
                      : "bg-amber-50"
                  }`}
                >
                  {d.predicted_disease?.toLowerCase().includes("healthy") ? (
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                  ) : (
                    <AlertTriangle
                      className={`h-4 w-4 ${
                        d.risk_assessment === "HIGH" || d.risk_assessment === "CRITICAL"
                          ? "text-red-600"
                          : "text-amber-600"
                      }`}
                    />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-foreground">
                    {d.predicted_disease
                      ? (() => {
                          let disease = d.predicted_disease.includes("___")
                            ? d.predicted_disease.split("___")[1] || ""
                            : d.predicted_disease
                          return disease.replace(/_/g, " ").replace(/\s+/g, " ").trim()
                            .split(" ").map((w: string) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ")
                        })()
                      : "Processing..."}
                  </p>
                  <div className="mt-0.5 flex items-center gap-2 text-xs text-muted-foreground">
                    {d.crop_type && <span>{d.crop_type.replace(/[_(].*\)/, "").replace(/,_/g, " ").replace(/_/g, " ").trim()}</span>}
                    {d.confidence_score != null && (
                      <span>
                        {d.confidence_score.toFixed(0)}% confidence
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {new Date(d.created_at).toLocaleDateString()}
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    d.status === "completed"
                      ? "bg-green-100 text-green-700"
                      : d.status === "failed"
                      ? "bg-red-100 text-red-700"
                      : "bg-amber-100 text-amber-700"
                  }`}
                >
                  {d.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Most Common Disease */}
      {stats?.most_common_disease && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="rounded-xl border border-amber-200 bg-amber-50/50 p-5"
        >
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 text-amber-600" />
            <div>
              <h3 className="text-sm font-semibold text-amber-900">
                Most Frequent Issue
              </h3>
              <p className="mt-1 text-sm text-amber-700">
                <strong>{stats.most_common_disease}</strong> has been detected
                most frequently in your scans. Consider reviewing preventive
                measures.
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}
