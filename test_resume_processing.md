# Resume-Processing End-to-End Integration Test Plan

> **Scope**  
> Validate the complete resume-ingestion pipeline – from user upload to final UI render – against the pre-loaded sample database and media fixtures. All functional paths (happy & error) must pass with **0 defects**, **≤ 3 s** per document and **100 %** data-consistency where applicable.

---

## 1. System Components & Boundaries
| Stage | Component | Key Responsibilities |
|-------|-----------|----------------------|
| A | **Upload** | File reception, MIME/type filtering, size limits |
| B | **PDF/DOCX Processing** | Text & metadata extraction, OCR fallback |
| C | **API Validation** | Schema validation, auth, 4xx/5xx handling |
| D | **Database Matching** | Candidate ↔︎ Job ↔︎ Company linking, transaction handling |
| E | **Rendering** | Template binding, state management |
| F | **User Output** | Success & error UX, latency, accessibility |

Mermaid overview:
```mermaid
graph LR
  A[Upload] --> B[PDF Processing]
  B --> C[API Validation]
  C --> D[Database Matching]
  D --> E[Rendering]
  E --> F[User Output]
```

---

## 2. Test Environment
1. **Isolated DB** – seeded with `/sample_db/schema.sql` & `/sample_db/test_data.sql`.
2. **Media Fixtures** – located in `./media/` (PDF & DOCX, varied sizes, some corrupted).
3. **Auth Context** – test user with all required permissions.
4. **Parallelism** – execute stress suites with configurable `CONCURRENCY` (default **10** simultaneous uploads).

```bash
# One-time setup example
psql "$TEST_DB_URL" < sample_db/schema.sql
psql "$TEST_DB_URL" < sample_db/test_data.sql
```

---

## 3. Test Matrix

| ID | Scenario | Input Fixture | Expected Outcome | Primary Assertions |
|----|----------|--------------|------------------|--------------------|
| H-01 | Happy-path PDF | `media/resume_jane.pdf` | Parsed → Stored → Rendered | 200 status; ≤3 s; 100 % field match |
| H-02 | Happy-path DOCX | `media/resume_john.docx` | Same as H-01 | " |
| E-01 | Corrupted PDF | `media/broken_resume.pdf` | Graceful error → UI fallback | No 500; user-facing message present; log entry created |
| E-02 | Scanned Image PDF | `media/scanned_resume.pdf` | OCR attempted; if text <50 % confidence → user prompt | Timeout <3 s; proper flag set |
| V-01 | Oversize File | Generated 25 MB PDF | 413 Payload Too Large | Response ≤100 ms; error banner |
| R-01 | Unauthorized Access | Upload w/o token | 401 Unauthorized | Redirect to login |
| S-01 | 50 concurrent uploads | Batch of 50 varied files | All complete ≤5× baseline; no memory leaks | Heap stable; no 5xx |

_Add additional edge cases as defects surface._

---

## 4. Automation Scripts
Tests are written in **TypeScript** using **Jest** + **Supertest** for HTTP interaction and **Playwright** for UI validation.

```typescript
// tests/helpers/upload.ts
export async function uploadResume(filePath: string, auth = true) {
  const token = auth ? await getAuthToken() : undefined;
  return request(app.callback())
    .post('/api/resumes')
    .set('Authorization', token ? `Bearer ${token}` : '')
    .attach('file', filePath);
}
```

### Sample Test Skeleton
```typescript
import { uploadResume } from './helpers/upload';
import { checkDbConsistency } from './helpers/db';
import { measurePerf } from './helpers/perf';

test('H-01: Happy-path PDF', async () => {
  const t0 = Date.now();
  const res = await uploadResume('media/resume_jane.pdf');
  expect(res.status).toBe(200);
  await checkDbConsistency(res.body.resumeId);
  expect(Date.now() - t0).toBeLessThan(3000);
});
```

Run all suites:
```bash
npm run test:integration
```

---

## 5. Validation & Metrics

### 5.1 Data Consistency
```sql
SELECT COUNT(*) = 0 AS mismatches
FROM extracted_resumes er
LEFT JOIN reference_resumes rr USING (candidate_id)
WHERE er.normalized_json IS DISTINCT FROM rr.normalized_json;
```

### 5.2 Performance
Use `measurePerf(fn)` wrapper to capture **server processing time** (upload → 200/4xx). Thresholds:
* **Green:** ≤3 s
* **Yellow:** 3-5 s (warn)
* **Red:** >5 s (fail)

### 5.3 Error Logging
Ensure each failure path pushes a structured log line:
```json
{
  "stage": "PDF Processing",
  "error": "CorruptedFileError",
  "requestId": "uuid",
  "file": "broken_resume.pdf"
}
```

---

## 6. Reporting Format
```typescript
interface TestResult {
  scenario: string;
  passed: boolean;
  errors: {
    type: 'syntax' | 'api' | 'rendering' | 'routing';
    message: string;
    component: string;
  }[];
  dataConsistency: number; // 0-100 %
  performance: number; // ms
}
```
Generate a JSON & HTML summary after each run:
```bash
jest --json --outputFile reports/results.json
npx jest-html-reporter --output reports/results.html
```

---

## 7. Execution Protocol
1. **Seed database** & **start application** in test mode.
2. Run `npm run test:integration`.
3. Inspect `reports/results.html` – _all tests must be green._
4. If any test fails:
   1. Locate failing stage through structured error/logs.
   2. Patch code → add regression test.
   3. Re-run full suite until zero-defect.

---

## 8. Acceptance Criteria
- Every scenario in §3 passes.
- No unhandled exceptions in server logs.
- 0 % data mismatch vs. reference DB.
- P95 processing time ≤3 s.
- UI fallback messages rendered for **all** simulated failures.
- Lint & type checks remain clean.

> **Done ≡ Merged** when the above holds for **CI**, **local** and **production-like** environments.

---

## 9. Change History
| Date | Author | Notes |
|------|--------|-------|
| 2025-08-04 | AI Assistant | Initial draft |
