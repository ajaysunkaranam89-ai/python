const dot = document.getElementById("status-dot");
const text = document.getElementById("status-text");
const uptimeEl = document.getElementById("uptime");

function formatUptime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h}h ${m}m ${s}s`;
}

async function refresh() {
  try {
    const [healthRes, infoRes] = await Promise.all([
      fetch("/health"),
      fetch("/api/info"),
    ]);

    if (healthRes.ok) {
      dot.className = "dot healthy";
      text.textContent = "Healthy";
    } else {
      throw new Error("unhealthy");
    }

    if (infoRes.ok) {
      const info = await infoRes.json();
      uptimeEl.textContent = formatUptime(info.uptime_seconds);
    }
  } catch (err) {
    dot.className = "dot down";
    text.textContent = "Unreachable";
  }
}

refresh();
setInterval(refresh, 5000);
