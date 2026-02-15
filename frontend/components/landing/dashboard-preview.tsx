"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import Image from "next/image"
import { Activity, Droplets, Thermometer, ShieldAlert } from "lucide-react"

const dashboardCards = [
  {
    icon: Activity,
    label: "Crop Health",
    value: "92%",
    trend: "+4.2%",
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    icon: Thermometer,
    label: "Temperature",
    value: "28°C",
    trend: "Optimal",
    color: "text-amber-600 dark:text-amber-400",
    bg: "bg-amber-500/10",
  },
  {
    icon: Droplets,
    label: "Soil Moisture",
    value: "67%",
    trend: "Good",
    color: "text-cyan-600 dark:text-cyan-400",
    bg: "bg-cyan-500/10",
  },
  {
    icon: ShieldAlert,
    label: "Risk Level",
    value: "Low",
    trend: "Stable",
    color: "text-primary",
    bg: "bg-primary/10",
  },
]

export function DashboardPreview() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-80px" })

  return (
    <section className="relative py-12 md:py-20" ref={ref}>
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="relative"
        >
          {/* Outer glow */}
          <div className="absolute -inset-4 rounded-3xl bg-primary/5 blur-2xl" />

          {/* Main card */}
          <div className="relative overflow-hidden rounded-2xl border border-border/60 bg-card shadow-xl">
            {/* Top bar */}
            <div className="flex items-center gap-2 border-b border-border/60 bg-muted/50 px-4 py-3">
              <div className="h-3 w-3 rounded-full bg-red-400/70" />
              <div className="h-3 w-3 rounded-full bg-amber-400/70" />
              <div className="h-3 w-3 rounded-full bg-primary/70" />
              <span className="ml-4 text-xs text-muted-foreground">
                AgriVisionTalk Dashboard
              </span>
            </div>

            {/* Content */}
            <div className="grid grid-cols-1 gap-0 lg:grid-cols-5">
              {/* Sidebar mockup */}
              <div className="hidden border-r border-border/60 bg-muted/30 p-4 lg:block">
                <div className="flex flex-col gap-2">
                  {[
                    "Overview",
                    "Upload Crop",
                    "Weather",
                    "Chat AI",
                    "History",
                  ].map((item, i) => (
                    <div
                      key={item}
                      className={`rounded-lg px-3 py-2 text-xs font-medium ${
                        i === 0
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-accent"
                      }`}
                    >
                      {item}
                    </div>
                  ))}
                </div>
              </div>

              {/* Main content */}
              <div className="p-5 lg:col-span-4 lg:p-6">
                {/* Mini stat cards */}
                <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                  {dashboardCards.map((card, i) => (
                    <motion.div
                      key={card.label}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={isInView ? { opacity: 1, scale: 1 } : {}}
                      transition={{ duration: 0.4, delay: 0.3 + i * 0.1 }}
                      className="rounded-xl border border-border/60 bg-card p-3"
                    >
                      <div className="flex items-center gap-2">
                        <div
                          className={`flex h-7 w-7 items-center justify-center rounded-lg ${card.bg}`}
                        >
                          <card.icon className={`h-3.5 w-3.5 ${card.color}`} />
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {card.label}
                        </span>
                      </div>
                      <p className="mt-2 font-heading text-xl font-bold text-foreground">
                        {card.value}
                      </p>
                      <p className="text-xs text-primary">{card.trend}</p>
                    </motion.div>
                  ))}
                </div>

                {/* Image preview */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={isInView ? { opacity: 1 } : {}}
                  transition={{ duration: 0.5, delay: 0.7 }}
                  className="mt-4 overflow-hidden rounded-xl border border-border/60"
                >
                  <div className="relative h-48 md:h-64">
                    <Image
                      src="/images/features-field.jpg"
                      alt="Smart farming dashboard preview showing healthy crop fields"
                      fill
                      className="object-cover"
                      priority
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-card/80 to-transparent" />
                    <div className="absolute bottom-4 left-4">
                      <p className="text-sm font-semibold text-foreground">
                        Field Analysis - Zone A
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Last scanned 2 hours ago
                      </p>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
