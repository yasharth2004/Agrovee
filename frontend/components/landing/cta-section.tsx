"use client"

import Link from "next/link"
import Image from "next/image"
import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export function CtaSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-80px" })

  return (
    <section id="about" className="py-24 md:py-32" ref={ref}>
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="relative overflow-hidden rounded-3xl shadow-xl"
        >
          {/* Background image with color overlay */}
          <div className="pointer-events-none absolute inset-0">
            <Image
              src="/images/cta-harvest.jpg"
              alt=""
              fill
              className="object-cover"
            />
            <div className="absolute inset-0 bg-primary/60" />
            <div className="absolute inset-0 bg-gradient-to-br from-primary/70 via-primary/40 to-primary/70" />
          </div>

          {/* Dot grid pattern */}
          <div className="pointer-events-none absolute inset-0">
            <svg
              className="absolute inset-0 h-full w-full opacity-[0.08]"
              aria-hidden="true"
            >
              <defs>
                <pattern
                  id="cta-grid"
                  width="30"
                  height="30"
                  patternUnits="userSpaceOnUse"
                >
                  <circle
                    cx="1"
                    cy="1"
                    r="1"
                    fill="currentColor"
                    className="text-primary-foreground"
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#cta-grid)" />
            </svg>
          </div>

          <div className="relative z-10 px-6 py-16 text-center md:px-12 md:py-24">
            <h2 className="font-heading mx-auto max-w-2xl text-3xl font-bold tracking-tight text-primary-foreground md:text-4xl lg:text-5xl">
              <span className="text-balance">
                Ready to Transform Your Farm?
              </span>
            </h2>
            <p className="mx-auto mt-5 max-w-xl text-pretty text-lg leading-relaxed text-primary-foreground/80">
              Join thousands of farmers already using AI to protect their crops,
              optimize resources, and increase their yield.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4">
              <Button
                size="lg"
                variant="secondary"
                className="gap-2 bg-primary-foreground px-8 text-base text-primary hover:bg-primary-foreground/90"
                asChild
              >
                <Link href="/register">
                  Start Free Trial
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-primary-foreground/30 bg-transparent px-8 text-base text-primary-foreground hover:bg-primary-foreground/10 hover:text-primary-foreground"
                asChild
              >
                <Link href="#features">Explore Features</Link>
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
