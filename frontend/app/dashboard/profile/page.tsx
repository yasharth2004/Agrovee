"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import {
  User,
  Mail,
  Phone,
  MapPin,
  Tractor,
  Save,
  Lock,
  Loader2,
  CheckCircle2,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { useAuth } from "@/lib/auth-context"
import { usersAPI } from "@/lib/api"

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [success, setSuccess] = useState("")
  const [error, setError] = useState("")

  const [profile, setProfile] = useState({
    full_name: user?.full_name || "",
    phone: user?.phone || "",
    location: user?.location || "",
    farm_size: user?.farm_size || "",
  })

  const [passwords, setPasswords] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  })

  const handleSaveProfile = async () => {
    setIsSaving(true)
    setError("")
    setSuccess("")

    try {
      await usersAPI.updateProfile(profile)
      await refreshUser()
      setSuccess("Profile updated successfully!")
      setIsEditing(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update profile")
    } finally {
      setIsSaving(false)
    }
  }

  const handleChangePassword = async () => {
    if (passwords.new_password !== passwords.confirm_password) {
      setError("New passwords do not match")
      return
    }
    if (passwords.new_password.length < 8) {
      setError("New password must be at least 8 characters")
      return
    }

    setIsSaving(true)
    setError("")
    setSuccess("")

    try {
      await usersAPI.changePassword(passwords)
      setSuccess("Password changed successfully!")
      setIsChangingPassword(false)
      setPasswords({ old_password: "", new_password: "", confirm_password: "" })
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to change password")
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-heading text-2xl font-bold text-foreground">
          My Profile
        </h1>
        <p className="mt-1 text-muted-foreground">
          Manage your account settings and preferences.
        </p>
      </motion.div>

      {/* Status messages */}
      {success && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
        >
          <CheckCircle2 className="h-4 w-4" />
          {success}
        </motion.div>
      )}

      {error && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
        >
          {error}
        </motion.div>
      )}

      {/* Profile Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-xl border border-border/60 bg-card p-6 shadow-sm"
      >
        {/* Avatar section */}
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-2xl font-bold text-primary">
            {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "U"}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              {user?.full_name || "User"}
            </h2>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Member since{" "}
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString("en-US", {
                    month: "long",
                    year: "numeric",
                  })
                : "N/A"}
            </p>
          </div>
        </div>

        <Separator className="my-6" />

        {/* Profile fields */}
        <div className="space-y-4">
          <div className="space-y-2">
            <Label className="flex items-center gap-2 text-xs">
              <User className="h-3.5 w-3.5" />
              Full Name
            </Label>
            {isEditing ? (
              <Input
                value={profile.full_name}
                onChange={(e) =>
                  setProfile((p) => ({ ...p, full_name: e.target.value }))
                }
                className="h-10"
              />
            ) : (
              <p className="text-sm text-foreground">
                {user?.full_name || "Not set"}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label className="flex items-center gap-2 text-xs">
              <Mail className="h-3.5 w-3.5" />
              Email
            </Label>
            <p className="text-sm text-foreground">{user?.email}</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-xs">
                <Phone className="h-3.5 w-3.5" />
                Phone
              </Label>
              {isEditing ? (
                <Input
                  value={profile.phone}
                  onChange={(e) =>
                    setProfile((p) => ({ ...p, phone: e.target.value }))
                  }
                  className="h-10"
                />
              ) : (
                <p className="text-sm text-foreground">
                  {user?.phone || "Not set"}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-xs">
                <MapPin className="h-3.5 w-3.5" />
                Location
              </Label>
              {isEditing ? (
                <Input
                  value={profile.location}
                  onChange={(e) =>
                    setProfile((p) => ({ ...p, location: e.target.value }))
                  }
                  className="h-10"
                />
              ) : (
                <p className="text-sm text-foreground">
                  {user?.location || "Not set"}
                </p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label className="flex items-center gap-2 text-xs">
              <Tractor className="h-3.5 w-3.5" />
              Farm Size
            </Label>
            {isEditing ? (
              <Input
                value={profile.farm_size}
                onChange={(e) =>
                  setProfile((p) => ({ ...p, farm_size: e.target.value }))
                }
                placeholder="e.g. 5 acres"
                className="h-10"
              />
            ) : (
              <p className="text-sm text-foreground">
                {user?.farm_size || "Not set"}
              </p>
            )}
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          {isEditing ? (
            <>
              <Button
                variant="outline"
                onClick={() => {
                  setIsEditing(false)
                  setProfile({
                    full_name: user?.full_name || "",
                    phone: user?.phone || "",
                    location: user?.location || "",
                    farm_size: user?.farm_size || "",
                  })
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSaveProfile}
                disabled={isSaving}
                className="gap-2"
              >
                {isSaving ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                Save Changes
              </Button>
            </>
          ) : (
            <Button variant="outline" onClick={() => setIsEditing(true)}>
              Edit Profile
            </Button>
          )}
        </div>
      </motion.div>

      {/* Change Password */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-border/60 bg-card p-6 shadow-sm"
      >
        <div className="flex items-center gap-2">
          <Lock className="h-5 w-5 text-muted-foreground" />
          <h3 className="font-semibold text-foreground">Security</h3>
        </div>

        {isChangingPassword ? (
          <div className="mt-4 space-y-4">
            <div className="space-y-2">
              <Label>Current Password</Label>
              <Input
                type="password"
                value={passwords.old_password}
                onChange={(e) =>
                  setPasswords((p) => ({ ...p, old_password: e.target.value }))
                }
                className="h-10"
              />
            </div>
            <div className="space-y-2">
              <Label>New Password</Label>
              <Input
                type="password"
                value={passwords.new_password}
                onChange={(e) =>
                  setPasswords((p) => ({ ...p, new_password: e.target.value }))
                }
                placeholder="Min. 8 characters"
                className="h-10"
              />
            </div>
            <div className="space-y-2">
              <Label>Confirm New Password</Label>
              <Input
                type="password"
                value={passwords.confirm_password}
                onChange={(e) =>
                  setPasswords((p) => ({
                    ...p,
                    confirm_password: e.target.value,
                  }))
                }
                className="h-10"
              />
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setIsChangingPassword(false)
                  setPasswords({
                    old_password: "",
                    new_password: "",
                    confirm_password: "",
                  })
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={handleChangePassword}
                disabled={isSaving}
                className="gap-2"
              >
                {isSaving ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Lock className="h-4 w-4" />
                )}
                Update Password
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-3">
            <p className="text-sm text-muted-foreground">
              Change your password to keep your account secure.
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-3"
              onClick={() => setIsChangingPassword(true)}
            >
              Change Password
            </Button>
          </div>
        )}
      </motion.div>
    </div>
  )
}
