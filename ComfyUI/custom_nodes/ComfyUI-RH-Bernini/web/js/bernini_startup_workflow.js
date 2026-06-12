import { app } from "../../../../scripts/app.js";

const WORKFLOW_URL = "/api/workflow_templates/ComfyUI-RH-Bernini/bernini_ui_workflow.json";
const SESSION_KEY = "berniniStartupWorkflowAttempted:v2";
const BAD_NODE_TYPES = new Set([
    "easy imageScaleDownToSize",
]);

function graphLooksEmpty() {
    const nodes = app?.graph?._nodes;
    if (!Array.isArray(nodes)) {
        return true;
    }
    return nodes.length === 0;
}

function graphNeedsReplacement() {
    const nodes = app?.graph?._nodes;
    if (!Array.isArray(nodes) || nodes.length === 0) {
        return true;
    }
    return nodes.some((node) => !node?.type || BAD_NODE_TYPES.has(node.type));
}

async function tryLoadBerniniWorkflow() {
    if (sessionStorage.getItem(SESSION_KEY) === "1") {
        return;
    }

    let attempts = 0;
    while (attempts < 60) {
        attempts += 1;

        if (!app?.graph) {
            await new Promise((resolve) => setTimeout(resolve, 250));
            continue;
        }

        if (!graphNeedsReplacement()) {
            sessionStorage.setItem(SESSION_KEY, "1");
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
            sessionStorage.setItem(SESSION_KEY, "1");
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
