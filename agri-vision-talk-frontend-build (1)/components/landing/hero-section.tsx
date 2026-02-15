"use client"

import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { ArrowRight, Sparkles, ShieldCheck, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"

const floatingStats = [
  { label: "Crop Accuracy", value: "98.5%", icon: ShieldCheck, delay: 0.8 },
  { label: "Diseases Detected", value: "150+", icon: Zap, delay: 1.0 },
  { label: "Active Farms", value: "12K+", icon: Sparkles, delay: 1.2 },
]

export function HeroSection() {
  return (
    <section className="relative overflow-hidden pt-32 pb-20 md:pt-44 md:pb-32">
      {/* Full bleed background image */}
      <div className="pointer-events-none absolute inset-0">
        <Image
          src="/images/hero-bg.jpg"
          alt=""
          fill
          sizes="100vw"
          className="object-cover"
          priority
        />
        {/* Multi-layer blend overlay */}
        <div className="absolute inset-0 bg-background/80 backdrop-blur-[2px]" />
        <div className="absolute inset-0 bg-gradient-to-b from-background via-background/60 to-background" />
        <div className="absolute right-0 bottom-0 left-0 h-40 bg-gradient-to-t from-background to-transparent" />
      </div>

      {/* Soft glows on top */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-[600px] w-[600px] rounded-full bg-primary/8 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-primary/8 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="flex flex-col items-center text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-background/70 px-4 py-1.5 text-sm font-medium text-accent-foreground backdrop-blur-md">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              <span>AI-Powered Agricultural Intelligence</span>
            </div>
          </motion.div>

          {/* Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="font-heading max-w-4xl text-4xl font-bold leading-tight tracking-tight text-foreground md:text-6xl lg:text-7xl"
          >
            <span className="text-balance">
              Smart Farming Starts{" "}
              <span className="text-primary">With AI</span>
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-6 max-w-2xl text-pretty text-lg leading-relaxed text-muted-foreground md:text-xl"
          >
            Monitor crop health in real-time, detect diseases early, and receive
            AI-powered advisory tailored to your farm. From seed to harvest,
            we&apos;ve got you covered.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="mt-10 flex flex-col gap-3 sm:flex-row sm:gap-4"
          >
            <Button size="lg" className="gap-2 px-8 text-base" asChild>
              <Link href="/register">
                Get Started Free
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="border-border bg-background/60 px-8 text-base backdrop-blur-sm"
              asChild
            >
              <Link href="#how-it-works">Learn More</Link>
            </Button>
          </motion.div>

          {/* Floating Stat Cards */}
          <div className="mt-16 grid w-full max-w-3xl grid-cols-1 gap-4 sm:grid-cols-3">
            {floatingStats.map((stat) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: stat.delay }}
                whileHover={{ y: -4, scale: 1.02 }}
                className="group rounded-2xl border border-border/60 bg-card/90 p-5 shadow-sm backdrop-blur-lg transition-shadow hover:shadow-md"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent">
                    <stat.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="text-left">
                    <p className="font-heading text-2xl font-bold text-foreground">
                      {stat.value}
                    </p>
                    <p className="text-xs font-medium text-muted-foreground">
                      {stat.label}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
