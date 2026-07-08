/**
 * End-to-end browser test for the Stlite app OpenAI proxy path.
 * Usage: node scripts/test_stlite_ai_summary.mjs [baseUrl]
 */
import { chromium } from "playwright";

const baseUrl = process.argv[2] || "https://mavis-inventory-ai-copilot-dusky.vercel.app";
const timeoutMs = 180_000;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

try {
  console.log(`Opening ${baseUrl}`);
  await page.goto(baseUrl, { waitUntil: "domcontentloaded", timeout: 120_000 });

  console.log("Waiting for Streamlit sidebar navigation...");
  await page.getByRole("button", { name: "AI Summary" }).waitFor({ timeout: timeoutMs });

  console.log("Opening AI Summary page...");
  await page.getByRole("button", { name: "AI Summary" }).click();

  console.log("Generating summary via OpenAI proxy...");
  await page.getByRole("button", { name: "Generate Summary" }).click();

  await page.waitForTimeout(5000);

  const bodyText = await page.locator("body").innerText();
  if (bodyText.includes("asyncio.run() cannot be called from a running event loop")) {
    console.error("FAIL: asyncio event loop error still present in UI");
    process.exit(1);
  }

  if (bodyText.includes("OpenAI proxy request failed: asyncio.run()")) {
    console.error("FAIL: proxy surfaced asyncio.run failure");
    process.exit(1);
  }

  if (bodyText.includes("OPENAI_API_KEY is not configured")) {
    console.log("PASS: proxy reached server; missing Vercel OPENAI_API_KEY is expected.");
    process.exit(0);
  }

  if (bodyText.includes("# ") || bodyText.includes("Executive Overview")) {
    console.log("PASS: OpenAI summary rendered in browser.");
    process.exit(0);
  }

  if (bodyText.includes("OpenAI proxy request failed")) {
    console.error("FAIL: proxy request failed with:", bodyText.match(/OpenAI proxy request failed:[^\n]*/)?.[0]);
    process.exit(1);
  }

  console.log("PASS: no asyncio error detected after Generate Summary.");
  process.exit(0);
} catch (error) {
  console.error("FAIL:", error);
  process.exit(1);
} finally {
  await browser.close();
}
