"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import Image from "next/image"
import { Camera, Brain, FileCheck } from "lucide-react"

const steps = [
  {
    number: "01",
    icon: Camera,
    title: "Upload Your Crop Image",
    description:
      "Simply take a photo of your crop using your smartphone and upload it to our platform. Our system accepts images from any device.",
  },
  {
    number: "02",
    icon: Brain,
    title: "AI Analyzes Your Crop",
    description:
      "Our deep learning model processes the image in seconds, detecting diseases, assessing health, and cross-referencing weather data.",
  },
  {
    number: "03",
    icon: FileCheck,
    title: "Get Actionable Insights",
    description:
      "Receive detailed reports with disease identification, risk assessment, and tailored recommendations for treatment and prevention.",
  },
]

export function HowItWorksSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-80px" })

  return (
    <section id="how-it-works" className="relative py-24 md:py-32" ref={ref}>
      {/* Background image blend */}
      <div className="pointer-events-none absolute inset-0">
        <Image
          src="/images/how-it-works-bg.jpg"
          alt=""
          fill
          sizes="100vw"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-background/85 backdrop-blur-sm" />
        <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background" />
      </div>

      {/* Accent stripe */}
      <div className="pointer-events-none absolute inset-0 bg-accent/20" />

      <div className="relative mx-auto max-w-7xl px-6">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
          className="mx-auto mb-20 max-w-2xl text-center"
        >
          <p className="mb-3 text-sm font-semibold tracking-wider text-primary uppercase">
            How It Works
          </p>
          <h2 className="font-heading text-3xl font-bold tracking-tight text-foreground md:text-4xl lg:text-5xl">
            <span className="text-balance">
              Three Simple Steps to Smarter Farming
            </span>
          </h2>
          <p className="mt-4 text-pretty text-lg leading-relaxed text-muted-foreground">
            Get started in minutes. No complex setup required.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative grid grid-cols-1 gap-12 md:grid-cols-3 md:gap-8">
          {/* Connector line */}
          <div className="pointer-events-none absolute top-16 right-0 left-0 hidden h-px bg-border md:block" />

          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.15 * index }}
              className="relative flex flex-col items-center text-center"
            >
              {/* Step number ring */}
              <motion.div
                whileHover={{ scale: 1.05, rotate: 3 }}
                className="relative z-10 mb-6 flex h-32 w-32 items-center justify-center"
              >
                <div className="absolute inset-0 rounded-full border-2 border-dashed border-primary/30" />
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary shadow-lg shadow-primary/20">
                  <step.icon className="h-9 w-9 text-primary-foreground" />
                </div>
                <span className="absolute -top-1 -right-1 flex h-8 w-8 items-center justify-center rounded-full bg-card text-xs font-bold text-foreground shadow-sm ring-2 ring-border">
                  {step.number}
                </span>
              </motion.div>

              <h3 className="font-heading mb-3 text-xl font-semibold text-foreground">
                {step.title}
              </h3>
              <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
