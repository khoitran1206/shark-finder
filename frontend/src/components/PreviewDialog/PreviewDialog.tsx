type Props = {
  blobUrl: string | null;
  uploading: boolean;
  uploaded: boolean;
  /** False while there is no recorded data to submit. */
  canSubmit: boolean;
  err: string | null;
  onClose: () => void;
  onSubmit: () => void;
};

export default function PreviewDialog({
  blobUrl,
  uploading,
  uploaded,
  canSubmit,
  err,
  onClose,
  onSubmit,
}: Props) {
  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Recording preview"
      onKeyDown={(e) => e.key === "Escape" && onClose()}
    >
      <div className="w-full max-w-3xl rounded-2xl border border-gray-200 bg-white p-4 shadow-2xl dark:border-gray-800 dark:bg-gray-900">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-semibold">Preview your pitch</h3>
          <button
            onClick={onClose}
            className="rounded-md cursor-pointer p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
            aria-label="Close preview"
            title="Close"
          >
            ✕
          </button>
        </div>

        <div className="overflow-hidden rounded-lg">
          {blobUrl ? (
            <video src={blobUrl} controls className="h-auto w-full" />
          ) : (
            <div className="flex h-60 items-center justify-center text-sm text-gray-500">
              No preview available
            </div>
          )}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-700"
            >
              Re-record
            </button>
            <button
              onClick={onSubmit}
              disabled={uploading || uploaded || !canSubmit}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {uploaded ? "Submitted" : uploading ? "Submitting..." : "Submit"}
            </button>
          </div>
        </div>

        {err && <p className="mt-3 text-sm text-red-600">{err}</p>}
      </div>
    </div>
  );
}
