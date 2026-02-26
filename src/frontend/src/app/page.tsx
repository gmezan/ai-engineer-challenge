"use client";

import { ProverbsCard } from "@/components/proverbs";
import { TransactionReviewCard } from "@/components/transaction-review";
import { AgentState } from "@/lib/types";
import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
import { useState } from "react";

export default function CopilotKitPage() {
  const [themeColor, setThemeColor] = useState("#6366f1");

  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <CopilotSidebar
        disableSystemMessage={true}
        clickOutsideToClose={false}
        suggestions={[]}
      >
        <YourMainContent themeColor={themeColor} />
      </CopilotSidebar>
    </main>
  );
}

function YourMainContent({ themeColor }: { themeColor: string }) {
  // 🪁 Shared State: https://docs.copilotkit.ai/microsoft-agent-framework/shared-state
  const { state, setState } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: {
      proverbs: [
        "CopilotKit may be new, but its the best thing since sliced bread.",
      ],
    },
  })

  useCopilotAction({
    name: "review_transaction",
    description: "Approve a transaction after manual approval; otherwise keep it blocked.",
    available: "disabled",
    renderAndWaitForResponse: ({ respond, status, args }) => {
      return (
        <TransactionReviewCard
          themeColor={themeColor}
          status={status}
          respond={respond}
          transactionId={args.transaction_id as string | undefined}
        />
      )
    },
  }, [themeColor]);

  return (
    <div
      style={{ backgroundColor: themeColor }}
      className="h-screen flex justify-center items-center flex-col transition-colors duration-300"
    >
      <ProverbsCard state={state} setState={setState} />
    </div>
  );
}
