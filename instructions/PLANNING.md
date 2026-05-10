# PLANNING.md — Project Planning Framework

## Planning Philosophy
Plans must be written before execution. A well-structured plan catches conflicts, identifies dependencies, and reduces wasted work. This file defines the planning format and houses active project plans.

---

## Planning Format

### Level 1: Feature Plan (for single features)
```markdown
## Feature Plan: [Feature Name]
**Date**: YYYY-MM-DD
**Status**: Draft | Approved | In-Progress | Complete

### Objective
One sentence: what does this feature accomplish?

### Acceptance Criteria
- [ ] Criterion 1 (observable, verifiable)
- [ ] Criterion 2
- [ ] Criterion N

### Technical Design

#### Backend Changes
- [ ] New model: [ModelName] (fields: ...)
- [ ] New/updated controller: [ControllerName] (methods: ...)
- [ ] New/updated routes: [method] /api/[path]
- [ ] New validators: [validatorFile]
- [ ] New constants: [codes to add]

#### Frontend Changes
- [ ] New/updated slice: [sliceName] (actions: ...)
- [ ] New/updated API functions: [api file]
- [ ] New/updated components: [ComponentName]
- [ ] New/updated pages: [PageName]

### Dependencies
- Depends on: [other features/tasks that must be complete first]
- Blocks: [features that can't start until this is done]

### Risks
- Risk 1: [description] → Mitigation: [approach]
- Risk 2: [description] → Mitigation: [approach]

### Estimated Complexity
□ Small (< 2 hours)  □ Medium (2-8 hours)  □ Large (> 8 hours)
```

### Level 2: Subtask Plan (for atomic implementation tasks)
```markdown
## Task [ID]: [Task Name]
**Status**: pending | in-progress | blocked | complete
**Parent Feature**: [Feature Plan name]

### Implementation Steps
1. [Step 1: What to do, what file to create/modify]
2. [Step 2]
3. [Step N]

### Files Modified
- [file path]: [what changes]

### Mental Test Plan
- Happy path: [expected behavior]
- Error path: [expected behavior]

### Definition of Done
- [ ] Code follows CODING_STANDARDS.md
- [ ] All error paths handled
- [ ] Debug logs removed
- [ ] Changes consistent with ARCHITECTURE.md
```

---

## Active Plans

### Feature Plan: User Profile Management
**Status**: Complete (reference implementation)

#### Objective
Allow users to create, view, update, and delete their profile.

#### Acceptance Criteria
- [x] User can save profile data
- [x] Profile persists across page refresh
- [x] User can switch between saved profiles
- [x] User can delete a profile
- [x] Profile changes require authentication

#### Backend Design
- [x] Model: User + Profile (separate collection or embedded — decided: separate collection)
- [x] GET /api/profile → get authenticated user's profiles
- [x] POST /api/profile → create new profile
- [x] PATCH /api/profile/:id → update profile
- [x] DELETE /api/profile/:id → soft delete profile

#### Frontend Design
- [x] Redux slice: profileSlice (profiles[], selectedProfile, loading, error, clearError)
- [x] API: profileApi.js (fetchProfilesApi, createProfileApi, updateProfileApi, deleteProfileApi)
- [x] Component: ProfileForm (multi-step with validation)
- [x] Component: ProfileList (list + switch + delete)

---

### Feature Plan: AI Content Generation
**Status**: Complete (reference implementation)

#### Objective
Generate AI-powered content (headlines, summaries, etc.) for user profiles.

#### Acceptance Criteria
- [x] User can trigger AI generation for their profile
- [x] System uses Gemini as primary AI model
- [x] System falls back to Grok if Gemini fails
- [x] System falls back to free OpenAI model if Grok fails
- [x] User can rate generated content (thumbs up/down)
- [x] Generation requires authentication

#### Backend Design
- [x] POST /api/generate/headline → generate content
- [x] POST /api/feedback → submit feedback (Boolean not string)
- [x] Multi-model fallback chain in service layer
- [x] Rate limiting on generation endpoint

#### Lessons Learned
- Feedback field must be Boolean in schema (not string "up"/"down") — see FAILURES.md
- Multi-model fallback needs timeout config per model

---

## Planning Checklist
Before starting any implementation:
- [ ] Feature plan is written and complete
- [ ] All dependencies are identified
- [ ] Risks are documented with mitigations
- [ ] Acceptance criteria are specific and verifiable
- [ ] Backend and frontend changes are both planned
- [ ] Complexity is estimated
- [ ] Human approval obtained if architectural changes involved
