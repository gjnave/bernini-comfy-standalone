import { app } from "../../../../scripts/app.js";

const WORKFLOW_URL = "/api/workflow_templates/ComfyUI-RH-Bernini/bernini_ui_workflow.json";
const BAD_NODE_TYPES = new Set([
    "easy imageScaleDownToSize",
]);
const BAD_WORKFLOW_MARKERS = [
    "comfyui-easy-use",
    "easy imageScaleDownToSize",
    "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors",
    "wan_2.1_vae_Comfy-Org.safetensors",
];

let startupWorkflowLoaded = false;

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
    if (nodes.some((node) => node?.id === 76 || !node?.type || BAD_NODE_TYPES.has(node.type))) {
        return true;
    }

    try {
        const serialized = JSON.stringify(app.graph.serialize?.() ?? {});
        return BAD_WORKFLOW_MARKERS.some((marker) => serialized.includes(marker));
    } catch {
        return false;
    }
}

async function tryLoadBerniniWorkflow() {
    if (startupWorkflowLoaded || !graphNeedsReplacement()) {
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
            startupWorkflowLoaded = true;
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
        for (const delay of [750, 2000, 5000]) {
            setTimeout(() => void tryLoadBerniniWorkflow(), delay);
        }
    },
});
