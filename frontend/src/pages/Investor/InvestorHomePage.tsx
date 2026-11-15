import { useState, useEffect, useMemo } from "react";
import { useAuthenticator } from "@aws-amplify/ui-react";
import apiClient, { abortAllRequests } from "../../services/api-client";
import { apiErrorMessage } from "../../lib/apiError";
import { buildInvestorPayload } from "../../lib/investorPayload";
import { useProfileExists } from "../../hooks/useProfileExists";
import Navbar from "../../components/Navbar/Navbar";
import LoadingScreen from "../../components/LoadingScreen";
import InvestorProfileForm from "../../components/InvestorProfileForm";
import MatchInvestorToFirmsList from "../../components/MatchInvestorToFirmsList";

const POST_URL = "/investor/create-profile";
const EXISTS_URL = "/investor/exists";

export default function InvestorHomePage() {
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [ok, setOk] = useState(false);

  const { checking, exists, error: existsError, recheck } = useProfileExists(
    EXISTS_URL,
    "Failed to check investor existence."
  );
  const error = submitError ?? existsError;

  const { user } = useAuthenticator((ctx) => [ctx.user]);

  const emailFromAuth = useMemo<string | null>(() => {
    // @ts-expect-error: Amplify user shape varies
    const attrEmail = user?.attributes?.email ?? user?.signInDetails?.loginId ?? user?.username;
    return typeof attrEmail === "string" && attrEmail.includes("@") ? attrEmail : null;
  }, [user]);

  useEffect(() => () => abortAllRequests(), []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitError(null);
    setOk(false);

    if (!emailFromAuth) {
      setSubmitError("No authenticated email found. Sign in again.");
      return;
    }

    const form = e.currentTarget; // capture before await
    const payload = buildInvestorPayload(new FormData(form), emailFromAuth);
    if (!payload) {
      setSubmitError("Name is required.");
      return;
    }

    setSubmitting(true);
    try {
      await apiClient.post(POST_URL, payload);
      setOk(true);
      form.reset();
      // Re-check existence after successful creation
      await recheck();
    } catch (err) {
      setSubmitError(apiErrorMessage(err, "Failed to submit investor profile."));
    } finally {
      setSubmitting(false);
    }
  }

  if (checking) {
    return (
      <>
        <Navbar />
        <LoadingScreen />
      </>
    );
  }

  // Profile exists → show matches
  if (exists === true) {
    return (
      <>
        <Navbar />

        <div className="max-w-7xl  mx-auto">
          <MatchInvestorToFirmsList />
        </div>
      </>
    );
  }

  // No profile yet (or the exists check failed): show the form and any error banner
  return (
    <>
      <Navbar />
      <div className="mx-auto max-w-3xl p-6">
        <h1 className="mb-6 text-3xl font-semibold tracking-tight dark:text-white">Investor Profile</h1>

        {error && (
          <div className="mb-4 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900 dark:border-amber-900/40 dark:bg-amber-900/20 dark:text-amber-200">
            {error}
            <div className="mt-2">
              <button
                type="button"
                onClick={() => {
                  setSubmitError(null);
                  recheck();
                }}
                className="rounded-md bg-gray-900 px-3 py-1 text-xs font-medium text-white hover:opacity-90 dark:bg-gray-700"
              >
                Retry check
              </button>
            </div>
          </div>
        )}

        {ok && (
          <div className="mb-4 rounded-md border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-900 dark:border-emerald-900/40 dark:bg-emerald-900/20 dark:text-emerald-200">
            Saved
          </div>
        )}

        <InvestorProfileForm email={emailFromAuth} submitting={submitting} onSubmit={handleSubmit} />
      </div>
    </>
  );
}
