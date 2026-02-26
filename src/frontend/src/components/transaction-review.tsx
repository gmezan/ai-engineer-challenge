import { useState } from "react";

export interface TransactionReviewCardProps {
  themeColor: string;
  status: "inProgress" | "executing" | "complete";
  transactionId?: string;
  respond?: (response: string) => void | Promise<void>;
}

export function TransactionReviewCard({
  themeColor,
  status,
  transactionId,
  respond,
}: TransactionReviewCardProps) {
  const [decision, setDecision] = useState<"confirmed" | "declined" | null>(null);
  const normalizedId = transactionId?.trim() || "UNKNOWN";

  const handleConfirm = () => {
    setDecision("confirmed");
    void respond?.(`APPROVED_TRANSACTION:${normalizedId}`);
  };

  const handleDecline = () => {
    setDecision("declined");
  };

  return (
    <div
      style={{ backgroundColor: themeColor }}
      className="rounded-2xl shadow-xl max-w-md w-full mt-6"
    >
      <div className="bg-white/20 backdrop-blur-md p-8 w-full rounded-2xl">
        {decision === "confirmed" ? (
          <div className="text-center">
            <div className="text-7xl mb-4">✅</div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Decision Confirmed
            </h2>
            <p className="text-white/90">
              Transaction {normalizedId} was approved.
            </p>
          </div>
        ) : decision === "declined" ? (
          <div className="text-center">
            <div className="text-7xl mb-4">✋</div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Transaction Blocked
            </h2>
            <p className="text-white/90">
              Approval was not granted, so the function was not executed.
            </p>
          </div>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className="text-7xl mb-4">🛡️</div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Approve Transaction?
              </h2>
              <p className="text-white/90">
                Transaction ID: {normalizedId}
              </p>
            </div>

            {status === "executing" && (
              <div className="flex gap-3">
                <button
                  onClick={handleConfirm}
                  className="flex-1 px-6 py-4 rounded-xl bg-white text-black font-bold 
                    shadow-lg hover:shadow-xl transition-all 
                    hover:scale-105 active:scale-95"
                >
                  ✅ Approve
                </button>
                <button
                  onClick={handleDecline}
                  className="flex-1 px-6 py-4 rounded-xl bg-black/20 text-white font-bold 
                    border-2 border-white/30 shadow-lg
                    transition-all hover:scale-105 active:scale-95
                    hover:bg-black/30"
                >
                  ✋ Keep Blocked
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
