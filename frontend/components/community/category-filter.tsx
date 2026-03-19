"use client"

const CATEGORIES = [
  { id: "all", label: "All Posts", icon: "🌾" },
  { id: "pest_control", label: "Pest Control", icon: "🦗" },
  { id: "irrigation", label: "Irrigation", icon: "💧" },
  { id: "soil_health", label: "Soil Health", icon: "🌱" },
  { id: "weather", label: "Weather & Climate", icon: "☀️" },
  { id: "crop_varieties", label: "Crop Varieties", icon: "🌽" },
  { id: "equipment", label: "Equipment & Tools", icon: "🔧" },
  { id: "general", label: "General Discussion", icon: "💬" },
] as const

export type CommunityCategoryId = (typeof CATEGORIES)[number]["id"]

interface CategoryFilterProps {
  selectedCategory: CommunityCategoryId
  onSelectCategory: (category: CommunityCategoryId) => void
}

export function CategoryFilter({
  selectedCategory,
  onSelectCategory,
}: CategoryFilterProps) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="font-heading text-lg font-semibold text-foreground">
          Categories
        </h3>
        <p className="text-sm text-muted-foreground">
          Browse discussions by topic
        </p>
      </div>

      <div className="space-y-2">
        {CATEGORIES.map((category) => (
          <button
            key={category.id}
            onClick={() => onSelectCategory(category.id)}
            className={`w-full rounded-lg px-4 py-3 text-left text-sm font-medium transition-all ${
              selectedCategory === category.id
                ? "bg-primary text-primary-foreground shadow-md"
                : "bg-card text-foreground hover:bg-accent"
            }`}
          >
            <span className="mr-3">{category.icon}</span>
            {category.label}
          </button>
        ))}
      </div>
    </div>
  )
}
