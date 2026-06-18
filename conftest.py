import html
import json
import os
import re
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


ARTIFACTS_DIR = Path("artifacts")
SCREENSHOTS_ROOT_DIR = ARTIFACTS_DIR / "screenshots"
DASHBOARD_PATH = ARTIFACTS_DIR / "dashboard.html"
RUNS_PER_PAGE = 10


def _safe_nodeid(nodeid: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in nodeid)


def _load_history() -> list[dict]:
    if not DASHBOARD_PATH.exists():
        return []

    dashboard_html = DASHBOARD_PATH.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="dashboard-data" type="application/json">\s*(.*?)\s*</script>',
        dashboard_html,
        re.DOTALL,
    )
    if not match:
        return []

    try:
        return json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError:
        return []


def _build_dashboard(history: list[dict]) -> str:
    history_json = json.dumps(history, ensure_ascii=False).replace("</script>", "<\\/script>")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Automation Dashboard</title>
  <style>
    :root {{
      --color-primary: #ff7a9e;
      --color-primary-strong: #f05f88;
      --color-secondary: #fff1f5;
      --color-point: #6e4b5e;
      --color-text: #222222;
      --color-muted: #6b6267;
      --color-border: #e9d7df;
      --color-surface: #ffffff;
      --color-surface-alt: #fff8fb;
      --color-success: #247a52;
      --color-fail: #d94b72;
      --color-skip: #b38396;
      --shadow-soft: 0 16px 40px rgba(110, 75, 94, 0.12);
      --shadow-card: 0 10px 26px rgba(255, 122, 158, 0.12);
      --radius-lg: 28px;
      --radius-md: 18px;
      --radius-sm: 12px;
      --layout-width: 1200px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Gowun Dodum", "Pretendard", "Segoe UI", sans-serif;
      color: var(--color-text);
      background:
        radial-gradient(circle at top left, rgba(255, 122, 158, 0.18) 0, transparent 26%),
        radial-gradient(circle at top right, rgba(110, 75, 94, 0.10) 0, transparent 22%),
        linear-gradient(180deg, #fffdfd 0%, #fff6fa 48%, #fff1f5 100%);
    }}
    .wrap {{
      max-width: var(--layout-width);
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}
    .hero, .toolbar, .run-card {{
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-soft);
    }}
    .hero {{
      position: relative;
      overflow: hidden;
      padding: 30px;
      margin-bottom: 18px;
    }}
    .hero::before,
    .hero::after {{
      content: "";
      position: absolute;
      border-radius: 999px;
      pointer-events: none;
    }}
    .hero::before {{
      width: 240px;
      height: 240px;
      right: -40px;
      top: -90px;
      background: radial-gradient(circle, rgba(255, 122, 158, 0.22) 0%, rgba(255, 122, 158, 0) 68%);
    }}
    .hero::after {{
      width: 180px;
      height: 180px;
      left: -30px;
      bottom: -70px;
      background: radial-gradient(circle, rgba(110, 75, 94, 0.10) 0%, rgba(110, 75, 94, 0) 72%);
    }}
    h1 {{
      margin: 0 0 8px;
      position: relative;
      z-index: 1;
      font-family: "Jua", "Pretendard", sans-serif;
      font-size: 38px;
      line-height: 1.05;
      color: var(--color-point);
      letter-spacing: 0.01em;
    }}
    .subtitle {{
      margin: 0;
      position: relative;
      z-index: 1;
      color: var(--color-muted);
      font-size: 15px;
      line-height: 1.7;
    }}
    .stats {{
      margin-top: 22px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px;
      position: relative;
      z-index: 1;
    }}
    .card {{
      background: linear-gradient(180deg, var(--color-surface) 0%, var(--color-surface-alt) 100%);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      padding: 16px;
      box-shadow: var(--shadow-card);
    }}
    .card strong {{
      display: block;
      font-size: 28px;
      margin-bottom: 6px;
      font-family: "Jua", "Pretendard", sans-serif;
      color: var(--color-primary-strong);
    }}
    .toolbar {{
      padding: 18px;
      margin-bottom: 18px;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: end;
      background: rgba(255, 248, 251, 0.96);
    }}
    .field {{
      min-width: 180px;
      flex: 1 1 180px;
    }}
    .field label {{
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      color: var(--color-point);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 700;
    }}
    .field input,
    .field select {{
      width: 100%;
      border: 1px solid var(--color-border);
      background: var(--color-surface);
      border-radius: var(--radius-md);
      padding: 12px 14px;
      font: inherit;
      color: var(--color-text);
      box-shadow: inset 0 1px 0 rgba(255, 122, 158, 0.05);
    }}
    .field input:focus,
    .field select:focus {{
      outline: 2px solid rgba(240, 95, 136, 0.18);
      border-color: var(--color-primary);
    }}
    .toolbar button {{
      border: 0;
      border-radius: var(--radius-md);
      padding: 12px 18px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-strong) 100%);
      color: #fff;
      box-shadow: 0 12px 24px rgba(240, 95, 136, 0.28);
    }}
    .meta {{
      margin: 2px 0 18px;
      color: var(--color-muted);
      font-size: 14px;
    }}
    .run-card {{
      padding: 20px;
      margin-top: 16px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 248, 251, 0.92) 100%);
      box-shadow: var(--shadow-card);
    }}
    .run-head {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      margin-bottom: 14px;
    }}
    .run-head h2 {{
      margin: 0 0 4px;
      font-size: 22px;
      font-family: "Jua", "Pretendard", sans-serif;
      color: var(--color-point);
    }}
    .run-head p {{
      margin: 0;
      color: var(--color-muted);
      font-size: 14px;
    }}
    .run-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .pill {{
      background: var(--color-secondary);
      color: var(--color-point);
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid rgba(240, 95, 136, 0.12);
    }}
    table {{
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      background: rgba(255, 255, 255, 0.72);
      border-radius: var(--radius-md);
      overflow: hidden;
    }}
    th:nth-child(1),
    td:nth-child(1) {{
      width: 5%;
    }}
    th:nth-child(2),
    td:nth-child(2) {{
      width: 40%;
    }}
    th:nth-child(3),
    td:nth-child(3) {{
      width: 15%;
    }}
    th:nth-child(4),
    td:nth-child(4) {{
      width: 22%;
    }}
    th:nth-child(5),
    td:nth-child(5) {{
      width: 18%;
    }}
    th, td {{
      padding: 15px 14px;
      text-align: left;
      vertical-align: top;
      border-bottom: 1px solid var(--color-border);
      font-size: 14px;
      line-height: 1.6;
      word-break: break-word;
      overflow-wrap: anywhere;
    }}
    th {{
      color: var(--color-muted);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      background: rgba(255, 241, 245, 0.8);
    }}
    .badge {{
      display: inline-block;
      padding: 5px 10px;
      border-radius: 999px;
      color: #fff;
      font-size: 12px;
      font-weight: 700;
    }}
    .badge.passed {{ background: var(--color-success); }}
    .badge.failed {{ background: var(--color-primary-strong); }}
    .badge.skipped {{ background: var(--color-skip); }}
    a {{
      color: var(--color-primary-strong);
      text-decoration: none;
      font-weight: 700;
    }}
    .pagination {{
      margin-top: 20px;
      display: flex;
      gap: 8px;
      justify-content: center;
      flex-wrap: wrap;
    }}
    .pagination button {{
      border: 1px solid var(--color-border);
      background: var(--color-surface);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      cursor: pointer;
      font: inherit;
      color: var(--color-point);
      box-shadow: var(--shadow-card);
    }}
    .pagination button.active {{
      background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-strong) 100%);
      color: #fff;
      border-color: var(--color-primary-strong);
    }}
    .empty {{
      background: rgba(255, 248, 251, 0.85);
      border: 1px dashed var(--color-border);
      border-radius: var(--radius-lg);
      padding: 36px 20px;
      color: var(--color-muted);
      text-align: center;
    }}
    .reason-preview {{
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      color: var(--color-text);
      line-height: 1.5;
      margin-bottom: 8px;
    }}
    .reason-empty {{
      color: var(--color-muted);
    }}
    .detail-button {{
      border: 1px solid var(--color-border);
      background: var(--color-surface-alt);
      color: var(--color-primary-strong);
      border-radius: 999px;
      padding: 6px 10px;
      font: inherit;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }}
    .detail-button:hover {{
      background: var(--color-secondary);
    }}
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(34, 34, 34, 0.42);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      z-index: 999;
    }}
    .modal-backdrop.open {{
      display: flex;
    }}
    .modal {{
      width: min(860px, 100%);
      max-height: min(82vh, 920px);
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-soft);
      padding: 24px;
      display: flex;
      flex-direction: column;
    }}
    .modal-head {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: start;
      margin-bottom: 18px;
    }}
    .modal-head h3 {{
      margin: 0 0 6px;
      font-family: "Jua", "Pretendard", sans-serif;
      font-size: 28px;
      color: var(--color-point);
    }}
    .modal-meta {{
      margin: 0;
      color: var(--color-muted);
      line-height: 1.7;
      font-size: 14px;
    }}
    .modal-close {{
      border: 0;
      background: var(--color-secondary);
      color: var(--color-point);
      width: 40px;
      height: 40px;
      border-radius: 999px;
      font-size: 20px;
      cursor: pointer;
      flex: 0 0 auto;
    }}
    .modal-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
      overflow: auto;
      padding-right: 4px;
    }}
    .modal-section {{
      border: 1px solid var(--color-border);
      background: var(--color-surface-alt);
      border-radius: var(--radius-md);
      padding: 16px;
    }}
    .modal-section h4 {{
      margin: 0 0 8px;
      font-size: 13px;
      color: var(--color-point);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .modal-section p {{
      margin: 0;
      line-height: 1.7;
    }}
    .traceback {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-wrap: anywhere;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
      line-height: 1.6;
      color: var(--color-text);
    }}
    .note {{
      margin-top: 12px;
      color: var(--color-muted);
      font-size: 13px;
      line-height: 1.7;
    }}
    @media (max-width: 760px) {{
      .wrap {{
        padding: 20px 14px 40px;
      }}
      .hero,
      .toolbar,
      .run-card {{
        border-radius: 22px;
      }}
      h1 {{
        font-size: 31px;
      }}
      .run-head {{
        flex-direction: column;
      }}
      table {{
        display: block;
        overflow-x: auto;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>Automation Dashboard</h1>
      <p class="subtitle">`dashboard.html` 하나에 실행 기록을 계속 쌓고, 스크린샷은 날짜별 폴더에 저장합니다.</p>
      <div class="stats" id="summary-cards"></div>
      <p class="note">실패 스크린샷은 Playwright `page` fixture가 있고 브라우저가 살아 있을 때만 저장됩니다.</p>
    </section>
    <section class="toolbar">
      <div class="field">
        <label for="date-filter">Date</label>
        <input id="date-filter" type="date">
      </div>
      <div class="field">
        <label for="status-filter">Status</label>
        <select id="status-filter">
          <option value="all">All</option>
          <option value="passed">Passed</option>
          <option value="failed">Failed</option>
          <option value="skipped">Skipped</option>
        </select>
      </div>
      <div class="field">
        <label for="run-search">Search</label>
        <input id="run-search" type="text" placeholder="test_login, product ...">
      </div>
      <button id="reset-filters" type="button">Reset</button>
    </section>
    <p class="meta" id="result-meta"></p>
    <div id="runs-container"></div>
    <div class="pagination" id="pagination"></div>
  </div>
  <div class="modal-backdrop" id="detail-modal-backdrop">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="detail-modal-title">
      <div class="modal-head">
        <div>
          <h3 id="detail-modal-title">Failure Details</h3>
          <p class="modal-meta" id="detail-modal-meta"></p>
        </div>
        <button class="modal-close" id="detail-modal-close" type="button" aria-label="Close">×</button>
      </div>
      <div class="modal-grid">
        <section class="modal-section">
          <h4>Summary</h4>
          <p id="detail-modal-summary"></p>
        </section>
        <section class="modal-section">
          <h4>Location</h4>
          <p id="detail-modal-location">-</p>
        </section>
        <section class="modal-section">
          <h4>Screenshot</h4>
          <p id="detail-modal-screenshot">-</p>
        </section>
        <section class="modal-section">
          <h4>Traceback</h4>
          <pre class="traceback" id="detail-modal-traceback"></pre>
        </section>
      </div>
    </div>
  </div>
  <script id="dashboard-data" type="application/json">{history_json}</script>
  <script>
    const runHistory = JSON.parse(document.getElementById("dashboard-data").textContent);
    const runsPerPage = {RUNS_PER_PAGE};
    const dateInput = document.getElementById("date-filter");
    const statusFilter = document.getElementById("status-filter");
    const runSearch = document.getElementById("run-search");
    const resetButton = document.getElementById("reset-filters");
    const summaryCards = document.getElementById("summary-cards");
    const resultMeta = document.getElementById("result-meta");
    const runsContainer = document.getElementById("runs-container");
    const pagination = document.getElementById("pagination");
    const modalBackdrop = document.getElementById("detail-modal-backdrop");
    const modalClose = document.getElementById("detail-modal-close");
    const modalMeta = document.getElementById("detail-modal-meta");
    const modalSummary = document.getElementById("detail-modal-summary");
    const modalLocation = document.getElementById("detail-modal-location");
    const modalScreenshot = document.getElementById("detail-modal-screenshot");
    const modalTraceback = document.getElementById("detail-modal-traceback");

    let currentPage = 1;
    let detailStore = {{}};

    function escapeHtml(value) {{
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }}

    function badge(status) {{
      return `<span class="badge ${{status}}">${{status.toUpperCase()}}</span>`;
    }}

    function summarizeMessage(message) {{
      if (!message) {{
        return "-";
      }}

      const lines = message.split("\\n").map((line) => line.trim()).filter(Boolean);
      const errorLine = lines.find((line) => line.startsWith("E       ")) || lines.find((line) => line.startsWith("E   "));
      if (errorLine) {{
        return errorLine.replace(/^E\\s+/, "");
      }}

      const assertionLine = lines.find((line) => /AssertionError|TimeoutError|Error|Exception/i.test(line));
      if (assertionLine) {{
        return assertionLine;
      }}

      return lines[0];
    }}

    function extractLocation(message) {{
      if (!message) {{
        return "-";
      }}

      const match = message.match(/([\\w./-]+\\.py:\\d+(?::\\s*[A-Za-z_][\\w.]*)?)/);
      return match ? match[1] : "-";
    }}

    function escapeAttribute(value) {{
      return escapeHtml(value).replaceAll('"', "&quot;");
    }}

    function openDetail(detailId) {{
      const detail = detailStore[detailId];
      if (!detail) {{
        return;
      }}

      modalMeta.innerHTML = `${{escapeHtml(detail.nodeid)}}<br>${{escapeHtml(detail.status.toUpperCase())}}`;
      modalSummary.textContent = detail.summary;
      modalLocation.textContent = detail.location;
      modalTraceback.textContent = detail.message || "-";
      modalScreenshot.innerHTML = detail.screenshotRelpath
        ? `<a href="${{escapeAttribute(detail.screenshotRelpath)}}" target="_blank">Open screenshot</a>`
        : "-";
      modalBackdrop.classList.add("open");
    }}

    function closeDetail() {{
      modalBackdrop.classList.remove("open");
    }}

    function buildSummary() {{
      const totals = runHistory.reduce((acc, run) => {{
        acc.runs += 1;
        acc.tests += run.summary.total;
        acc.passed += run.summary.passed;
        acc.failed += run.summary.failed;
        acc.skipped += run.summary.skipped;
        return acc;
      }}, {{ runs: 0, tests: 0, passed: 0, failed: 0, skipped: 0 }});

      summaryCards.innerHTML = `
        <div class="card"><strong>${{totals.runs}}</strong><span>Total Runs</span></div>
        <div class="card"><strong>${{totals.tests}}</strong><span>Total Tests</span></div>
        <div class="card"><strong>${{totals.passed}}</strong><span>Passed</span></div>
        <div class="card"><strong>${{totals.failed}}</strong><span>Failed</span></div>
        <div class="card"><strong>${{totals.skipped}}</strong><span>Skipped</span></div>
      `;
    }}

    function filteredRuns() {{
      const selectedDate = dateInput.value;
      const selectedStatus = statusFilter.value;
      const searchTerm = runSearch.value.trim().toLowerCase();

      return runHistory
        .map((run) => {{
          const runDate = run.started_at.slice(0, 10);
          if (selectedDate && runDate !== selectedDate) {{
            return null;
          }}

          const results = run.results.filter((result) => {{
            const matchesStatus = selectedStatus === "all" || result.status === selectedStatus;
            const matchesSearch = !searchTerm || result.nodeid.toLowerCase().includes(searchTerm);
            return matchesStatus && matchesSearch;
          }});

          if (!results.length) {{
            return null;
          }}

          return {{
            ...run,
            filteredResults: results,
            filteredSummary: {{
              total: results.length,
              passed: results.filter((item) => item.status === "passed").length,
              failed: results.filter((item) => item.status === "failed").length,
              skipped: results.filter((item) => item.status === "skipped").length,
            }},
          }};
        }})
        .filter(Boolean);
    }}

    function renderRuns() {{
      const runs = filteredRuns();
      const totalPages = Math.max(1, Math.ceil(runs.length / runsPerPage));
      currentPage = Math.min(currentPage, totalPages);
      const start = (currentPage - 1) * runsPerPage;
      const pageRuns = runs.slice(start, start + runsPerPage);

      resultMeta.textContent = runs.length
        ? `${{runs.length}} runs found. Page ${{currentPage}} / ${{totalPages}}`
        : "No runs match the selected filters.";

      if (!pageRuns.length) {{
        runsContainer.innerHTML = '<div class="empty">조건에 맞는 실행 기록이 없습니다.</div>';
      }} else {{
        detailStore = {{}};
        runsContainer.innerHTML = pageRuns.map((run) => `
          <section class="run-card">
            <div class="run-head">
              <div>
                <h2>${{escapeHtml(run.run_name)}}</h2>
              </div>
              <div class="run-stats">
                <span class="pill">${{run.filteredSummary.total}} tests</span>
                <span class="pill">${{run.filteredSummary.passed}} passed</span>
                <span class="pill">${{run.filteredSummary.failed}} failed</span>
                <span class="pill">${{run.filteredSummary.skipped}} skipped</span>
              </div>
            </div>
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Checklist Item</th>
                  <th>Status</th>
                  <th>Failure Reason</th>
                  <th>Screenshot</th>
                </tr>
              </thead>
              <tbody>
                ${{run.filteredResults.map((result, index) => {{
                  const detailId = `${{run.run_name}}-${{index}}`;
                  const summary = summarizeMessage(result.message);
                  const location = extractLocation(result.message);
                  detailStore[detailId] = {{
                    nodeid: result.nodeid,
                    status: result.status,
                    summary,
                    location,
                    message: result.message,
                    screenshotRelpath: result.screenshot_relpath,
                  }};

                  return `
                    <tr>
                      <td>${{index + 1}}</td>
                      <td>${{escapeHtml(result.nodeid)}}</td>
                      <td>${{badge(result.status)}}</td>
                      <td>
                        ${{result.message
                          ? `<div class="reason-preview">${{escapeHtml(summary)}}</div><button class="detail-button" type="button" data-detail-id="${{escapeAttribute(detailId)}}">상세 보기</button>`
                          : `<span class="reason-empty">-</span>`}}
                      </td>
                      <td>${{result.screenshot_relpath ? `<a href="${{escapeHtml(result.screenshot_relpath)}}" target="_blank">open</a>` : "-"}}</td>
                    </tr>
                  `;
                }}).join("")}}
              </tbody>
            </table>
          </section>
        `).join("");
      }}

      pagination.innerHTML = "";
      if (runs.length <= runsPerPage) {{
        return;
      }}

      const prevButton = document.createElement("button");
      prevButton.textContent = "Prev";
      prevButton.disabled = currentPage === 1;
      prevButton.addEventListener("click", () => {{
        currentPage -= 1;
        renderRuns();
      }});
      pagination.appendChild(prevButton);

      for (let page = 1; page <= totalPages; page += 1) {{
        const button = document.createElement("button");
        button.textContent = page;
        if (page === currentPage) {{
          button.classList.add("active");
        }}
        button.addEventListener("click", () => {{
          currentPage = page;
          renderRuns();
        }});
        pagination.appendChild(button);
      }}

      const nextButton = document.createElement("button");
      nextButton.textContent = "Next";
      nextButton.disabled = currentPage === totalPages;
      nextButton.addEventListener("click", () => {{
        currentPage += 1;
        renderRuns();
      }});
      pagination.appendChild(nextButton);
    }}

    function bindFilters() {{
      [dateInput, statusFilter, runSearch].forEach((element) => {{
        element.addEventListener("input", () => {{
          currentPage = 1;
          renderRuns();
        }});
        element.addEventListener("change", () => {{
          currentPage = 1;
          renderRuns();
        }});
      }});

      resetButton.addEventListener("click", () => {{
        dateInput.value = "";
        statusFilter.value = "all";
        runSearch.value = "";
        currentPage = 1;
        renderRuns();
      }});

      runsContainer.addEventListener("click", (event) => {{
        const button = event.target.closest("[data-detail-id]");
        if (!button) {{
          return;
        }}
        openDetail(button.dataset.detailId);
      }});

      modalClose.addEventListener("click", closeDetail);
      modalBackdrop.addEventListener("click", (event) => {{
        if (event.target === modalBackdrop) {{
          closeDetail();
        }}
      }});

      window.addEventListener("keydown", (event) => {{
        if (event.key === "Escape") {{
          closeDetail();
        }}
      }});
    }}

    buildSummary();
    bindFilters();
    renderRuns();
  </script>
</body>
</html>
"""


def pytest_sessionstart(session):
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    SCREENSHOTS_ROOT_DIR.mkdir(parents=True, exist_ok=True)
    run_started_at = datetime.now()
    screenshots_dir = SCREENSHOTS_ROOT_DIR / run_started_at.strftime("%Y-%m-%d")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    session.config._dashboard_results = []
    session.config._dashboard_started_at = run_started_at.strftime("%Y-%m-%d %H:%M:%S")
    session.config._dashboard_run_name = run_started_at.strftime("%Y-%m-%d %H:%M:%S")
    session.config._dashboard_screenshots_dir = screenshots_dir


@pytest.fixture(scope="function")
def page(request):
    browser_name = os.getenv("PLAYWRIGHT_BROWSER", "chromium").lower()
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() in {"1", "true", "yes", "on"}
    default_slow_mo = "0" if headless else "500"
    slow_mo = int(os.getenv("PLAYWRIGHT_SLOW_MO", default_slow_mo))

    with sync_playwright() as p:
        browser_type = getattr(p, browser_name, None)
        if browser_type is None:
            raise pytest.UsageError(
                "Unsupported PLAYWRIGHT_BROWSER value. "
                "Use one of: chromium, firefox, webkit."
            )

        try:
            browser = browser_type.launch(
                headless=headless,
                slow_mo=slow_mo,
            )
        except PlaywrightError as exc:
            raise pytest.UsageError(
                "Failed to launch Playwright browser. "
                "Try `playwright install`, or run with "
                "`PLAYWRIGHT_BROWSER=webkit pytest` / `PLAYWRIGHT_BROWSER=firefox pytest`. "
                "On restricted macOS environments, Chromium may be blocked by OS permissions."
            ) from exc

        context = browser.new_context()
        page = context.new_page()
        request.node.page = page
        yield page
        context.close()
        browser.close()


@pytest.fixture(scope="session")
def login_success_close_delay_ms():
    return int(os.getenv("LOGIN_SUCCESS_CLOSE_DELAY_MS", "2000"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    screenshot_relpath = None
    message = ""

    if report.failed:
        message = str(report.longreprtext).strip()
        page = getattr(item, "page", None)
        if page:
            timestamp = datetime.now().strftime("%H-%M-%S")
            screenshot_name = f"{timestamp}_{_safe_nodeid(item.nodeid)}.png"
            screenshot_path = item.config._dashboard_screenshots_dir / screenshot_name
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                screenshot_relpath = str(screenshot_path.relative_to(ARTIFACTS_DIR))
            except PlaywrightError as exc:
                message = f"{message}\n\nScreenshot failed: {exc}".strip()

    item.config._dashboard_results.append(
        {
            "nodeid": item.nodeid,
            "status": report.outcome,
            "message": message,
            "screenshot_relpath": screenshot_relpath,
        }
    )


def pytest_sessionfinish(session, exitstatus):
    rows = getattr(session.config, "_dashboard_results", [])
    started_at = getattr(session.config, "_dashboard_started_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    run_name = getattr(session.config, "_dashboard_run_name", started_at)

    current_run = {
        "run_name": run_name,
        "started_at": started_at,
        "summary": {
            "total": len(rows),
            "passed": sum(1 for row in rows if row["status"] == "passed"),
            "failed": sum(1 for row in rows if row["status"] == "failed"),
            "skipped": sum(1 for row in rows if row["status"] == "skipped"),
        },
        "results": rows,
    }

    history = _load_history()
    history.insert(0, current_run)
    DASHBOARD_PATH.write_text(_build_dashboard(history), encoding="utf-8")
