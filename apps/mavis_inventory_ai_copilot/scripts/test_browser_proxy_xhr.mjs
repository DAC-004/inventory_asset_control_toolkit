/**
 * Simulates the Pyodide sync-XHR proxy call used by browser_http._post_json_pyodide.
 * Run with: node scripts/test_browser_proxy_xhr.mjs [baseUrl]
 */
const baseUrl = process.argv[2] || "https://mavis-inventory-ai-copilot-dusky.vercel.app";
const url = `${baseUrl.replace(/\/$/, "")}/api/summary`;
const payload = {
  model: "gpt-4o-mini",
  context: {
    kpis: { total_inventory_value: 1000 },
    top_risks: [],
    transfer_summary: { recommended_count: 1, total_net_benefit: 250 },
    markdown_summary: { candidate_count: 1, total_recovery: 100 },
  },
};

function syncPostJson(targetUrl, body) {
  const xhr = new XMLHttpRequest();
  xhr.open("POST", targetUrl, false);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(JSON.stringify(body));
  return { status: xhr.status, text: xhr.responseText };
}

const result = syncPostJson(url, payload);
console.log(`status=${result.status}`);
console.log(result.text.slice(0, 500));

if (result.text.includes("asyncio.run()")) {
  console.error("FAIL: asyncio error detected in proxy response");
  process.exit(1);
}

if (result.status >= 400) {
  const parsed = JSON.parse(result.text);
  if (parsed.error?.includes("OPENAI_API_KEY")) {
    console.log("PASS: sync XHR reached proxy; missing API key is expected until Vercel env is set.");
    process.exit(0);
  }
  console.error("FAIL: unexpected HTTP error", parsed);
  process.exit(1);
}

const parsed = JSON.parse(result.text);
if (!parsed.summary) {
  console.error("FAIL: missing summary in success response", parsed);
  process.exit(1);
}

console.log("PASS: OpenAI proxy returned summary via sync XHR.");
process.exit(0);
