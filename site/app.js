"use strict";
const states = {
  working: { label: "Clawdy is on it.", message: "Big ideas.\nSmall thinking face.", detail: "Amber stays on while any tracked session is working.", color: "amber" },
  done: { label: "All done. Over to you.", message: "Job done.\nTiny victory lap.", detail: "Green means all tracked sessions are ready or finished.", color: "green" },
  input: { label: "Your little cue to step in.", message: "Human API.\nAwaiting response.", detail: "Blinking red means a supported request for your input or permission.", color: "red blink" },
  error: { label: "A little help, please.", message: "Plot twist.\nWe found a bug.", detail: "Solid red indicates an explicit error signal from a supported application.", color: "red" }
};
document.querySelectorAll("[data-state]").forEach(button => button.addEventListener("click", () => {
  const state = states[button.dataset.state];
  document.querySelectorAll("[data-state]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
  document.querySelector("#demo-dot").className = "status-dot " + state.color;
  document.querySelector("#demo-label").textContent = state.label;
  const message = document.querySelector("#demo-message");
  message.replaceChildren(...state.message.split("\n").flatMap((line, index) => index ? [document.createElement("br"), document.createTextNode(line)] : [document.createTextNode(line)]));
  document.querySelector("#demo-detail").textContent = state.detail;
}));
const setupRequest = "I bought a new Clawdy and it is powered on near this computer. Set it up for me using https://github.com/alfonsoforcen3/TrafficLights_Arduino. Read AGENTS.md and docs/CUSTOMER_AGENT.md, help me identify and name my toy, configure my installed supported AI apps, and verify the lights. Guide me through normal Bluetooth and app approvals.";
document.querySelector("#copy-command").addEventListener("click", async () => {
  const feedback = document.querySelector("#copy-feedback");
  try {
    await navigator.clipboard.writeText(setupRequest);
    feedback.textContent = "Copied. Paste into your local AI assistant with terminal access.";
  } catch {
    feedback.textContent = "Copy this into your local AI: " + setupRequest;
  }
});
