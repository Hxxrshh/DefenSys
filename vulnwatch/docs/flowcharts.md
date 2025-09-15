# Defensys - System Flowcharts

## 🔄 Main Application Flow

### 1. User Journey Flowchart
```
         [User Accesses Dashboard]
                    │
                    ▼
         [Dashboard Loads UI Components]
                    │
                    ├── [Load Statistics] ──► [Display Stat Cards]
                    │
                    ├── [Load Charts Data] ──► [Render Charts]
                    │
                    ├── [Load Recent Scans] ──► [Display Scan List]
                    │
                    └── [Check API Health] ──► [Update Status Indicator]
                    │
                    ▼
         [User Interacts with Scanner]
                    │
                    ▼
         [Enter Repository URL]
                    │
                    ▼
         [Select Scan Types]
                    │
                    ▼
         [Click Start Scan]
                    │
                    ▼
         [Scan Process Begins] ──► [View Results]
```

### 2. Repository Scanning Process Flow
```
    [Repository URL Input]
             │
             ▼
    [Validate URL Format]
             │
             ├── [Invalid] ──► [Show Error Message]
             │
             ▼ [Valid]
    [Create Scan Record]
             │
             ▼
    [Set Scan Status: PENDING]
             │
             ▼
    [Clone Repository]
             │
             ├── [Clone Failed] ──► [Set Status: FAILED]
             │
             ▼ [Clone Success]
    [Parallel Scanner Execution]
             │
             ├─── [SAST Scanner] ────┐
             │                       │
             ├─── [Secret Scanner] ───┼── [Collect Results]
             │                       │
             └─── [Dependency Scan] ──┘
                         │
                         ▼
             [Aggregate All Results]
                         │
                         ▼
             [Store in Database]
                         │
                         ▼
             [Set Status: COMPLETED]
                         │
                         ▼
             [Update Dashboard]
                         │
                         ▼
             [Generate Report]
```

### 3. API Request Flow
```
    [Frontend Request]
             │
             ▼
    [API Gateway (Flask)]
             │
             ▼
    [Request Validation]
             │
             ├── [Invalid] ──► [Return 400 Error]
             │
             ▼ [Valid]
    [Route to Controller]
             │
             ▼
    [Business Logic Processing]
             │
             ▼
    [Database Operation]
             │
             ├── [DB Error] ──► [Return 500 Error]
             │
             ▼ [Success]
    [Format Response]
             │
             ▼
    [Return JSON Response]
             │
             ▼
    [Frontend Receives Data]
             │
             ▼
    [Update UI Components]
```

## 🔍 Detailed Scanner Workflows

### 1. SAST Scanner Flow
```
    [Receive Scan Request]
             │
             ▼
    [Clone Repository]
             │
             ▼
    [Initialize Bandit Scanner]
             │
             ▼
    [Scan Python Files]
             │
             ├── [File 1] ──┐
             ├── [File 2] ──┼── [Analyze Code Patterns]
             └── [File N] ──┘
                     │
                     ▼
    [Generate Findings]
             │
             ├── [SQL Injection]
             ├── [Hardcoded Secrets]
             ├── [Weak Crypto]
             └── [Other Issues]
                     │
                     ▼
    [Parse Results to JSON]
             │
             ▼
    [Return to Main Process]
```

### 2. Secret Scanner Flow
```
    [Receive Scan Request]
             │
             ▼
    [Clone Repository]
             │
             ▼
    [Initialize TruffleHog]
             │
             ▼
    [Scan All Files for Patterns]
             │
             ├── [API Keys] ────┐
             ├── [Passwords] ───┼── [Pattern Matching]
             ├── [Tokens] ──────┤
             └── [Private Keys] ─┘
                     │
                     ▼
    [Validate Findings]
             │
             ├── [True Positive] ──► [High Confidence]
             ├── [False Positive] ──► [Low Confidence]
             └── [Uncertain] ──► [Medium Confidence]
                     │
                     ▼
    [Generate Report]
             │
             ▼
    [Return Secret Findings]
```

### 3. Dependency Scanner Flow
```
    [Receive Scan Request]
             │
             ▼
    [Clone Repository]
             │
             ▼
    [Detect Dependency Files]
             │
             ├── [requirements.txt] ──► [Python Dependencies]
             ├── [package.json] ──► [Node.js Dependencies]
             ├── [Gemfile] ──► [Ruby Dependencies]
             └── [composer.json] ──► [PHP Dependencies]
                     │
                     ▼
    [Parse Dependencies]
             │
             ▼
    [Check Against Vulnerability DB]
             │
             ├── [CVE Database]
             ├── [GitHub Advisory]
             └── [Security Advisories]
                     │
                     ▼
    [Generate Vulnerability Report]
             │
             ├── [Critical CVEs]
             ├── [High Severity]
             ├── [Medium Severity]
             └── [Low Severity]
                     │
                     ▼
    [Return Dependency Report]
```

## 📊 Data Processing Flows

