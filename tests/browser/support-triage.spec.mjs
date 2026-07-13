import { expect, test } from "@playwright/test";


async function loadRecorded(page, sampleId = "T001") {
  if (sampleId !== "T001") {
    await page.locator(`[data-sample="${sampleId}"]`).click();
  }
  await page.getByRole("button", { name: "Load recorded example" }).click();
  await expect(page.getByText("Recorded example loaded.")).toBeVisible();
}


test.beforeEach(async ({ page }) => {
  await page.goto("/support-triage.html");
  await expect(page).toHaveTitle("Support Triage Review Console");
});


test("recorded recommendation enters human review without a model call", async ({ page }) => {
  const apiRequests = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/triage")) apiRequests.push(request.url());
  });

  await loadRecorded(page);

  await expect(page.locator("#mode-pill")).toHaveText("RECORDED");
  await expect(page.locator("#validation-pill")).toHaveText("CONTRACT PASSED");
  await expect(page.locator("#review-form")).toBeVisible();
  await expect(page.locator("#review-product-area")).toHaveValue("authentication");
  await expect(page.locator("#review-urgency")).toHaveValue("high");
  expect(apiRequests).toEqual([]);
});


test("reviewer can accept a recommendation and metrics update", async ({ page }) => {
  await loadRecorded(page);
  await page.getByRole("button", { name: "Accept recommendation" }).click();

  await expect(page.locator("#review-state")).toHaveText("ACCEPTED");
  await expect(page.getByText("Human reviewer accepted the recommendation.")).toBeVisible();
  await expect(page.locator("#review-metrics")).toContainText("Reviews1");
  await expect(page.locator("#review-metrics")).toContainText("Accepted1");
  await expect(page.locator("#review-metrics")).toContainText("Agreement100%");
  await expect(page.locator('[data-queue-sample="T001"]')).toContainText("Accepted");

  const records = await page.evaluate(() =>
    JSON.parse(localStorage.getItem("support-triage-review-console-v1"))
  );
  expect(records).toHaveLength(1);
  expect(records[0].outcome).toBe("accepted");
  expect(JSON.stringify(records[0])).not.toContain("access-code");
  expect(JSON.stringify(records[0])).not.toContain("I have tried resetting my password");
});


test("edited decision requires a reason and records the correction", async ({ page }) => {
  const apiRequests = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/triage")) apiRequests.push(request.url());
  });

  await loadRecorded(page, "T002");
  await page.locator("#review-urgency").selectOption("medium");
  await page.getByRole("button", { name: "Save edited decision" }).click();
  await expect(page.getByText("Choose a reviewer reason for the correction.")).toBeVisible();

  await page.locator("#review-reason").selectOption("urgency_correction");
  await page.getByRole("button", { name: "Save edited decision" }).click();

  await expect(page.locator("#review-state")).toHaveText("CORRECTED");
  await expect(page.locator('[data-queue-sample="T002"]')).toContainText("Corrected");
  await expect(page.locator("#review-metrics")).toContainText("Corrected1");
  await expect(page.locator("#review-metrics")).toContainText("Agreement0%");

  const records = await page.evaluate(() =>
    JSON.parse(localStorage.getItem("support-triage-review-console-v1"))
  );
  expect(records[0].outcome).toBe("overridden");
  expect(records[0].override_reason).toBe("urgency_correction");
  expect(records[0].model_decision.urgency).toBe("high");
  expect(records[0].final_decision.urgency).toBe("medium");
  expect(apiRequests).toEqual([]);
});


test("sanitized review export downloads and reset clears local state", async ({ page }) => {
  await loadRecorded(page);
  await page.getByRole("button", { name: "Accept recommendation" }).click();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export sanitized JSON" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("support-triage-synthetic-reviews.json");
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const exported = JSON.parse(Buffer.concat(chunks).toString("utf-8"));

  expect(exported.schema_version).toBe("support-triage-review-export-v1");
  expect(exported.synthetic_data_only).toBe(true);
  expect(exported.review_count).toBe(1);
  expect(JSON.stringify(exported)).not.toContain("access-code");
  expect(JSON.stringify(exported)).not.toContain("I have tried resetting my password");

  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Reset browser reviews" }).click();
  await expect(page.locator("#review-metrics")).toContainText("Reviews0");
  const stored = await page.evaluate(() => localStorage.getItem("support-triage-review-console-v1"));
  expect(stored).toBeNull();
});


test("demo access request opens a browser compose URL without sending", async ({ page }) => {
  const link = page.locator("#request-demo-access");
  await expect(link).toHaveAttribute("target", "_blank");
  await expect(link).toHaveAttribute("rel", "noopener noreferrer");

  const href = await link.getAttribute("href");
  const destination = new URL(href);
  expect(destination.origin).toBe("https://mail.google.com");
  expect(destination.searchParams.get("view")).toBe("cm");
  expect(destination.searchParams.get("to")).toBe("pablo.de.la.cruz.pro@gmail.com");
  expect(destination.searchParams.get("su")).toBe("Support Triage Demo Access Request");
});


test("feedback report exposes candidates without claiming golden-set promotion", async ({ page }) => {
  await page.goto("/feedback-candidate-report.html");

  await expect(page).toHaveTitle("Support Triage Feedback Pipeline");
  await expect(page.locator("#promotion-state")).toHaveText("AWAITING HUMAN REVIEW");
  await expect(page.locator("#feedback-summary")).toContainText("4validated reviews");
  await expect(page.locator("#feedback-summary")).toContainText("2unique candidates");
  await expect(page.locator("#candidate-list article")).toHaveCount(2);
  await expect(page.getByText("Permanent eval data changes only through a separate reviewed code change.")).toBeVisible();
});
