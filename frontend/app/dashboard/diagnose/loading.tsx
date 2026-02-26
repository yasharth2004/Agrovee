import { Skeleton } from "@/components/ui/skeleton"

export default function DiagnoseLoading() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-80" />
      </div>

      {/* Upload area skeleton */}
      <div className="rounded-xl border-2 border-dashed border-muted-foreground/25 p-12">
        <div className="flex flex-col items-center justify-center space-y-4">
          <Skeleton className="h-16 w-16 rounded-full" />
          <Skeleton className="h-5 w-52" />
          <Skeleton className="h-4 w-36" />
        </div>
      </div>

      {/* Form fields */}
      <div className="grid gap-4 sm:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-10 w-full rounded-md" />
          </div>
        ))}
      </div>
    </div>
  )
}