### 1. Result Aggregation Flow
```
    [Receive Scanner Results]
             │
             ├── [SAST Results]
             ├── [Secret Results]
             └── [Dependency Results]
                     │
                     ▼
    [Normalize Data Format]
             │
             ▼
    [Apply Severity Mapping]
             │
             ├── [Critical] ──► [Requires Immediate Action]
             ├── [High] ──► [Fix Within 24h]
             ├── [Medium] ──► [Fix Within 1 Week]
             └── [Low] ──► [Fix When Convenient]
                     │
                     ▼
    [Deduplicate Findings]
             │
             ▼
    [Calculate Statistics]
             │
             ├── [Total Count]
             ├── [Severity Distribution]
             ├── [Scanner Breakdown]
             └── [Confidence Levels]
                     │
                     ▼
    [Store in Database]
             │
             ▼
    [Update Dashboard Metrics]
```

### 2. Real-time Update Flow
```
    [Scan Status Change]
             │
             ▼
    [Update Database Record]
             │
             ▼
    [Trigger Dashboard Refresh]
             │
             ▼
    [Frontend Polls for Updates]
             │
             ▼
    [Fetch Latest Data]
             │
             ├── [Scan Progress]
             ├── [New Vulnerabilities]
             └── [Updated Statistics]
                     │
                     ▼
    [Update UI Components]
             │
             ├── [Progress Bars]
             ├── [Charts]
             ├── [Statistics Cards]
             └── [Recent Scans List]
```

## 🔒 Security Process Flows

### 1. Input Validation Flow
```
    [User Input Received]
             │
             ▼
    [Check Input Type]
             │
             ├── [URL] ──► [Validate URL Format]
             ├── [String] ──► [Sanitize Special Characters]
             └── [JSON] ──► [Validate JSON Schema]
                     │
                     ▼
    [Apply Security Filters]
             │
             ├── [XSS Prevention]
             ├── [SQL Injection Prevention]
             └── [Path Traversal Prevention]
                     │
                     ▼
    [Validation Result]
             │
             ├── [Valid] ──► [Process Request]
             └── [Invalid] ──► [Return Error]
```

### 2. Error Handling Flow
```
    [Exception Occurs]
             │
             ▼
    [Determine Error Type]
             │
             ├── [Network Error] ──► [Retry Logic]
             ├── [Validation Error] ──► [Return 400]
             ├── [Authentication Error] ──► [Return 401]
             ├── [Authorization Error] ──► [Return 403]
             ├── [Resource Not Found] ──► [Return 404]
             ├── [Server Error] ──► [Return 500]
             └── [Unknown Error] ──► [Log & Return 500]
                     │
                     ▼
    [Log Error Details]
             │
             ▼
    [Send Error Response]
             │
             ▼
    [Update UI with Error Message]
```

## 🚀 Deployment Process Flow

### 1. CI/CD Pipeline Flow
```
    [Code Push to Repository]
             │
             ▼
    [Trigger Jenkins Pipeline]
             │
             ▼
    [Checkout Source Code]
             │
             ▼
    [Run Unit Tests]
             │
             ├── [Tests Fail] ──► [Stop Pipeline]
             │
             ▼ [Tests Pass]
    [Build Docker Images]
             │
             ▼
    [Run Security Scans]
             │
             ├── [Vulnerabilities Found] ──► [Alert Team]
             │
             ▼ [Clean]
    [Push to Container Registry]
             │
             ▼
    [Deploy to Staging]
             │
             ▼
    [Run Integration Tests]
             │
             ├── [Tests Fail] ──► [Rollback]
             │
             ▼ [Tests Pass]
    [Deploy to Production]
             │
             ▼
    [Health Check]
             │
             ├── [Unhealthy] ──► [Rollback]
             │
             ▼ [Healthy]
    [Deployment Complete]
```

### 2. Database Migration Flow
```
    [New Code Deployment]
             │
             ▼
    [Check for DB Changes]
             │
             ├── [No Changes] ──► [Skip Migration]
             │
             ▼ [Changes Detected]
    [Backup Current Database]
             │
             ▼
    [Run Migration Scripts]
             │
             ├── [Migration Fails] ──► [Restore Backup]
             │
             ▼ [Success]
    [Verify Data Integrity]
             │
             ├── [Issues Found] ──► [Restore Backup]
             │
             ▼ [Verified]
    [Update Application]
             │
             ▼
    [Migration Complete]
```

## 📈 Monitoring & Alerting Flow

```
    [System Metrics Collection]
             │
             ├── [API Response Times]
             ├── [Database Performance]
             ├── [Scanner Success Rates]
             └── [Error Rates]
                     │
                     ▼
    [Threshold Evaluation]
             │
             ├── [Normal] ──► [Continue Monitoring]
             │
             ▼ [Threshold Exceeded]
    [Generate Alert]
             │
             ├── [Email Notification]
             ├── [Slack Message]
             └── [Dashboard Warning]
                     │
                     ▼
    [Incident Response]
             │
             ├── [Auto-scaling]
             ├── [Manual Investigation]
             └── [System Recovery]
```

## 🔄 State Management Flow

```
    [Component State Change]
             │
             ▼
    [Update Local State]
             │
             ▼
    [Trigger Re-render]
             │
             ▼
    [Sync with Backend]
             │
             ├── [API Call Success] ──► [Confirm State]
             │
             ▼ [API Call Fails]
    [Revert to Previous State]
             │
             ▼
    [Show Error Message]
             │
             ▼
    [User Can Retry]
```