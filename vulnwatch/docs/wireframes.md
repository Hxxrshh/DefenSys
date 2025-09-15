# Defensys - UI Wireframes

## 🎨 Dashboard Wireframes

### 1. Main Dashboard Layout
```
┌─────────────────────────────────────────────────────────────────────────┐
│  [Logo] Defensys                                [🔍 Search...] [👤 User] │
├───────────────┬─────────────────────────────────────────────────────────┤
│               │                                                         │
│ NAVIGATION    │                    MAIN CONTENT AREA                    │
│               │                                                         │
│ 📊 Dashboard  │ ┌─────────────────────────────────────────────────────┐ │
│ 📄 Logs       │ │              Security Dashboard                     │ │
│ ⚠️  Threats   │ │         Real-time overview of security             │ │
│ 📊 Reports    │ └─────────────────────────────────────────────────────┘ │
│ ⚙️  Settings  │                                                         │
│               │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│               │ │ Total   │ │Critical │ │ Active  │ │ Passed  │       │
│               │ │ Scans   │ │ Vulns   │ │Warnings │ │ Tests   │       │
│               │ │ 1,247   │ │   23    │ │  156    │ │  892    │       │
│               │ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│               │                                                         │
│               │ ┌─────────────────────────────────────────────────────┐ │
│               │ │            Repository Scanner                       │ │
│               │ │                                                     │ │
│               │ │ Repository URL: [________________] [Scan Type ▼]    │ │
│               │ │                                   [Start Scan]      │ │
│               │ └─────────────────────────────────────────────────────┘ │
│               │                                                         │
│               │ ┌─────────────────┐ ┌─────────────────────────────────┐ │
│               │ │ Vulnerability   │ │    Vulnerability Trend         │ │
│               │ │ Distribution    │ │                                 │ │
│               │ │                 │ │     📈 Line Chart              │ │
│               │ │   🍩 Donut     │ │                                 │ │
│               │ │   Chart         │ │                                 │ │
│               │ └─────────────────┘ └─────────────────────────────────┘ │
│               │                                                         │
│               │ ┌─────────────────────────────────────────────────────┐ │
│               │ │              Recent Scans                           │ │
│               │ │                                                     │ │
│               │ │ • repo1/project  [COMPLETED] [23 vulnerabilities]  │ │
│               │ │ • repo2/app      [RUNNING]   [In progress...]      │ │
│               │ │ • repo3/service  [FAILED]    [Error: Access denied]│ │
│               │ └─────────────────────────────────────────────────────┘ │
└───────────────┴─────────────────────────────────────────────────────────┘
```

