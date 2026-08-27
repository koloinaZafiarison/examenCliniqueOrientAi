"use client"

import { SCENARIOS } from "@/lib/scenarios"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type ScenarioDropdownProps = {
  value?: string | null
  disabled?: boolean
  onValueChange: (scenarioId: string) => void
}

const selectItems = SCENARIOS.map((scenario) => ({
  value: scenario.id,
  label: scenario.label,
}))

export function ScenarioDropdown({
  value = null,
  disabled,
  onValueChange,
}: ScenarioDropdownProps) {
  return (
    <Select
      items={selectItems}
      value={value}
      disabled={disabled}
      onValueChange={(next) => {
        if (next) onValueChange(next)
      }}
    >
      <SelectTrigger
        className="scenario-select-trigger w-full max-w-full"
        aria-label="Choisir un scénario d’orientation"
      >
        <SelectValue placeholder="Choisir un scénario prédéfini…" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          {SCENARIOS.map((scenario) => (
            <SelectItem key={scenario.id} value={scenario.id}>
              {scenario.label}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}
