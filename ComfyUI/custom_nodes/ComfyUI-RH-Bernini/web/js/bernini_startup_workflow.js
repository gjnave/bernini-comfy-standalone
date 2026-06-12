import { app } from "../../../../scripts/app.js";

const WORKFLOW_URL = "/api/workflow_templates/ComfyUI-RH-Bernini/bernini_ui_workflow.json";
const SESSION_KEY = "berniniStartupWorkflowAttempted";

function graphLooksEmpty() {
    const nodes = app?.graph?._nodes;
    if (!Array.isArray(nodes)) {
        return true;
    }
    return nodes.length === 0;
}

async function tryLoadBerniniWorkflow() {
    if (sessionStorage.getItem(SESSION_KEY) === "1") {
        return;
    }
    sessionStorage.setItem(SESSION_KEY, "1");

    let attempts = 0;
    while (attempts < 60) {
        attempts += 1;

        if (!app?.graph) {
            await new Promise((resolve) => setTimeout(resolve, 250));
            continue;
        }

        if (!graphLooksEmpty()) {
            return;
        }

        try {
            const response = await fetch(WORKFLOW_URL, { cache: "no-store" });
            if (!response.ok) {
                console.warn("[Bernini] Failed to fetch startup workflow:", response.status);
                return;
            }
            const workflow = await response.json();
            await app.loadGraphData(workflow);
            console.info("[Bernini] Loaded startup workflow.");
        } catch (error) {
            console.warn("[Bernini] Failed to load startup workflow:", error);
        }
        return;
    }
}

app.registerExtension({
    name: "ComfyUI.RHBernini.StartupWorkflow",
    async setup() {
        queueMicrotask(() => {
            void tryLoadBerniniWorkflow();
        });
    },
});
