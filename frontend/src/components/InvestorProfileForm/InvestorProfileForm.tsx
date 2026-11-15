import { SelectField, TextField } from "../form/Fields";

const YES_NO = [
  { value: "true", label: "Yes" },
  { value: "false", label: "No" },
];

type Props = {
  /** Email from the signed-in account; shown read-only. */
  email: string | null;
  submitting: boolean;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
};

export default function InvestorProfileForm({ email, submitting, onSubmit }: Props) {
  return (
    <form onSubmit={onSubmit} className="space-y-6">
      {/* Name + Email (email readonly from Amplify) */}
      <div className="grid gap-4 sm:grid-cols-2">
        <TextField id="name" name="name" label="Name" required placeholder="Your full name" />
        <TextField
          id="email"
          type="email"
          label="Email (from account)"
          value={email ?? ""}
          readOnly
          placeholder="Sign in to populate"
        />
      </div>

      {/* Risk Tolerance / Investment Stage / Meeting Frequency */}
      <div className="grid gap-4 sm:grid-cols-3">
        <SelectField id="risk_tolerance" label="Risk Tolerance" options={["Low", "Medium", "High"]} />
        <SelectField
          id="investment_stage"
          label="Investment Stage"
          options={["Pre-seed", "Seed", "Series A", "Series B+", "Public"]}
        />
        <SelectField
          id="meeting_frequency"
          label="Meeting Frequency"
          options={["Weekly", "Monthly", "Quarterly"]}
        />
      </div>

      {/* Industry / Location */}
      <div className="grid gap-4 sm:grid-cols-2">
        <TextField id="industry" name="industry" label="Industry" placeholder="e.g., FinTech, HealthTech" />
        <TextField id="location" name="location" label="Location" placeholder="City, Country" />
      </div>

      {/* Numeric fields */}
      <div className="grid gap-4 sm:grid-cols-3">
        <TextField id="years_active" name="years_active" type="number" min={0} label="Years Active" placeholder="e.g., 5" />
        <TextField id="num_investments" name="num_investments" type="number" min={0} label="# Investments" placeholder="e.g., 20" />
        <TextField
          id="investment_size"
          name="investment_size"
          type="number"
          min={0}
          label="Investment Size (USD)"
          placeholder="e.g., 250000"
        />
      </div>

      {/* Booleans */}
      <div className="grid gap-4 sm:grid-cols-2">
        <SelectField id="board_seat" label="Board Seat" options={YES_NO} />
        <SelectField id="follow_on_rate" label="Follow-On Participation" options={YES_NO} />
      </div>

      {/* Free-form rate fields */}
      <div className="grid gap-4 sm:grid-cols-3">
        <TextField id="rate_of_return" name="rate_of_return" label="Rate of Return" placeholder="e.g., 18% IRR" />
        <TextField id="success_rate" name="success_rate" label="Success Rate" placeholder="e.g., 30% exits" />
        <TextField
          id="reserved_capital"
          name="reserved_capital"
          label="Reserved Capital"
          placeholder="e.g., 40% fund reserved"
        />
      </div>

      {/* Submit */}
      <div className="pt-2">
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-indigo-500 dark:shadow-none dark:hover:bg-indigo-400 dark:focus-visible:outline-indigo-500"
        >
          {submitting ? "Submitting…" : "Submit"}
        </button>
      </div>
    </form>
  );
}
