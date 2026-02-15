"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import Image from "next/image"
import { Bug, CloudSun, MessageSquare, Droplets } from "lucide-react"

const features = [
  {
    icon: Bug,
    title: "Crop Disease Detection",
    description:
      "Upload a photo of your crop and our AI instantly identifies diseases with over 98% accuracy, powered by deep learning models trained on millions of samples.",
    color: "bg-red-500/10 text-red-600 dark:text-red-400",
  },
  {
    icon: CloudSun,
    title: "Weather-Aware Advisory",
    description:
      "Get real-time weather insights and predictive alerts tailored to your farm location. Plan your activities around accurate 5-day forecasts.",
    color: "bg-sky-500/10 text-sky-600 dark:text-sky-400",
  },
  {
    icon: MessageSquare,
    title: "AI Chat Support",
    description:
      "Chat with our intelligent assistant about crop management, soil health, pest control, and more. Get instant, expert-level answers 24/7.",
    color: "bg-primary/10 text-primary",
  },
  {
    icon: Droplets,
    title: "Smart Irrigation Guidance",
    description:
      "Optimize water usage with AI-driven irrigation schedules based on soil moisture, weather patterns, and crop growth stages.",
    color: "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400",
  },
]

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.12,
    },
  },
}

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" },
  },
}

export function FeaturesSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-80px" })

  return (
    <section id="features" className="relative py-24 md:py-32" ref={ref}>
      <div className="mx-auto max-w-7xl px-6">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
          className="mx-auto mb-16 max-w-2xl text-center"
        >
          <p className="mb-3 text-sm font-semibold tracking-wider text-primary uppercase">
            Features
          </p>
          <h2 className="font-heading text-3xl font-bold tracking-tight text-foreground md:text-4xl lg:text-5xl">
            <span className="text-balance">Everything Your Farm Needs</span>
          </h2>
          <p className="mt-4 text-pretty text-lg leading-relaxed text-muted-foreground">
            Harness the power of artificial intelligence to transform your
            agricultural practices and maximize yield.
          </p>
        </motion.div>

        {/* Two-column layout: image left, cards right */}
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
          {/* Blended image */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="relative hidden lg:block"
          >
            <div className="relative overflow-hidden rounded-3xl">
              <div className="aspect-[4/5] relative">
                <Image
                  src="/images/features-field.jpg"
                  alt="Farmer inspecting healthy crop leaves"
                  fill
                  sizes="(max-width: 1024px) 100vw, 50vw"
                  className="object-cover"
                />
                {/* Blend overlays */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-background/90" />
                <div className="absolute inset-0 bg-gradient-to-t from-background/70 via-transparent to-background/40" />
                <div className="absolute inset-0 rounded-3xl ring-1 ring-inset ring-border/30" />
              </div>
            </div>
            {/* Decorative glow behind image */}
            <div className="absolute -inset-4 -z-10 rounded-3xl bg-primary/5 blur-2xl" />
          </motion.div>

          {/* Feature cards */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            className="grid grid-cols-1 gap-5 sm:grid-cols-2"
          >
            {features.map((feature) => (
              <motion.div
                key={feature.title}
                variants={cardVariants}
                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                className="group relative rounded-2xl border border-border/60 bg-card p-6 shadow-sm transition-shadow hover:shadow-lg"
              >
                <div className="pointer-events-none absolute inset-0 rounded-2xl bg-primary/[0.02] opacity-0 transition-opacity group-hover:opacity-100" />
                <div
                  className={`mb-4 flex h-12 w-12 items-center justify-center rounded-xl ${feature.color}`}
                >
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="font-heading mb-2 text-lg font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
