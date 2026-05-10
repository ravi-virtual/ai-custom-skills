# OBJECTIVE.md — Mission & Goals

## System Mission
Establish a **portable, project-agnostic AI Operating System** — a markdown-based framework placed at the root of any project (or in a shared directory) that governs how AI agents think, plan, execute, and remember, regardless of the technology stack or team.

## Current Primary Objectives

### Objective 1: AI Operating System
**Status**: In Progress  
**Goal**: Establish a complete markdown-based AI OS in the designated **`AI_OS_DIR`** directory that governs all AI agent behavior in the current workspace.  
> **Portability Note**: `AI_OS_DIR` is wherever you place this file collection — no absolute path is hardcoded. Copy the directory to any project or shared network location and update AI agent context-loading paths accordingly.
**Completion Criteria**:
- All AI instruction files created (CLAUDE.md, GEMINI.md, CHATGPT.md, CURSOR.md)
- All behavioral rules files created (AGENT_RULES.md, RULES.md, CONSTRAINTS.md)
- All memory files created (MEMORY.md, EXECUTION_MEMORY.md, DECISIONS.md)
- All architecture reference files created (ARCHITECTURE.md, BACKEND.md, FRONTEND.md)
- All workflow files created (AI_WORKFLOW.md, PLANNING.md)

### Objective 2: Profile Enhancer Application
**Status**: Feature Complete (ongoing maintenance)  
**Goal**: A full-stack MERN application where authenticated users create AI-enhanced professional profiles  
**Core Features**:
- User authentication (register, login, JWT, refresh token)
- Profile creation and management (multi-step form, persistence, switching)
- AI-powered content generation (Gemini → Grok → OpenAI fallback)
- User feedback on generated content
- Admin panel for managing users and profiles

### Objective 3: Engineering Excellence
**Status**: Ongoing  
**Goal**: Every piece of code in this workspace meets production-grade standards  
**Standards Applied**:
- MERN stack patterns from `backend-expressjs` and `frontend-reactjs` skills
- Security standards from SECURITY.md
- Testing standards from TESTING.md
- Code quality from CODING_STANDARDS.md

---

## Strategic Goals (Long-Term)

### Goal 1: Autonomous Development Capability
AI agents should be able to implement complete features (backend + frontend) with minimal human guidance, following established patterns without deviation.

### Goal 2: Zero Defect Deployment
All code delivered by AI agents passes the pre-delivery checklist in CODING_STANDARDS.md before reaching human review.

### Goal 3: Self-Improving System
The AI OS continuously improves through LEARNINGS.md and SELF_IMPROVEMENT.md — patterns that fail get corrected, patterns that work get reinforced.

### Goal 4: Knowledge Accumulation
The KNOWLEDGE_BASE.md grows richer with every session, reducing the time agents spend re-learning the same information.

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| AI OS files created | 60+ files | ~40+ |
| Code delivery with no revisions | 90%+ | Measured per session |
| Debug sessions with Trace-Solve-Clean | 100% | Tracked in FAILURES.md |
| Features with complete error handling | 100% | Verified in code review |
| Sessions with memory updated | 100% | Goal |
| Known failures documented | All | FAILURES.md |

---

## What We Are NOT Building
To maintain focus, explicitly exclude:
- Real-time features (WebSockets) — not in scope for current phase
- Mobile apps — web only
- Microservices — monolith MERN for now
- Multi-tenant SaaS — single tenant MVP
- Complex billing — not in scope

---

## Decision Log (Objective-Level)
| Decision | Rationale |
|----------|-----------|
| MERN stack | Full-stack JavaScript consistency, strong community, AI agents have deep knowledge |
| JWT (not sessions) | Stateless, horizontally scalable, compatible with mobile future |
| Vanilla CSS (not Tailwind) | Zero dependency debt, maximum control, consistent with design philosophy |
| UUID (not ObjectId) | Cross-system portability, no serialization surprises |
| Soft delete (not hard delete) | Data recovery, audit trail, compliance readiness |
