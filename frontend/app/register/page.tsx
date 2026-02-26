"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Leaf, Eye, EyeOff, ArrowRight, Loader2, CheckCircle2, Sun, Moon } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/lib/auth-context"

export default function RegisterPage() {
  const router = useRouter()
  const { register } = useAuth()
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirm_password: "",
    full_name: "",
    phone: "",
    location: "",
    farm_size: "",
  })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState(1)
  const { resolvedTheme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match")
      return
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters")
      return
    }

    setIsLoading(true)

    try {
      await register(formData)
      router.push("/login?registered=true")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left panel - form */}
      <div className="flex w-full flex-col justify-center px-6 py-12 lg:w-1/2 lg:px-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mx-auto w-full max-w-md"
        >
          <div className="mb-10 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                <Leaf className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="font-heading text-lg font-bold text-foreground">
                Agrovee
              </span>
            </Link>
            {mounted && (
              <button
                onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
                className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                aria-label="Toggle theme"
              >
                {resolvedTheme === "dark" ? (
                  <Sun className="h-4 w-4" />
                ) : (
                  <Moon className="h-4 w-4" />
                )}
              </button>
            )}
          </div>

          <h1 className="font-heading text-3xl font-bold tracking-tight text-foreground">
            Create your account
          </h1>
          <p className="mt-2 text-muted-foreground">
            Join thousands of farmers using AI to protect their crops.
          </p>

          {/* Step indicators */}
          <div className="mt-6 flex items-center gap-3">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${
                step >= 1
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {step > 1 ? <CheckCircle2 className="h-4 w-4" /> : "1"}
            </div>
            <div className={`h-0.5 flex-1 ${step > 1 ? "bg-primary" : "bg-muted"}`} />
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${
                step >= 2
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              2
            </div>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mt-4 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            {step === 1 && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-4"
              >
                <div className="space-y-2">
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input
                    id="full_name"
                    placeholder="John Doe"
                    value={formData.full_name}
                    onChange={(e) => updateField("full_name", e.target.value)}
                    className="h-11"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">
                    Email Address <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="farmer@example.com"
                    value={formData.email}
                    onChange={(e) => updateField("email", e.target.value)}
                    required
                    className="h-11"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">
                    Password <span className="text-destructive">*</span>
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Min. 8 characters"
                      value={formData.password}
                      onChange={(e) => updateField("password", e.target.value)}
                      required
                      minLength={8}
                      className="h-11 pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm_password">
                    Confirm Password <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    placeholder="Confirm your password"
                    value={formData.confirm_password}
                    onChange={(e) => updateField("confirm_password", e.target.value)}
                    required
                    className="h-11"
                  />
                </div>

                <Button
                  type="button"
                  className="h-11 w-full gap-2"
                  onClick={() => {
                    if (!formData.email || !formData.password || !formData.confirm_password) {
                      setError("Please fill in all required fields")
                      return
                    }
                    if (formData.password !== formData.confirm_password) {
                      setError("Passwords do not match")
                      return
                    }
                    setError("")
                    setStep(2)
                  }}
                >
                  Continue
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-4"
              >
                <p className="text-sm text-muted-foreground">
                  Optional: Help us personalize your experience.
                </p>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    placeholder="+91 9876543210"
                    value={formData.phone}
                    onChange={(e) => updateField("phone", e.target.value)}
                    className="h-11"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    placeholder="City, State or Region"
                    value={formData.location}
                    onChange={(e) => updateField("location", e.target.value)}
                    className="h-11"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="farm_size">Farm Size</Label>
                  <Input
                    id="farm_size"
                    placeholder="e.g. 5 acres"
                    value={formData.farm_size}
                    onChange={(e) => updateField("farm_size", e.target.value)}
                    className="h-11"
                  />
                </div>

                <div className="flex gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    className="h-11 flex-1"
                    onClick={() => setStep(1)}
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    className="h-11 flex-1 gap-2"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        Create Account
                        <ArrowRight className="h-4 w-4" />
                      </>
                    )}
                  </Button>
                </div>
              </motion.div>
            )}
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-semibold text-primary hover:underline"
            >
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>

      {/* Right panel - decoration */}
      <div className="relative hidden lg:block lg:w-1/2">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/90 via-primary/70 to-primary/90" />
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{ backgroundImage: "url('/images/features-field.jpg')" }}
        />
        <div className="relative flex h-full flex-col items-center justify-center px-12 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <Leaf className="mx-auto mb-6 h-16 w-16 text-primary-foreground/80" />
            <h2 className="font-heading text-3xl font-bold text-primary-foreground">
              Start Your Smart Farming Journey
            </h2>
            <p className="mt-4 max-w-md text-lg text-primary-foreground/70">
              Get instant crop disease detection, weather-aware advisories,
              and personalized recommendations powered by AI.
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
