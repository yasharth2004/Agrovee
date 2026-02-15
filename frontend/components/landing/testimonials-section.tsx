"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import Image from "next/image"
import { Star } from "lucide-react"

const testimonials = [
  {
    name: "Rajesh Patel",
    role: "Rice Farmer, Gujarat",
    content:
      "AgriVisionTalk helped me detect leaf blight early and saved 40% of my rice crop. The AI recommendations were spot-on.",
    rating: 5,
    initials: "RP",
  },
  {
    name: "Sarah Thompson",
    role: "Vineyard Owner, Napa Valley",
    content:
      "The weather-aware advisory is a game-changer. I can plan my spraying and irrigation schedules with much more confidence now.",
    rating: 5,
    initials: "ST",
  },
  {
    name: "Amir Hassan",
    role: "Wheat Farmer, Punjab",
    content:
      "The chat assistant feels like having an agronomist in my pocket. Quick, accurate answers whenever I need them. Highly recommend!",
    rating: 5,
    initials: "AH",
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

export function TestimonialsSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-80px" })

  return (
    <section className="relative py-24 md:py-32" ref={ref}>
      {/* Background image blend */}
      <div className="pointer-events-none absolute inset-0">
        <Image
          src="/images/testimonials-farm.jpg"
          alt=""
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-background/50 backdrop-blur-[1px]" />
        <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-transparent to-background/60" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
          className="mx-auto mb-16 max-w-2xl text-center"
        >
          <p className="mb-3 text-sm font-semibold tracking-wider text-primary uppercase">
            Testimonials
          </p>
          <h2 className="font-heading text-3xl font-bold tracking-tight text-foreground md:text-4xl lg:text-5xl">
            <span className="text-balance">Trusted by Farmers Worldwide</span>
          </h2>
          <p className="mt-4 text-pretty text-lg leading-relaxed text-muted-foreground">
            See what our community of farmers has to say about AgriVisionTalk.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          className="grid grid-cols-1 gap-6 md:grid-cols-3"
        >
          {testimonials.map((testimonial) => (
            <motion.div
              key={testimonial.name}
              variants={cardVariants}
              whileHover={{ y: -4 }}
              className="rounded-2xl border border-border/60 bg-card/90 p-6 shadow-sm backdrop-blur-md transition-shadow hover:shadow-md"
            >
              {/* Stars */}
              <div className="mb-4 flex gap-1">
                {Array.from({ length: testimonial.rating }).map((_, i) => (
                  <Star
                    key={i}
                    className="h-4 w-4 fill-amber-400 text-amber-400"
                  />
                ))}
              </div>
              {/* Quote */}
              <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
                &ldquo;{testimonial.content}&rdquo;
              </p>
              {/* Author */}
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                  {testimonial.initials}
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">
                    {testimonial.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {testimonial.role}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
