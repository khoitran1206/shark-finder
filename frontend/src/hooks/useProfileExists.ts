import { useCallback, useEffect, useState } from "react";
import apiClient from "../services/api-client";
import { apiErrorMessage } from "../lib/apiError";

/**
 * Asks the backend whether the signed-in user already has a profile.
 * `exists` is null until known, and stays null if the check fails (see `error`).
 */
export function useProfileExists(url: string, fallbackMessage = "Failed to check profile.") {
  const [checking, setChecking] = useState(true);
  const [exists, setExists] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  const recheck = useCallback(async () => {
    setError(null);
    setChecking(true);
    setExists(null);
    try {
      const res = await apiClient.get(url);
      setExists(Boolean(res?.data?.exists));
    } catch (err) {
      setError(apiErrorMessage(err, fallbackMessage));
    } finally {
      setChecking(false);
    }
  }, [url, fallbackMessage]);

  useEffect(() => {
    recheck();
  }, [recheck]);

  return { checking, exists, error, recheck };
}
