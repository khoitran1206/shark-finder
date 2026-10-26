import { describe, expect, it } from "vitest";
import { buildInvestorPayload, toBoolOrNull, toIntOrNull, toStrOrNull } from "./investorPayload";

describe("form value parsers", () => {
  it("toIntOrNull", () => {
    expect(toIntOrNull("42")).toBe(42);
    expect(toIntOrNull(" 7 ")).toBe(7);
    expect(toIntOrNull("0")).toBe(0);
    expect([toIntOrNull(""), toIntOrNull("  "), toIntOrNull("abc"), toIntOrNull(null)]).toEqual([null, null, null, null]);
  });

  it("toStrOrNull", () => {
    expect(toStrOrNull("  hi ")).toBe("hi");
    expect([toStrOrNull(""), toStrOrNull("  "), toStrOrNull(null)]).toEqual([null, null, null]);
  });

  it("toBoolOrNull", () => {
    expect(toBoolOrNull("true")).toBe(true);
    expect(toBoolOrNull("FALSE")).toBe(false);
    expect([toBoolOrNull(""), toBoolOrNull("yes"), toBoolOrNull(null)]).toEqual([null, null, null]);
  });
});

function form(values: Record<string, string>) {
  const fd = new FormData();
  Object.entries(values).forEach(([k, v]) => fd.set(k, v));
  return fd;
}

describe("buildInvestorPayload", () => {
  it("requires a name", () => {
    expect(buildInvestorPayload(form({ name: "   " }), "a@b.co")).toBeNull();
    expect(buildInvestorPayload(form({}), "a@b.co")).toBeNull();
  });

  it("maps blanks to null and uses the account email, not a form value", () => {
    const p = buildInvestorPayload(form({ name: "Ada", email: "evil@x.co", industry: "", years_active: "" }), "ada@x.co");
    expect(p).toMatchObject({ name: "Ada", email: "ada@x.co", industry: null, years_active: null, board_seat: null });
  });

  it("parses every field type", () => {
    const p = buildInvestorPayload(
      form({
        name: "Ada",
        risk_tolerance: "High",
        investment_stage: "Series A",
        meeting_frequency: "Monthly",
        years_active: "5",
        num_investments: "20",
        investment_size: "250000",
        board_seat: "true",
        follow_on_rate: "false",
        rate_of_return: "18% IRR",
      }),
      "ada@x.co"
    );
    expect(p).toMatchObject({
      risk_tolerance: "High",
      investment_stage: "Series A",
      meeting_frequency: "Monthly",
      years_active: 5,
      num_investments: 20,
      investment_size: 250000,
      board_seat: true,
      follow_on_rate: false,
      rate_of_return: "18% IRR",
      success_rate: null,
    });
  });
});
