export type InvestorFormPayload = {
  name: string;
  email: string;
  risk_tolerance: "Low" | "Medium" | "High" | null;
  industry: string | null;
  years_active: number | null;
  num_investments: number | null;
  board_seat: boolean | null;
  location: string | null;
  investment_size: number | null;
  investment_stage: "Pre-seed" | "Seed" | "Series A" | "Series B+" | "Public" | null;
  follow_on_rate: boolean | null;
  rate_of_return: string | null;
  success_rate: string | null;
  reserved_capital: string | null;
  meeting_frequency: "Weekly" | "Monthly" | "Quarterly" | null;
};

export function toIntOrNull(v: FormDataEntryValue | null): number | null {
  if (v == null) return null;
  const s = String(v).trim();
  if (!s) return null;
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}

export function toStrOrNull(v: FormDataEntryValue | null): string | null {
  if (v == null) return null;
  const s = String(v).trim();
  return s.length ? s : null;
}

export function toBoolOrNull(v: FormDataEntryValue | null): boolean | null {
  if (v == null) return null;
  const s = String(v).trim().toLowerCase();
  if (s === "true") return true;
  if (s === "false") return false;
  return null;
}

/** Build the create-profile payload from the form, or null when the required name is empty. */
export function buildInvestorPayload(fd: FormData, email: string): InvestorFormPayload | null {
  const name = toStrOrNull(fd.get("name"));
  if (!name) return null;
  return {
    name,
    email,
    risk_tolerance: toStrOrNull(fd.get("risk_tolerance")) as InvestorFormPayload["risk_tolerance"],
    industry: toStrOrNull(fd.get("industry")),
    years_active: toIntOrNull(fd.get("years_active")),
    num_investments: toIntOrNull(fd.get("num_investments")),
    board_seat: toBoolOrNull(fd.get("board_seat")),
    location: toStrOrNull(fd.get("location")),
    investment_size: toIntOrNull(fd.get("investment_size")),
    investment_stage: toStrOrNull(fd.get("investment_stage")) as InvestorFormPayload["investment_stage"],
    follow_on_rate: toBoolOrNull(fd.get("follow_on_rate")),
    rate_of_return: toStrOrNull(fd.get("rate_of_return")),
    success_rate: toStrOrNull(fd.get("success_rate")),
    reserved_capital: toStrOrNull(fd.get("reserved_capital")),
    meeting_frequency: toStrOrNull(fd.get("meeting_frequency")) as InvestorFormPayload["meeting_frequency"],
  };
}
