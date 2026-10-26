import { AxiosError, type AxiosResponse } from "axios";
import { describe, expect, it } from "vitest";
import { apiErrorMessage } from "./apiError";

const failed = (data: unknown, message = "Request failed with status code 400") =>
  new AxiosError(message, "ERR_BAD_REQUEST", undefined, undefined, { status: 400, data } as AxiosResponse);

describe("apiErrorMessage", () => {
  it("prefers the FastAPI detail string", () =>
    expect(apiErrorMessage(failed({ detail: "Profile already exists for this user" }), "x")).toBe(
      "Profile already exists for this user"
    ));

  it("uses data.message when there is no detail", () =>
    expect(apiErrorMessage(failed({ message: "nope" }), "x")).toBe("nope"));

  it("stringifies structured details (FastAPI 422 validation errors)", () => {
    const detail = [{ loc: ["body", "name"], msg: "field required" }];
    expect(apiErrorMessage(failed({ detail }), "x")).toBe(JSON.stringify(detail));
  });

  it("falls back to the axios message when the body has nothing", () =>
    expect(apiErrorMessage(failed({}), "x")).toBe("Request failed with status code 400"));

  it("handles plain errors and unknown values", () => {
    expect(apiErrorMessage(new Error("boom"), "x")).toBe("boom");
    expect(apiErrorMessage("weird", "Something failed")).toBe("Something failed");
    expect(apiErrorMessage(undefined, "Something failed")).toBe("Something failed");
  });
});
