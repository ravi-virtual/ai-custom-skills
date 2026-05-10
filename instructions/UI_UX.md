# UI_UX.md — UI/UX Design Standards

## Purpose
Defines the visual design system, UX patterns, and interaction standards for the frontend application. All components must comply with these standards.

---

## Design Philosophy

### Core Principles
1. **Clarity First** — Every UI element has a single, obvious purpose
2. **Feedback Always** — Every user action has visible feedback (loading, success, error)
3. **Progressive Disclosure** — Show only what's needed; reveal complexity on demand
4. **Error Prevention** — Disable impossible actions; guide users before they make mistakes
5. **Consistency** — Same patterns for same problems, everywhere in the app

---

## Color System

### Primary Palette
```css
/* Use CSS custom properties for all colors — never hardcode hex values */
:root {
  /* Brand */
  --color-primary: #6366f1;        /* Indigo — primary actions */
  --color-primary-hover: #4f46e5;  /* Darker indigo — hover state */
  --color-primary-light: #e0e7ff;  /* Light indigo — backgrounds */

  /* Neutrals */
  --color-bg: #0f0f13;             /* Near-black background */
  --color-surface: #1a1a24;        /* Card / panel background */
  --color-border: #2d2d3f;         /* Borders and dividers */
  --color-text-primary: #f1f5f9;   /* Main text */
  --color-text-secondary: #94a3b8; /* Muted text */
  --color-text-disabled: #475569;  /* Disabled state text */

  /* Semantic */
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #6366f1, #8b5cf6);
  --gradient-surface: linear-gradient(135deg, #1a1a24, #252535);
}
```

### Color Usage Rules
- Never use color alone to convey meaning — pair with icon or text
- Primary color for ONE primary action per screen
- Error red only for actual errors, never decoratively
- Text on dark surfaces must have ≥ 4.5:1 contrast ratio (WCAG AA)

---

## Typography

### Font Stack
```css
:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

/* Import in index.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
```

### Type Scale
```css
:root {
  --text-xs: 0.75rem;     /* 12px — labels, captions */
  --text-sm: 0.875rem;    /* 14px — secondary text, table data */
  --text-base: 1rem;      /* 16px — body text */
  --text-lg: 1.125rem;    /* 18px — emphasized text */
  --text-xl: 1.25rem;     /* 20px — small headings */
  --text-2xl: 1.5rem;     /* 24px — section headings */
  --text-3xl: 1.875rem;   /* 30px — page headings */
  --text-4xl: 2.25rem;    /* 36px — hero headings */
}
```

---

## Spacing System

```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
}
```

---

## Component Standards

### Buttons
```css
/* Primary — one per screen maximum */
.btn-primary {
  background: var(--gradient-primary);
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: 8px;
  font-weight: 600;
  font-size: var(--text-sm);
  transition: opacity 0.2s ease, transform 0.1s ease;
  cursor: pointer;
  border: none;
}
.btn-primary:hover { opacity: 0.9; }
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

/* Secondary */
.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  padding: var(--space-3) var(--space-6);
  border-radius: 8px;
  font-weight: 500;
}
.btn-secondary:hover { background: var(--color-surface); border-color: var(--color-text-secondary); }
```

### Form Inputs
```css
.input {
  width: 100%;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--space-3) var(--space-4);
  color: var(--color-text-primary);
  font-size: var(--text-base);
  font-family: var(--font-sans);
  transition: border-color 0.2s ease;
  outline: none;
}
.input:focus { border-color: var(--color-primary); }
.input.error { border-color: var(--color-error); }
.input::placeholder { color: var(--color-text-disabled); }
```

### Cards
```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: var(--space-6);
}
.card-hover {
  transition: border-color 0.2s ease, transform 0.2s ease;
}
.card-hover:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
}
```

---

## UX Patterns

### Loading States
- **Button loading**: Show spinner inside button, disable button, keep button text
- **Page loading**: Full-page skeleton (not spinner) for initial data load
- **Inline loading**: Small spinner next to the element being updated
- **Never**: Block the entire UI with a loading overlay unless absolutely necessary

### Error States
- **Form errors**: Show below the specific field, not as a toast
- **API errors**: Show in an error banner above the form, not alert()
- **Network errors**: Show "Connection error. Check your internet." with retry button
- **404 errors**: Show a friendly page with navigation options

### Empty States
- Every list/table must have an empty state (never show nothing)
- Empty state: icon + heading + subtext + optional call to action
- Example: 🗂️ "No profiles yet" / "Create your first profile to get started" / [Create Profile button]

### Form UX Rules
- Labels above inputs (never inside as placeholder-only)
- Inline error messages below the field that has the error
- Disabled submit button until required fields are filled
- Multi-step forms: show progress indicator (Step 2 of 4)
- Validate on blur (not on every keystroke)

### Confirmation Dialogs
Required for destructive actions (delete, account deletion):
- "Are you sure you want to delete [Name]? This cannot be undone."
- Two buttons: "Cancel" (secondary) and "Delete" (danger/red)
- Never auto-confirm — always require explicit click

---

## Responsive Breakpoints

```css
/* Mobile first */
/* Base styles: 0-767px (mobile) */

@media (min-width: 768px) {
  /* Tablet: 768px-1023px */
}

@media (min-width: 1024px) {
  /* Desktop: 1024px+ */
}

@media (min-width: 1280px) {
  /* Large desktop: 1280px+ */
}
```

### Navigation Responsive Rule
- Mobile (< 768px): hamburger menu with slide-out drawer
- Tablet (768px+): horizontal nav or compact sidebar
- Desktop (1024px+): full sidebar or top navigation

---

## Animation Standards

```css
/* Micro-animations: fast and subtle */
--transition-fast: 0.15s ease;
--transition-base: 0.2s ease;
--transition-slow: 0.3s ease;

/* Use transform + opacity — not width/height (causes layout reflow) */
.fade-in { animation: fadeIn 0.2s ease; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### Animation Rules
- Hover effects: ≤ 0.2s
- Page transitions: ≤ 0.3s
- Loading skeletons: shimmer animation (not flashing)
- Never animate layout properties (width, height, margin) — use transform instead
- Respect `prefers-reduced-motion` media query

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Accessibility Standards

- All interactive elements focusable via keyboard
- Focus ring visible (never `outline: none` without replacement)
- All images have `alt` text
- Form inputs have associated `<label>` elements
- Color contrast ≥ 4.5:1 for normal text, ≥ 3:1 for large text
- Error messages associated with inputs via `aria-describedby`
- Loading states announced via `aria-live` regions
