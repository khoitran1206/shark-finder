import MatchList from "../MatchList";
import type { MatchRow } from "../MatchList";
import { textOr } from "../../lib/text";

type MatchApiItem = {
  firm: {
    name: string | null;
    email: string | null;
    industry: string | null;
    location: string | null;
  };
  match_score: number;
};

function toRow(item: MatchApiItem): MatchRow {
  const f = item?.firm ?? ({} as Partial<MatchApiItem["firm"]>);
  return {
    name: textOr(f.name, "Unknown"),
    email: textOr(f.email, "unknown@example.com"),
    industry: f.industry ?? null,
    location: f.location ?? null,
    metric: Math.round(typeof item?.match_score === "number" ? item.match_score : 0),
  };
}

const endpoint = (investorId: string) => `/investors/${investorId}/matching-firms`;

export default function MatchInvestorToFirmsList() {
  return (
    <MatchList
      title="Your Startup Matches"
      endpoint={endpoint}
      metricLabel="Match Score"
      toRow={toRow}
    />
  );
}
