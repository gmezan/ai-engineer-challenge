"use client";

import { ProverbsCard } from "@/components/proverbs";
import { WeatherCard } from "@/components/weather";
import { ApprovalAction, ApprovalCard } from "@/components/moon";
import { AgentState } from "@/lib/types";
import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
import { useRef, useState } from "react";

export default function CopilotKitPage() {
  const [themeColor, setThemeColor] = useState("#6366f1");

  // 🪁 Frontend Actions: https://docs.copilotkit.ai/microsoft-agent-framework/frontend-actions
  useCopilotAction({
    name: "setThemeColor",
    parameters: [{
      name: "themeColor",
      description: "The theme color to set. Make sure to pick nice colors.",
      required: true, 
    }],
    handler({ themeColor }) {
      setThemeColor(themeColor);
    },
  });

  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <CopilotSidebar
        disableSystemMessage={true}
        clickOutsideToClose={false}
        labels={{
          title: "Popup Assistant",
          initial: "👋 Hi, there! You're chatting with an agent."
        }}
        suggestions={[
          {
            title: "Generative UI",
            message: "Get the weather in San Francisco.",
          },
          {
            title: "Frontend Tools",
            message: "Set the theme to green.",
          },
          {
            title: "Human In the Loop",
            message: "Approve transaction TX-12345.",
          },
          {
            title: "Human In the Loop",
            message: "Reject transaction TX-98765.",
          },
          {
            title: "Write Agent State",
            message: "Add a proverb about AI.",
          },
          {
            title: "Update Agent State",
            message: "Please remove 1 random proverb from the list if there are any.",
          },
          {
            title: "Read Agent State",
            message: "What are the proverbs?",
          }
        ]}
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

  //🪁 Generative UI: https://docs.copilotkit.ai/microsoft-agent-framework/generative-ui
  useCopilotAction({
    name: "get_weather",
    description: "Get the weather for a given location.",
    available: "disabled",
    parameters: [
      { name: "location", type: "string", required: true },
    ],
    render: ({ args }) => {
      return <WeatherCard location={args.location} themeColor={themeColor} />
    },
  }, [themeColor]);

  const activeApprovalToolRef = useRef<"approve_transaction" | "reject_transaction" | null>(null);

  const renderApproval = (
    toolName: "approve_transaction" | "reject_transaction",
    action: ApprovalAction,
    context: unknown,
  ) => {
    const { respond, status, args } = context as {
      respond?: (response: string) => void;
      status: "inProgress" | "executing" | "complete";
      args?: { transaction_id?: string };
    };

    if (status !== "complete" && activeApprovalToolRef.current !== toolName) {
      activeApprovalToolRef.current = toolName;
    }

    if (activeApprovalToolRef.current !== toolName) {
      return <></>;
    }

    return (
      <ApprovalCard
        themeColor={themeColor}
        status={status}
        action={action}
        transactionId={args?.transaction_id}
        respond={respond}
      />
    );
  };

  // 🪁 Human In the Loop: https://docs.copilotkit.ai/microsoft-agent-framework/human-in-the-loop
  useCopilotAction({
    name: "approve_transaction",
    description: "Approve a transaction with human confirmation.",
    available: "disabled",
    parameters: [{ name: "transaction_id", type: "string", required: true }],
    renderAndWaitForResponse: (context) => renderApproval("approve_transaction", "approve", context),
  }, [themeColor]);

  useCopilotAction({
    name: "reject_transaction",
    description: "Reject a transaction with human confirmation.",
    available: "disabled",
    parameters: [{ name: "transaction_id", type: "string", required: true }],
    renderAndWaitForResponse: (context) => renderApproval("reject_transaction", "reject", context),
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
