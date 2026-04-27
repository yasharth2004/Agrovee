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
  Calendar,
  Shield,
  EditIcon,
  X,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { useAuth } from "@/lib/auth-context"
import { usersAPI } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const { toast } = useToast()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

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

    try {
      const dataToSend = {
        full_name: profile.full_name || null,
        phone: profile.phone || null,
        location: profile.location || null,
        farm_size: profile.farm_size || null,
      }
      
      console.log("🔄 Saving profile with data:", dataToSend)
      console.log("🔗 API URL:", window.location.origin)
      
      const response = await usersAPI.updateProfile(dataToSend)
      console.log("✅ Profile update response:", response)
      
      await refreshUser()
      toast({
        title: "Success",
        description: "Profile updated successfully!",
      })
      setIsEditing(false)
    } catch (err: any) {
      console.error("❌ Profile update error:", err)
      console.error("Error code:", err.code)
      console.error("Error message:", err.message)
      console.error("Error response:", err.response?.data)
      console.error("Error status:", err.response?.status)
      
      // Check connection
      if (err.message === "Network Error") {
        console.error("🌐 Network connectivity issue - backend might not be running")
      }
      
      const errorMessage = 
        err.response?.data?.detail || 
        err.message || 
        "Failed to update profile"
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleChangePassword = async () => {
    if (passwords.new_password !== passwords.confirm_password) {
      toast({
        title: "Error",
        description: "New passwords do not match",
        variant: "destructive",
      })
      return
    }
    if (passwords.new_password.length < 8) {
      toast({
        title: "Error",
        description: "New password must be at least 8 characters",
        variant: "destructive",
      })
      return
    }

    setIsSaving(true)

    try {
      await usersAPI.changePassword(passwords)
      toast({
        title: "Success",
        description: "Password changed successfully!",
      })
      setIsChangingPassword(false)
      setPasswords({ old_password: "", new_password: "", confirm_password: "" })
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.response?.data?.detail || "Failed to change password",
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border border-primary/20 p-8"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/60 text-4xl font-bold text-white shadow-lg"
            >
              {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "U"}
            </motion.div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">{user?.full_name || "User"}</h1>
              <p className="text-muted-foreground mt-1">{user?.email}</p>
              <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  Member since{" "}
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        year: "numeric",
                      })
                    : "N/A"}
                </div>
                {user?.is_verified && (
                  <div className="flex items-center gap-1 text-green-600">
                    <CheckCircle2 className="h-4 w-4" />
                    Verified
                  </div>
                )}
              </div>
            </div>
          </div>
          {!isEditing && (
            <Button
              onClick={() => setIsEditing(true)}
              className="gap-2"
              size="lg"
            >
              <EditIcon className="h-4 w-4" />
              Edit Profile
            </Button>
          )}
        </div>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile Information - Main Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Profile Details Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="p-6 border border-border/60">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                  <User className="h-5 w-5 text-primary" />
                  Account Information
                </h2>
                {isEditing && (
                  <Button
                    variant="ghost"
                    size="sm"
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
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>

              <div className="space-y-5">
                {/* Full Name */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    Full Name
                  </Label>
                  {isEditing ? (
                    <Input
                      value={profile.full_name}
                      onChange={(e) =>
                        setProfile((p) => ({ ...p, full_name: e.target.value }))
                      }
                      className="h-11 bg-muted/30"
                      placeholder="Enter your full name"
                    />
                  ) : (
                    <div className="h-11 rounded-lg bg-muted/30 px-4 py-2.5 text-sm text-foreground flex items-center">
                      {user?.full_name || <span className="text-muted-foreground">Not set</span>}
                    </div>
                  )}
                </div>

                {/* Email */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    Email Address
                  </Label>
                  <div className="h-11 rounded-lg bg-muted/30 px-4 py-2.5 text-sm text-foreground flex items-center cursor-not-allowed opacity-70">
                    {user?.email}
                  </div>
                  <p className="text-xs text-muted-foreground">Email cannot be changed</p>
                </div>

                {/* Phone and Location */}
                <div className="grid gap-5 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-foreground flex items-center gap-2">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      Phone
                    </Label>
                    {isEditing ? (
                      <Input
                        value={profile.phone}
                        onChange={(e) =>
                          setProfile((p) => ({ ...p, phone: e.target.value }))
                        }
                        type="tel"
                        className="h-11 bg-muted/30"
                        placeholder="e.g. +1 234 567 8900"
                      />
                    ) : (
                      <div className="h-11 rounded-lg bg-muted/30 px-4 py-2.5 text-sm text-foreground flex items-center">
                        {user?.phone || <span className="text-muted-foreground">Not set</span>}
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-foreground flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      Location
                    </Label>
                    {isEditing ? (
                      <Input
                        value={profile.location}
                        onChange={(e) =>
                          setProfile((p) => ({ ...p, location: e.target.value }))
                        }
                        className="h-11 bg-muted/30"
                        placeholder="Farm location"
                      />
                    ) : (
                      <div className="h-11 rounded-lg bg-muted/30 px-4 py-2.5 text-sm text-foreground flex items-center">
                        {user?.location || <span className="text-muted-foreground">Not set</span>}
                      </div>
                    )}
                  </div>
                </div>

                {/* Farm Size */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <Tractor className="h-4 w-4 text-muted-foreground" />
                    Farm Size
                  </Label>
                  {isEditing ? (
                    <Input
                      value={profile.farm_size}
                      onChange={(e) =>
                        setProfile((p) => ({ ...p, farm_size: e.target.value }))
                      }
                      className="h-11 bg-muted/30"
                      placeholder="e.g. 5 acres, 2 hectares"
                    />
                  ) : (
                    <div className="h-11 rounded-lg bg-muted/30 px-4 py-2.5 text-sm text-foreground flex items-center">
                      {user?.farm_size || <span className="text-muted-foreground">Not set</span>}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              {isEditing && (
                <div className="flex gap-3 mt-6 pt-6 border-t border-border/40">
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
                    className="gap-2 flex-1"
                  >
                    {isSaving ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Save Changes
                  </Button>
                </div>
              )}
            </Card>
          </motion.div>
        </div>

        {/* Sidebar - Security */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="p-6 border border-border/60 bg-gradient-to-br from-amber-50/40 to-transparent">
              <div className="flex items-center gap-2 mb-4">
                <Lock className="h-5 w-5 text-amber-600" />
                <h3 className="font-semibold text-foreground">Security</h3>
              </div>

              <p className="text-sm text-muted-foreground mb-4">
                Keep your account secure by updating your password regularly.
              </p>

              {!isChangingPassword ? (
                <Button
                  variant="outline"
                  className="w-full gap-2"
                  onClick={() => setIsChangingPassword(true)}
                >
                  <Shield className="h-4 w-4" />
                  Change Password
                </Button>
              ) : (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-sm">Current Password</Label>
                    <Input
                      type="password"
                      value={passwords.old_password}
                      onChange={(e) =>
                        setPasswords((p) => ({ ...p, old_password: e.target.value }))
                      }
                      className="h-10 bg-muted/30"
                      placeholder="Enter current password"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm">New Password</Label>
                    <Input
                      type={showPassword ? "text" : "password"}
                      value={passwords.new_password}
                      onChange={(e) =>
                        setPasswords((p) => ({ ...p, new_password: e.target.value }))
                      }
                      className="h-10 bg-muted/30"
                      placeholder="Min. 8 characters"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm">Confirm New Password</Label>
                    <Input
                      type={showPassword ? "text" : "password"}
                      value={passwords.confirm_password}
                      onChange={(e) =>
                        setPasswords((p) => ({
                          ...p,
                          confirm_password: e.target.value,
                        }))
                      }
                      className="h-10 bg-muted/30"
                      placeholder="Confirm new password"
                    />
                  </div>

                  <div className="flex gap-3 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
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
                      size="sm"
                      className="flex-1 gap-2"
                      onClick={handleChangePassword}
                      disabled={isSaving}
                    >
                      {isSaving ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Shield className="h-4 w-4" />
                      )}
                      Update
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </motion.div>

          {/* Verification Status Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className={`p-6 border ${
              user?.is_verified
                ? "bg-gradient-to-br from-green-50/40 to-transparent border-green-200/50"
                : "bg-gradient-to-br from-blue-50/40 to-transparent border-blue-200/50"
            }`}>
              <div className="flex items-center gap-2 mb-3">
                {user?.is_verified ? (
                  <>
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <h3 className="font-semibold text-green-900">Verified</h3>
                  </>
                ) : (
                  <>
                    <Shield className="h-5 w-5 text-blue-600" />
                    <h3 className="font-semibold text-blue-900">Pending Verification</h3>
                  </>
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                {user?.is_verified
                  ? "Your account has been verified."
                  : "Complete verification to unlock all features."}
              </p>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
