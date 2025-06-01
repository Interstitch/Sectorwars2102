# Shared Design System Components

**Document Status**: Component Pattern Library  
**Created**: 2025-06-01  
**Purpose**: Define reusable component patterns shared between Admin UI and Player Client

---

## 🎨 Component Pattern Library

### Button Component

```css
/* Base Button Pattern - Shared */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-sm);
  font-weight: 500;
  line-height: 1.5;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: all var(--transition-base);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

/* Admin UI Button */
.admin-ui .btn-primary {
  background-color: var(--color-blue-500);
  color: white;
  border-color: var(--color-blue-500);
}

.admin-ui .btn-primary:hover {
  background-color: var(--color-blue-600);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Player Client Button */
.player-client .btn-primary {
  background: linear-gradient(135deg, var(--color-blue-600) 0%, var(--color-blue-500) 100%);
  color: white;
  border-color: var(--hud-accent);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  position: relative;
  overflow: hidden;
}

.player-client .btn-primary:hover {
  box-shadow: 0 0 20px var(--glow-primary);
  border-color: var(--color-blue-400);
}
```

### Card Component

```css
/* Base Card Pattern - Shared */
.card {
  background: var(--surface-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.card-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-primary);
}

.card-body {
  padding: var(--space-6);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* Admin UI Card */
.admin-ui .card {
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-base);
}

.admin-ui .card:hover {
  box-shadow: var(--shadow-md);
}

/* Player Client Card */
.player-client .card {
  background: linear-gradient(135deg, var(--surface-primary) 0%, var(--surface-secondary) 100%);
  position: relative;
}

.player-client .card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--hud-accent), transparent);
  opacity: 0.5;
}
```

### Form Components

```css
/* Base Form Input - Shared */
.form-input {
  width: 100%;
  padding: var(--space-3);
  font-size: var(--font-size-base);
  line-height: 1.5;
  color: var(--text-primary);
  background-color: var(--background-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}

.form-input:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  border-color: var(--color-blue-500);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Admin UI Input */
.admin-ui .form-input:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Player Client Input */
.player-client .form-input {
  background-color: var(--surface-secondary);
  border-color: var(--border-secondary);
}

.player-client .form-input:focus {
  border-color: var(--hud-accent);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}
```

### Status Indicators

```css
/* Base Status Indicator - Shared */
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.success {
  background-color: var(--color-success);
}

.status-dot.warning {
  background-color: var(--color-warning);
}

.status-dot.error {
  background-color: var(--color-error);
}

.status-dot.info {
  background-color: var(--color-info);
}

/* Pulse Animation - Shared */
.status-dot.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 currentColor;
  }
  70% {
    box-shadow: 0 0 0 8px transparent;
  }
  100% {
    box-shadow: 0 0 0 0 transparent;
  }
}

/* Player Client Status - Enhanced with glow */
.player-client .status-dot.success {
  box-shadow: 0 0 10px var(--color-success);
}

.player-client .status-dot.error {
  box-shadow: 0 0 10px var(--color-error);
}
```

### Badge Component

```css
/* Base Badge - Shared */
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  font-size: var(--font-size-xs);
  font-weight: 500;
  line-height: 1;
  border-radius: var(--radius-sm);
  white-space: nowrap;
}

.badge-success {
  background-color: var(--color-success);
  color: white;
}

.badge-warning {
  background-color: var(--color-warning);
  color: white;
}

.badge-error {
  background-color: var(--color-error);
  color: white;
}

.badge-info {
  background-color: var(--color-info);
  color: white;
}

/* Player Client Badge - With glow effect */
.player-client .badge {
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.player-client .badge-success {
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
}

.player-client .badge-error {
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}
```

### Loading States