### 2. Repository Scanner Section Detail
```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Repository Scanner                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Repository URL                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ https://github.com/username/repository                              │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Scan Type                                                              │
│  ┌─────────────────────────┐                                            │
│  │ All Scans          ▼   │                                            │
│  └─────────────────────────┘                                            │
│  • All Scans (SAST + Secrets + Dependencies)                           │
│  • SAST Only                                                            │
│  • Secrets Only                                                         │
│  • Dependencies Only                                                     │
│                                                                         │
│  ┌─────────────────┐                                                    │
│  │   Start Scan    │                                                    │
│  └─────────────────┘                                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3. Vulnerability Details Modal
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Vulnerability Details                                           [X]    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Title: SQL Injection in user authentication                           │
│  Severity: [🔴 CRITICAL]                                               │
│  Scanner: Bandit                                                        │
│  File: src/auth.py:42                                                   │
│                                                                         │
│  Description:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Potential SQL injection vulnerability detected. User input is      │ │
│  │ directly concatenated into SQL query without proper sanitization   │ │
│  │ or parameterized queries.                                           │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Code Snippet:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ query = f"SELECT * FROM users WHERE id = {user_id}"               │ │
│  │ cursor.execute(query)                                              │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Recommendation:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Use parameterized queries or prepared statements:                  │ │
│  │ cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  [Mark as Fixed]  [Ignore]  [View Documentation]                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4. Scan Progress View
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Scan Progress - repository/project                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Overall Progress: [████████████░░░░] 75%                              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 1. Repository Cloning        [✓] Completed                         │ │
│  │ 2. SAST Analysis             [⟳] In Progress...                    │ │
│  │    • Bandit scan             [✓] Completed (12 issues found)       │ │
│  │    • Semgrep scan            [⟳] Running...                        │ │
│  │ 3. Secret Detection          [⏳] Waiting...                        │ │
│  │ 4. Dependency Analysis       [⏳] Waiting...                        │ │
│  │ 5. Report Generation         [⏳] Waiting...                        │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Real-time Log:                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ [10:23:15] Starting SAST analysis...                               │ │
│  │ [10:23:18] Bandit scan completed - 12 issues found                 │ │
│  │ [10:23:20] Starting Semgrep analysis...                            │ │
│  │ [10:23:25] Processing file: src/auth.py                            │ │
│  │ [10:23:27] Found potential SQL injection                           │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  [Cancel Scan]  [View Preliminary Results]                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5. Mobile Responsive Layout
```
Mobile View (< 768px)
┌───────────────────────┐
│ ☰ Defensys      [👤] │
├───────────────────────┤
│                       │
│   Security Dashboard  │
│                       │
│ ┌───────────────────┐ │
│ │   Total Scans     │ │
│ │     1,247         │ │
│ └───────────────────┘ │
│                       │
│ ┌───────────────────┐ │
│ │ Critical Vulns    │ │
│ │       23          │ │
│ └───────────────────┘ │
│                       │
│ Repository Scanner    │
│ ┌───────────────────┐ │
│ │ github.com/...    │ │
│ └───────────────────┘ │
│ ┌───────────────────┐ │
│ │ All Scans    ▼   │ │
│ └───────────────────┘ │
│ ┌───────────────────┐ │
│ │   Start Scan      │ │
│ └───────────────────┘ │
│                       │
│ [Chart Area Stacked]  │
│                       │
│ Recent Scans List...  │
│                       │
└───────────────────────┘
```

## 🎯 User Interface Components

### Navigation Sidebar
```
┌─────────────────┐
│ 🛡️ Defensys     │
│ Security Dash.  │
├─────────────────┤
│                 │
│ NAVIGATION      │
│                 │
│ 📊 Dashboard    │ ← Active state
│ 📄 Logs         │
│ ⚠️  Threats     │
│ 📊 Reports      │
│ ⚙️  Settings    │
│                 │
└─────────────────┘
```

### Status Indicators
```
API Status:
┌─────────────────┐
│ 🟢 System Active│ ← Connected
│ 🔴 System Error │ ← Disconnected
│ 🟡 System Slow  │ ← Warning
└─────────────────┘

Scan Status:
┌─────────────────┐
│ [✓] COMPLETED   │ ← Success
│ [⟳] RUNNING     │ ← In Progress
│ [✗] FAILED      │ ← Error
│ [⏳] PENDING    │ ← Waiting
└─────────────────┘
```

### Chart Components
```
Vulnerability Distribution (Donut Chart):
    Critical (Red)
    High (Orange)
    Medium (Yellow)
    Low (Green)

Vulnerability Trend (Line Chart):
    X-axis: Time (Jan, Feb, Mar...)
    Y-axis: Count
    Lines: Critical, High severity
```

### Form Elements
```
Input Field:
┌─────────────────────────────────┐
│ Repository URL                  │
│ ┌─────────────────────────────┐ │
│ │ https://github.com/...      │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘

Dropdown:
┌─────────────────┐
│ All Scans   ▼  │
├─────────────────┤
│ All Scans       │
│ SAST Only       │
│ Secrets Only    │
│ Dependencies    │
└─────────────────┘

Button:
┌─────────────┐
│ Start Scan  │
└─────────────┘
```

## 🎨 Color Scheme & Typography

### Colors
- **Primary**: #4285f4 (Blue)
- **Critical**: #ea4335 (Red)
- **High**: #ff9800 (Orange)
- **Medium**: #fbbc04 (Yellow)
- **Low**: #34a853 (Green)
- **Background**: #0f1419 (Dark)
- **Cards**: #1a1f2e (Dark Blue)
- **Text**: #ffffff (White)
- **Secondary Text**: #8b9dc3 (Light Blue)

### Typography
- **Primary Font**: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
- **Headers**: 700 weight
- **Body**: 400 weight
- **Small Text**: 12px
- **Regular Text**: 14px
- **Headers**: 18px-32px

## 📱 Responsive Breakpoints

- **Desktop**: > 1200px (Full layout)
- **Tablet**: 768px - 1200px (Stacked charts)
- **Mobile**: < 768px (Single column, hidden sidebar)