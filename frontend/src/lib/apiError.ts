import { isAxiosError } from "axios";

/** Best human-readable message from a failed API call (FastAPI `detail`, then `message`). */
export function apiErrorMessage(err: unknown, fallback: string): string {
  let msg: unknown;
  if (isAxiosError<{ detail?: unknown; message?: unknown }>(err)) {
    msg = err.response?.data?.detail || err.response?.data?.message || err.message;
  } else if (err instanceof Error) {
    msg = err.message;
  }
  msg = msg || fallback;
  return typeof msg === "string" ? msg : JSON.stringify(msg);
}
