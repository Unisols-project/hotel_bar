const API = window.API_BASE_URL;

async function apiGet(path) {
  const res = await fetch(API + path);
  if (!res.ok) throw new Error("API error " + res.status);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "API error " + res.status);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(API + path, { method: "DELETE" });
  if (!res.ok) throw new Error("API error " + res.status);
  return res.json();
}

function money(v) {
  return Number(v || 0).toFixed(2);
}

function dateTime(value) {
  if (!value) return "-";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "-";
  const date = d.toLocaleDateString("en-IN", { day: "2-digit", month: "2-digit", year: "numeric" });
  const time = d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
  return `${date} ${time}`;
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s == null ? "" : String(s);
  return d.innerHTML;
}

const NAV_ITEMS = [
  ["dashboard", "index.html", "D", "Dashboard"],
  ["products", "products.html", "P", "Products"],
  ["tables", "tables.html", "T", "Tables"],
  ["vendors", "vendors.html", "V", "Vendors"],
  ["purchase", "purchase.html", "S", "Stock In"],
  ["bills", "bills.html", "B", "Bill History"],
  ["report", "report.html", "R", "Report"],
];

function renderSidebar(active, appName) {
  const mount = document.getElementById("sidebar");
  if (!mount) return;
  const navHtml = NAV_ITEMS.map(
    ([key, href, icon, label]) => `
      <a class="nav-item ${key === active ? "active" : ""}" href="${href}">
        <span class="ic">${icon}</span><span class="label">${label}</span>
      </a>`
  ).join("");
  mount.innerHTML = `
    <div class="brand"><div class="glyph">${esc((appName || "B")[0])}</div>${esc(appName || "Bar Ledger")}</div>
    <div class="brand-sub">STOCK - VENDORS - BILLING</div>
    <div class="nav">${navHtml}</div>
    <div class="sidebar-foot" id="conn-status">Connecting to API...</div>
  `;
  document.title = (appName || "Bar Ledger") + " - Hotel Bar Billing";
}

async function checkBackendHealth() {
  const el = document.getElementById("conn-status");
  try {
    const h = await apiGet("/api/health");
    if (el) {
      el.textContent = "Connected to API";
      el.style.color = "var(--success)";
    }
    renderSidebar.__appName = h.app;
    return h;
  } catch (e) {
    if (el) {
      el.textContent = "Backend not reachable";
      el.style.color = "var(--danger)";
    }
    return null;
  }
}
