"use strict";
const q = (selector) => document.querySelector(selector);
const local = ["127.0.0.1", "localhost"].includes(location.hostname);
const dialog = q("dialog");
document
  .querySelectorAll(".preview")
  .forEach((button) =>
    button.addEventListener("click", () => dialog.showModal()),
  );
q("#close-dialog").onclick = q("#dismiss").onclick = () => dialog.close();
document.querySelectorAll("[data-toy]").forEach((button) =>
  button.addEventListener("click", () => {
    const duck = button.dataset.toy === "duck";
    document.body.classList.toggle("duck", duck);
    document.querySelectorAll("[data-name]").forEach((node) => {
      node.textContent = duck ? "CyberDuck" : "Clawdy";
    });
    document
      .querySelectorAll("[data-toy]")
      .forEach((node) =>
        node.setAttribute("aria-pressed", String(node === button)),
      );
    q(".toy").setAttribute(
      "aria-label",
      "Illustration of " + (duck ? "CyberDuck" : "Clawdy"),
    );
  }),
);
function render(data) {
  const valid = data.connected && !data.stale;
  const battery = valid ? data.battery : null;
  q("#connection").textContent = valid
    ? "Board connected over Bluetooth"
    : "Waiting for your board";
  q("#connection-dot").classList.toggle("online", valid);
  const percent =
    battery && battery.measurement_valid ? battery.estimated_percent : null;
  q("#percent").textContent = Number.isFinite(percent) ? percent + "%" : "—";
  q("#meter-fill").style.width = Number.isFinite(percent)
    ? Math.max(0, Math.min(100, percent)) + "%"
    : "0%";
  q("#voltage").textContent =
    battery && Number.isFinite(battery.voltage)
      ? battery.voltage.toFixed(3) + " V"
      : "Unverified";
  q("#sensor").textContent =
    battery && Number.isFinite(battery.sensor_voltage)
      ? battery.sensor_voltage.toFixed(4) + " V"
      : "—";
  q("#sample-age").textContent = valid
    ? "UPDATED " + data.age_seconds + "s AGO"
    : "NO CURRENT READING";
  q("#battery-note").textContent = !valid
    ? "Power on your companion and allow Bluetooth access. Old readings are not shown as live."
    : battery && battery.calibrated
      ? "Estimated percentage from a verified voltage conversion. Charging can inflate the estimate."
      : "Live sensor reading. Battery voltage and percentage need a verified divider calibration for this board.";
  const samples = valid
    ? (data.history || []).filter((sample) =>
        Number.isFinite(sample.sensor_voltage),
      )
    : [];
  let trend = "Awaiting samples";
  if (samples.length >= 2) {
    const delta = samples.at(-1).sensor_voltage - samples[0].sensor_voltage;
    trend =
      Math.abs(delta) < 0.005
        ? "Steady"
        : delta > 0
          ? "Voltage rising"
          : "Voltage falling";
    const min = Math.min(...samples.map((s) => s.sensor_voltage)) - 0.005;
    const max = Math.max(...samples.map((s) => s.sensor_voltage)) + 0.005;
    q("#chart-line").setAttribute(
      "d",
      samples
        .map(
          (s, i) =>
            `${i ? "L" : "M"}${(i / (samples.length - 1)) * 600},${90 - ((s.sensor_voltage - min) / (max - min)) * 80}`,
        )
        .join(" "),
    );
  } else q("#chart-line").setAttribute("d", "");
  q("#trend").textContent = trend;
}
async function refresh() {
  try {
    const response = await fetch("/api/battery", {
      cache: "no-store",
      signal: AbortSignal.timeout(4000),
    });
    if (!response.ok) throw new Error("Bridge unavailable");
    render(await response.json());
  } catch {
    render({ connected: false, stale: true });
  }
}
if (local) {
  refresh();
  setInterval(refresh, 5000);
} else {
  q("#connection").textContent = "Live battery data lives on your Mac";
  q("#battery-note").textContent =
    "Open the local Mac dashboard to see your board’s real readings. This public page contains no simulated battery values.";
  q("#local-link").hidden = false;
}
