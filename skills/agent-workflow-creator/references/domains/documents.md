# Document Processing Workflows

Domain-specific guidance for building agent workflows that extract, transform, analyze, summarize, or generate documents.

---

## Core Challenges in Document Workflows

- **Format diversity** — PDFs, DOCX, HTML, scanned images, spreadsheets, emails: each requires a different ingestion path
- **Layout complexity** — tables, multi-column layouts, headers/footers, footnotes all break naive text extraction
- **Scale** — processing 1 document vs. 10,000 requires different architectures
- **Accuracy requirements** — a missed clause in a contract is not the same as a missed sentence in a blog post
- **Output format** — structured data (JSON), narrative summary, or transformed document?

---

## Document Ingestion Pipeline

### Step 1: Format Detection & Routing
- Detect file type from extension + MIME type (don't trust extension alone)
- Route to the appropriate extractor:
  - PDF (native text) → `pdfplumber`, `pymupdf`
  - PDF (scanned/image) → OCR pipeline (`tesseract`, `Google Vision`, `AWS Textract`)
  - DOCX → `python-docx`
  - HTML → `BeautifulSoup` / `trafilatura`
  - Spreadsheet → `openpyxl` / `pandas`
  - Email → parse headers + body + attachments recursively

### Step 2: Text Extraction & Cleaning
- Remove headers, footers, page numbers (pattern matching)
- Normalize whitespace, fix encoding issues
- Preserve structure signals: headings, bullet points, table delimiters
- For tables: extract as structured data (list of dicts), not as flat text

### Step 3: Chunking Strategy
Choose based on downstream use:
- **Fixed-size chunks** (512–1024 tokens) — simple, works for most retrieval use cases
- **Semantic chunks** (split at paragraph/section boundaries) — preserves context better
- **Hierarchical chunks** (chapter → section → paragraph) — best for long structured documents
- **Table-aware chunking** — keep table rows together; don't split mid-row

### Step 4: Metadata Extraction
Always extract and store alongside content:
- Document title, author, date, source URL
- Section/chapter headings for each chunk
- Page number(s) for each chunk (for citation)
- Document type classification (contract, invoice, report, email, etc.)

---

## Processing Workflow Archetypes

### A. Summarization
1. Ingest + chunk document
2. For each chunk: generate a mini-summary
3. Merge mini-summaries → hierarchical reduce
4. Generate final summary at desired length
5. Extract key entities (people, dates, amounts, decisions) as structured metadata

**Pattern**: Map-Reduce

---

### B. Information Extraction
Extract specific fields from documents (invoices, contracts, forms).

1. Classify document type
2. Load extraction schema for that type (e.g., invoice: vendor, date, line_items, total)
3. For each field: targeted extraction with LLM + regex validation
4. Confidence scoring per field
5. Flag low-confidence fields for human review
6. Output structured JSON

**Pattern**: Sequential Chain with confidence gates

---

### C. Document Q&A / RAG
Answer questions about a document or document corpus.

1. Ingest + chunk + embed documents → vector store
2. Receive user question
3. Embed question → retrieve top-K chunks
4. Re-rank chunks by relevance
5. Compose prompt with chunks as context
6. Generate answer with citations (chunk ID + page number)
7. Return answer + source references

**Pattern**: Retrieval-Augmented

---

### D. Document Comparison
Compare two versions of a document (contracts, policies, proposals).

1. Ingest both documents
2. Align sections by heading or semantic similarity
3. For each aligned section pair: diff and summarize changes
4. Classify change type: addition, deletion, modification, reorder
5. Flag high-risk changes (e.g., liability clauses, payment terms)
6. Generate change summary report

**Pattern**: Fan-Out → Pairwise comparison → Fan-In

---

### E. Document Generation
Generate new documents from templates + data.

1. Receive input data (structured JSON, form responses, etc.)
2. Load appropriate template
3. Fill template slots with input data
4. LLM drafts freeform sections (narrative, reasoning, recommendations)
5. Validate output against required fields checklist
6. Format to target output type (PDF, DOCX, HTML)
7. Human review gate (optional, based on risk level)

**Pattern**: Sequential Chain

---

## Quality Gates

- [ ] Text extraction is complete (no truncated pages)
- [ ] Tables are extracted as structured data, not flat text
- [ ] Metadata (source, date, page numbers) attached to all chunks
- [ ] Confidence scores captured for extracted fields
- [ ] Low-confidence extractions flagged for review
- [ ] Output schema validated against expected structure
- [ ] Citations/sources included wherever content was drawn from

---

## Error Handling

| Failure Type | Recovery Strategy |
|---|---|
| PDF is scanned/image-only | Re-route to OCR pipeline |
| OCR confidence < threshold | Flag page for manual review; continue with rest |
| Unsupported file format | Return error with supported format list |
| Chunk exceeds context window | Split further; use hierarchical reduce |
| Extraction field not found | Return null + confidence=0; flag for review |
| Template slot missing required value | Block generation; request missing field |

---

## Scale Considerations

| Scale | Architecture |
|---|---|
| 1–10 docs | Sequential processing, in-memory |
| 10–1,000 docs | Async queue (Celery, Pub/Sub); parallel workers |
| 1,000+ docs | Distributed pipeline; streaming ingestion; managed vector DB |

Always design for the scale the user actually needs — don't over-engineer single-document workflows.

---

## Anti-Patterns to Avoid

- **Treating all PDFs as text PDFs** — always check if OCR is needed
- **Ignoring table structure** — extracting tables as flat text loses the relational data
- **No citation tracking** — users must be able to verify where extracted content came from
- **Chunking across section boundaries** — splits context that belongs together
- **Auto-publishing generated documents without human review** — especially for legal, medical, or financial docs
