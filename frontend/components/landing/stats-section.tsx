"use client"

import {
  motion,
  useInView,
  useMotionValue,
  useTransform,
  animate,
} from "framer-motion"
import { useRef, useEffect, useState } from "react"
import Image from "next/image"

interface AnimatedCounterProps {
  target: number
  suffix?: string
  duration?: number
}

function AnimatedCounter({
  target,
  suffix = "",
  duration = 2,
}: AnimatedCounterProps) {
  const [displayValue, setDisplayValue] = useState(0)
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  const motionValue = useMotionValue(0)
  const rounded = useTransform(motionValue, (v) => Math.round(v))

  useEffect(() => {
    if (isInView) {
      const controls = animate(motionValue, target, {
        duration,
        ease: "easeOut",
      })
      return controls.stop
    }
  }, [isInView, motionValue, target, duration])

  useEffect(() => {
    const unsubscribe = rounded.on("change", (v) => setDisplayValue(v))
    return unsubscribe
  }, [rounded])

  return (
    <span ref={ref}>
      {displayValue.toLocaleString()}
      {suffix}
    </span>
  )
}

const stats = [
  { value: 98, suffix: "%", label: "Detection Accuracy" },
  { value: 150, suffix: "+", label: "Diseases Recognized" },
  { value: 12000, suffix: "+", label: "Active Farms" },
  { value: 50, suffix: "+", label: "Crop Types Supported" },
]

export function StatsSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-80px" })

  return (
    <section className="relative py-20 md:py-28" ref={ref}>
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="relative overflow-hidden rounded-3xl border border-border/60 shadow-lg"
        >
          {/* Background image */}
          <div className="pointer-events-none absolute inset-0">
            <Image
              src="/images/stats-greenhouse.jpg"
              alt=""
              fill
              className="object-cover"
            />
            <div className="absolute inset-0 bg-background/50 backdrop-blur-[1px]" />
            <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-primary/10" />
          </div>

          <div className="relative p-10 md:p-14">
            <div className="grid grid-cols-2 gap-8 md:grid-cols-4 md:gap-12">
              {stats.map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="font-heading text-4xl font-bold text-primary md:text-5xl">
                    <AnimatedCounter
                      target={stat.value}
                      suffix={stat.suffix}
                    />
                  </p>
                  <p className="mt-2 text-sm font-medium text-muted-foreground">
                    {stat.label}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
