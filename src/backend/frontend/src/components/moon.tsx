import { useState } from "react";

export type ApprovalAction = "approve" | "reject";

export interface ApprovalCardProps {
  themeColor: string;
  status: "inProgress" | "executing" | "complete";
  action: ApprovalAction;
  transactionId?: string;
  respond?: (response: string) => void;
}

export function ApprovalCard({
  themeColor,
  status,
  action,
  transactionId,
  respond,
}: ApprovalCardProps) {
  const [decision, setDecision] = useState<"confirmed" | "cancelled" | null>(null);
  const normalizedTransactionId = transactionId?.trim() || "the provided transaction";
  const isApproveAction = action === "approve";

  const handleConfirm = () => {
    setDecision("confirmed");
    respond?.(
      isApproveAction
        ? `Approve request confirmed for transaction ${normalizedTransactionId}.`
        : `Reject request confirmed for transaction ${normalizedTransactionId}.`
    );
  };

  const handleCancel = () => {
    setDecision("cancelled");
    respond?.(
      isApproveAction
        ? `Approve request cancelled for transaction ${normalizedTransactionId}.`
        : `Reject request cancelled for transaction ${normalizedTransactionId}.`
    );
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
              Request Confirmed
            </h2>
            <p className="text-white/90">
              {isApproveAction ? "Approval has been confirmed." : "Rejection has been confirmed."}
            </p>
          </div>
        ) : decision === "cancelled" ? (
          <div className="text-center">
            <div className="text-7xl mb-4">⏹️</div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Request Cancelled
            </h2>
            <p className="text-white/90">
              No decision was submitted.
            </p>
          </div>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className="text-7xl mb-4">🧾</div>
              <h2 className="text-2xl font-bold text-white mb-2">
                {isApproveAction ? "Approve Transaction" : "Reject Transaction"}
              </h2>
              <p className="text-white/90">
                Transaction ID: {normalizedTransactionId}
              </p>
            </div>

            {status !== "complete" && (
              <div className="flex gap-3">
                <button
                  onClick={handleConfirm}
                  className="flex-1 px-6 py-4 rounded-xl bg-white text-black font-bold 
                    shadow-lg hover:shadow-xl transition-all 
                    hover:scale-105 active:scale-95"
                >
                  {isApproveAction ? "✅ Confirm Approve" : "⛔ Confirm Reject"}
                </button>
                <button
                  onClick={handleCancel}
                  className="flex-1 px-6 py-4 rounded-xl bg-black/20 text-white font-bold 
                    border-2 border-white/30 shadow-lg
                    transition-all hover:scale-105 active:scale-95
                    hover:bg-black/30"
                >
                  Cancel
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
