"use client"

import { useState } from "react"
import Link from "next/link"
import { authAPI } from "@/lib/api"
import { toast } from "sonner"

type Step = "email" | "code" | "done"

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<Step>("email")
  const [email, setEmail] = useState("")
  const [code, setCode] = useState("")
  const [resetCode, setResetCode] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const handleRequestCode = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      const res = await authAPI.forgotPassword(email)
      // In demo mode, the API returns the code directly
      if (res.data.reset_code) {
        setResetCode(res.data.reset_code)
      }
      toast.success("Reset code generated!")
      setStep("code")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to send reset code")
    } finally {
      setIsLoading(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match")
      return
    }
    setIsLoading(true)
    setError("")

    try {
      await authAPI.resetPassword(code, newPassword, confirmPassword)
      toast.success("Password reset successfully!")
      setStep("done")
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to reset password")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-green-50 to-white dark:from-green-950/20 dark:to-background px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="font-heading text-3xl font-bold text-foreground">
            Reset Password
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {step === "email" && "Enter your email to receive a reset code"}
            {step === "code" && "Enter the reset code and your new password"}
            {step === "done" && "Your password has been reset"}
          </p>
        </div>

        <div className="rounded-xl border bg-card p-6 shadow-sm">
          {error && (
            <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-900/20 p-3 text-sm text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          {step === "email" && (
            <form onSubmit={handleRequestCode} className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-foreground">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                  placeholder="your@email.com"
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-green-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {isLoading ? "Sending..." : "Send Reset Code"}
              </button>
            </form>
          )}

          {step === "code" && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              {resetCode && (
                <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 p-3 text-sm text-blue-700 dark:text-blue-300">
                  <span className="font-medium">Demo mode:</span> Your reset code is{" "}
                  <code className="rounded bg-blue-100 dark:bg-blue-800/50 px-1.5 py-0.5 font-mono font-bold">
                    {resetCode}
                  </code>
                </div>
              )}
              <div>
                <label className="mb-1 block text-sm font-medium text-foreground">Reset Code</label>
                <input
                  type="text"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  required
                  maxLength={6}
                  className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm font-mono tracking-widest text-center focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                  placeholder="000000"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-foreground">New Password</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                  placeholder="Min. 8 characters"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-foreground">Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                  placeholder="Repeat password"
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-green-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {isLoading ? "Resetting..." : "Reset Password"}
              </button>
            </form>
          )}

          {step === "done" && (
            <div className="text-center py-4">
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Your password has been reset. You can now log in.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center rounded-lg bg-green-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-green-700 transition-colors"
              >
                Go to Login
              </Link>
            </div>
          )}
        </div>

        <p className="mt-4 text-center text-sm text-muted-foreground">
          Remember your password?{" "}
          <Link href="/login" className="font-medium text-green-600 hover:text-green-500">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