```css
/* Base Spinner - Shared */
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-primary);
  border-radius: 50%;
  border-top-color: var(--color-primary-500);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Admin UI Spinner */
.admin-ui .spinner {
  border-color: var(--color-gray-300);
  border-top-color: var(--color-blue-500);
}

/* Player Client Spinner */
.player-client .spinner {
  border-color: var(--border-secondary);
  border-top-color: var(--hud-accent);
  box-shadow: 0 0 20px var(--hud-accent);
}

/* Loading Skeleton - Shared */
.skeleton {
  background: linear-gradient(90deg, 
    var(--surface-secondary) 25%, 
    var(--surface-primary) 50%, 
    var(--surface-secondary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
```

### Modal/Dialog

```css
/* Base Modal - Shared */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal {
  background: var(--surface-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-body {
  padding: var(--space-6);
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-primary);
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}

/* Player Client Modal - Enhanced */
.player-client .modal {
  border: 1px solid var(--hud-accent);
  animation: modalSlideIn 0.3s ease-out;
}

.player-client .modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--hud-accent);
  box-shadow: 0 0 20px var(--hud-accent);
}

@keyframes modalSlideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

---

## 📐 Layout Utilities (Shared)

```css
/* Container */
.container {
  width: 100%;
  max-width: var(--breakpoint-wide);
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

/* Section Spacing */
.section {
  padding-top: var(--space-12);
  padding-bottom: var(--space-12);
}

/* Flex Utilities */
.flex { display: flex; }
.inline-flex { display: inline-flex; }
.flex-col { flex-direction: column; }
.flex-row { flex-direction: row; }
.flex-wrap { flex-wrap: wrap; }
.items-start { align-items: flex-start; }
.items-center { align-items: center; }
.items-end { align-items: flex-end; }
.justify-start { justify-content: flex-start; }
.justify-center { justify-content: center; }
.justify-end { justify-content: flex-end; }
.justify-between { justify-content: space-between; }
.flex-1 { flex: 1 1 0%; }
.flex-auto { flex: 1 1 auto; }
.flex-none { flex: none; }

/* Grid Utilities */
.grid { display: grid; }
.grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.gap-2 { gap: var(--space-2); }
.gap-4 { gap: var(--space-4); }
.gap-6 { gap: var(--space-6); }

/* Spacing Utilities */
.m-0 { margin: 0; }
.m-1 { margin: var(--space-1); }
.m-2 { margin: var(--space-2); }
.m-4 { margin: var(--space-4); }
.mt-2 { margin-top: var(--space-2); }
.mr-2 { margin-right: var(--space-2); }
.mb-2 { margin-bottom: var(--space-2); }
.ml-2 { margin-left: var(--space-2); }
.mx-auto { margin-left: auto; margin-right: auto; }

.p-0 { padding: 0; }
.p-1 { padding: var(--space-1); }
.p-2 { padding: var(--space-2); }
.p-4 { padding: var(--space-4); }
.p-6 { padding: var(--space-6); }
.px-4 { padding-left: var(--space-4); padding-right: var(--space-4); }
.py-4 { padding-top: var(--space-4); padding-bottom: var(--space-4); }

/* Typography Utilities */
.text-xs { font-size: var(--font-size-xs); }
.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-lg { font-size: var(--font-size-lg); }
.text-xl { font-size: var(--font-size-xl); }
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

/* Color Utilities */
.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-tertiary { color: var(--text-tertiary); }
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-error { color: var(--color-error); }
.bg-primary { background-color: var(--background-primary); }
.bg-secondary { background-color: var(--background-secondary); }
```

---

## 🔧 Implementation Guidelines

### When to Share Components
1. Core UI patterns (buttons, forms, cards)
2. Layout utilities
3. Typography and spacing
4. Basic animations
5. Accessibility features

### When to Customize
1. Brand-specific styling
2. Theme-specific effects
3. Interface-specific behaviors
4. Unique visual treatments
5. Performance optimizations

### Best Practices
1. Always use CSS custom properties for customization
2. Keep shared components semantic and flexible
3. Document variations clearly
4. Test in both UIs before finalizing
5. Maintain accessibility standards

---

**Last Updated**: 2025-06-01  
**Version**: 1.0.0