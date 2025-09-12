# DefenSys - Comprehensive DevSecOps Vulnerability Scanner

DefenSys is a modern DevSecOps monitoring and threat detection platform designed to seamlessly integrate into development pipelines, providing real-time vulnerability scanning and security insights.

## 🏗️ Project Structure

```
defensys/
├── backend/
│   └── defensys/          # Flask API backend
│       ├── src/
│       │   ├── server.py  # Main API server
│       │   ├── models.py  # Database models
│       │   └── core/      # Security scanners
│       └── requirements.txt
├── frontend/
│   └── defensys-dash/     # React dashboard
│       ├── src/
│       │   ├── components/
│       │   └── services/
│       └── package.json
├── docker-compose.yml     # Service orchestration
├── defensys.py           # Management script
└── README.md
```

## 🛡️ Features

- **SAST (Static Application Security Testing)**: Code vulnerability detection
- **Secret Detection**: Exposed credentials and API keys scanning
- **Dependency Scanning**: Known vulnerability detection in packages
- **Real-time Dashboard**: Interactive web interface
- **CI/CD Integration**: GitHub/GitLab webhook support
- **Multi-language Support**: Python, JavaScript, Java, Go, and more

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Access the dashboard
open http://localhost:8081
```

### Manual Setup

```bash
# Start API server
cd c:\Users\hys20\Desktop\Devsyns\vulnwatch\backend\defensys
python src/server.py

# Start frontend (new terminal)
cd c:\Users\hys20\Desktop\Devsyns\vulnwatch\frontend\defensys-dash
npm install
npm run dev
```

## 🔧 Architecture

- **Frontend**: React + TypeScript + Vite
- **Backend**: Flask + SQLAlchemy + PostgreSQL
- **Scanners**: Bandit, Semgrep, TruffleHog, pip-audit
- **Infrastructure**: Docker, Redis, RabbitMQ

## 📊 Usage

1. Open the dashboard at http://localhost:8081
2. Click "Start New Scan"
3. Enter a repository URL
4. Select scan types (SAST, SECRET, DEPENDENCY)
5. Monitor results in real-time

## 🛠️ Development

```bash
# Run tests
pytest tests/

# Format code
black src/

# Lint code
flake8 src/
```

## 📝 License

MIT License - see LICENSE file for details
