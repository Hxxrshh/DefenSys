# Defensys - System Architecture Documentation

## 🏗️ System Overview

Defensys is a comprehensive DevSecOps vulnerability scanning platform that provides automated security analysis for repositories through multiple scanning engines.

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           DEFENSYS PLATFORM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐ │
│  │   Frontend      │    │   API Gateway    │    │  Database   │ │
│  │   Dashboard     │◄──►│   (Flask)        │◄──►│  (SQLite)   │ │
│  │   (HTML/JS)     │    │                  │    │             │ │
│  └─────────────────┘    └──────────────────┘    └─────────────┘ │
│                                   │                              │
│                                   ▼                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                SCANNING ENGINES                             │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │    SAST     │  │   Secrets   │  │    Dependencies     │ │ │
│  │  │  Scanner    │  │   Scanner   │  │     Scanner         │ │ │
│  │  │ (Bandit)    │  │(TruffleHog) │  │   (Safety/Audit)    │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Architecture

### 1. Frontend Layer
```
┌─────────────────────────────────────┐
│            Frontend                 │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐ │
│  │        Dashboard UI             │ │
│  │  • Security Overview           │ │
│  │  • Vulnerability Charts        │ │
│  │  • Scan Management             │ │
│  │  • Real-time Updates           │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │        Repository Scanner       │ │
│  │  • URL Input                   │ │
│  │  • Scan Type Selection         │ │
│  │  • Progress Tracking           │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 2. Backend API Layer
```
┌─────────────────────────────────────┐
│            API Layer                │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐ │
│  │        Flask Application        │ │
│  │  • REST API Endpoints          │ │
│  │  • Request Validation          │ │
│  │  • Response Formatting         │ │
│  │  • CORS Handling               │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │        Core Services            │ │
│  │  • Scan Orchestration          │ │
│  │  • Result Aggregation          │ │
│  │  • Data Processing             │ │
│  │  • Alert Generation            │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 3. Scanning Engine Layer
```
┌─────────────────────────────────────┐
│         Scanning Engines            │
├─────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐      │
│  │   SAST    │  │ Secrets   │      │
│  │ ┌───────┐ │  │ ┌───────┐ │      │
│  │ │Bandit │ │  │ │Truffle│ │      │
│  │ │Semgrep│ │  │ │Hog    │ │      │
│  │ └───────┘ │  │ └───────┘ │      │
│  └───────────┘  └───────────┘      │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │        Dependencies             │ │
│  │  ┌───────┐  ┌─────────────────┐ │ │
│  │  │Safety │  │   npm audit     │ │ │
│  │  └───────┘  └─────────────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 4. Data Layer
```
┌─────────────────────────────────────┐
│            Data Layer               │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐ │
│  │        SQLite Database          │ │
│  │                                 │ │
│  │  ┌─────────┐  ┌─────────────┐   │ │
│  │  │ Scans   │  │Vulnerabi-   │   │ │
│  │  │ Table   │  │lities Table │   │ │
│  │  └─────────┘  └─────────────┘   │ │
│  │                                 │ │
│  │  ┌─────────┐  ┌─────────────┐   │ │
│  │  │ Logs    │  │   Reports   │   │ │
│  │  │ Table   │  │   Table     │   │ │
│  │  └─────────┘  └─────────────┘   │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 🌐 Network Architecture

```
Internet
    │
    ▼
┌─────────────────┐
│   Load Balancer │ (Port 80/443)
│     (Nginx)     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Frontend      │ (Port 8080)
│   Server        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   API Server    │ (Port 5000)
│   (Flask)       │
└─────────────────┘
    │
    ├── Scanner Services ──┐
    │                      │
    ▼                      ▼
┌─────────────┐    ┌─────────────┐
│ SAST Engine │    │Secret Engine│
│ (Port 5001) │    │ (Port 5002) │
└─────────────┘    └─────────────┘
    │
    ▼
┌─────────────┐
│Dependency   │
│Engine       │
│(Port 5003)  │
└─────────────┘
```

## 📊 Data Flow Architecture

```
Repository URL Input
        │
        ▼
┌─────────────────┐
│   API Gateway   │
│   Validation    │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ Scan Controller │
│  • Create Scan  │
│  • Set Status   │
└─────────────────┘
        │
        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SAST Scan     │    │  Secret Scan    │    │Dependency Scan  │
│   • Clone Repo  │    │  • Clone Repo   │    │  • Clone Repo   │
│   • Run Bandit  │    │  • Run TruffleH │    │  • Run Safety   │
│   • Parse Results│    │  • Parse Results│    │  • Parse Results│
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                    ┌─────────────────┐
                    │ Result Processor│
                    │ • Aggregate     │
                    │ • Normalize     │
                    │ • Store Results │
                    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   Database      │
                    │   Storage       │
                    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   Dashboard     │
                    │   Update        │
                    └─────────────────┘
```

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Transport Security                       │ │
│  │  • HTTPS/TLS Encryption                                │ │
│  │  • Secure Headers                                      │ │
│  │  • CORS Policy                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Application Security                     │ │
│  │  • Input Validation                                    │ │
│  │  • SQL Injection Prevention                            │ │
│  │  • XSS Protection                                      │ │
│  │  • CSRF Protection                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Data Security                         │ │
│  │  • Database Encryption                                 │ │
│  │  • Sensitive Data Masking                              │ │
│  │  • Access Control                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🐳 Deployment Architecture

### Development Environment
```
Local Machine
├── Frontend Server (Python HTTP Server)
├── Backend API (Flask Development Server)
├── SQLite Database
└── Scanner Scripts (Local Python)
```

### Production Environment
```
Docker Containers
├── Nginx (Reverse Proxy)
├── Frontend Container
├── API Container
├── Database Container (PostgreSQL)
├── Scanner Containers
│   ├── SAST Scanner
│   ├── Secret Scanner
│   └── Dependency Scanner
└── Message Queue (RabbitMQ)
```

### Cloud Architecture (K8s)
```
Kubernetes Cluster
├── Ingress Controller
├── Frontend Pods (3 replicas)
├── API Pods (3 replicas)
├── Database StatefulSet
├── Scanner Jobs
└── Monitoring Stack
    ├── Prometheus
    ├── Grafana
    └── AlertManager
```

## 📈 Scalability Considerations

1. **Horizontal Scaling**
   - Multiple API server instances
   - Load balancer distribution
   - Scanner service replicas

2. **Database Scaling**
   - Read replicas
   - Connection pooling
   - Caching layer (Redis)

3. **Queue Management**
   - RabbitMQ for scan jobs
   - Worker processes
   - Job prioritization

4. **Storage Optimization**
   - Result compression
   - Archive old scans
   - CDN for static assets

## 🔄 Technology Stack

### Frontend
- **Framework**: Vanilla HTML/CSS/JavaScript
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **Server**: Python HTTP Server

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (Dev), PostgreSQL (Prod)
- **ORM**: SQLAlchemy
- **API**: RESTful endpoints

### Scanning Tools
- **SAST**: Bandit, Semgrep
- **Secrets**: TruffleHog
- **Dependencies**: Safety, npm audit

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: Jenkins
- **Monitoring**: Prometheus + Grafana