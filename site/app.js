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
document.querySelector("#copy-command").addEventListener("click", async () => {
  const feedback = document.querySelector("#copy-feedback");
  try {
    await navigator.clipboard.writeText("python3 install.py --onboard");
    feedback.textContent = "Copied. Run from your approved Clawdy folder.";
  } catch {
    feedback.textContent = "Copy manually: python3 install.py --onboard";
  }
});
