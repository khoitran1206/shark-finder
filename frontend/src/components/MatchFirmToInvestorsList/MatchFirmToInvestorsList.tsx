import MatchList from "../MatchList";
import type { MatchRow } from "../MatchList";
import { textOr } from "../../lib/text";

type MatchApiItem = {
  investor: {
    name: string | null;
    email: string | null;
    num_investments: number | null;
    industry: string | null;
    location: string | null;
  };
  match_score: number;
};

function toRow(item: MatchApiItem): MatchRow {
  const i = item?.investor ?? ({} as Partial<MatchApiItem["investor"]>);
  return {
    name: textOr(i.name, "Unknown"),
    email: textOr(i.email, "unknown@example.com"),
    industry: i.industry ?? null,
    location: i.location ?? null,
    metric: typeof i.num_investments === "number" ? i.num_investments : null,
  };
}

const endpoint = (firmId: string) => `/firms/${firmId}/matching-investors`;

export default function MatchFirmToInvestorsList() {
  return (
    <MatchList
      title="Your Investor Matches"
      endpoint={endpoint}
      metricLabel="# of Investments"
      toRow={toRow}
    />
  );
}
