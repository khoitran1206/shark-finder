/** Trim a possibly-null API string and fall back when empty. */
export function textOr(value: string | null | undefined, fallback: string) {
  return (value ?? "").trim() || fallback;
}
