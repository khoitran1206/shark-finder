import { describe, expect, it } from "vitest";
import { textOr } from "./text";

describe("textOr", () => {
  it("trims real values", () => expect(textOr("  Acme ", "Unknown")).toBe("Acme"));
  it.each([null, undefined, "", "   "])("falls back for %j", (v) => expect(textOr(v, "Unknown")).toBe("Unknown"));
});
