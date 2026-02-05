# SME Financial Health Assessment Platform

AI-powered financial health assessment platform for Small and Medium Enterprises (SMEs) in India. Analyzes financial statements, evaluates creditworthiness, identifies risks, and provides actionable recommendations.

## Features

### Core Capabilities
- **📊 Financial Analysis**: Comprehensive ratio analysis (liquidity, profitability, leverage, efficiency)
- **💳 Credit Scoring**: Multi-factor creditworthiness evaluation (300-900 scale)
- **⚠️ Risk Assessment**: Automated identification of liquidity, credit, operational, and market risks
- **💡 AI-Powered Insights**: GPT-4/Claude-generated recommendations in English and Hindi
- **📈 Cash Flow Analysis**: Operating, investing, and financing cash flow tracking
- **📋 Tax Compliance**: GST filing validation and tax optimization suggestions
- **🏦 Financial Product Recommendations**: Personalized suggestions for loans, credit lines, insurance
- **📄 Document Processing**: Automated parsing of CSV, Excel, and PDF financial statements
- **🌐 Multilingual Support**: English and Hindi interface and insights

### Integrations
- **Banking API**: Plaid integration for transaction syncing
- **Payment Gateway**: Razorpay for payment tracking
- **GST API**: Automated tax filing data import

### Security & Compliance
- **🔐 AES-256 Encryption**: Data at rest encryption
- **🔒 TLS 1.3**: Secure data transmission
- **🎫 JWT Authentication**: Token-based auth with refresh tokens
- **👥 Role-Based Access Control**: User permissions management
- **📝 Audit Logging**: Complete activity tracking
- **✅ Regulatory Compliance**: Data privacy and RBI guidelines

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI**: OpenAI GPT-4 / Anthropic Claude
- **Security**: Cryptography, PassLib (bcrypt), Python-JOSE (JWT)
- **Data Processing**: Pandas, NumPy
- **Document Parsing**: PyPDF2, pdfplumber, openpyxl

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: TailwindCSS
- **Charts**: Chart.js, Recharts
- **HTTP Client**: Axios
- **i18n**: i18next for multilingual support

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Server**: Uvicorn (ASGI)
- **Database**: PostgreSQL 15

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Docker (optional)

### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Copy example env file
cp ../.env.example .env

# Edit .env with your configuration
# Required: DATABASE_URL, SECRET_KEY, ENCRYPTION_KEY, OPENAI_API_KEY or CLAUDE_API_KEY
```

4. **Initialize database**
```bash
# Database will be automatically created on first run
# Alternatively, use the database.py script
python -c "from database.database import init_db; init_db()"
```

5. **Run backend server**
```bash
# Development
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/api/v1/docs`

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment**
```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env
```

3. **Run frontend**
```bash
npm start
```

Frontend will be available at `http://localhost:3000`

### Docker Setup (Recommended)

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Documentation

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Company Management
- `POST /api/v1/companies` - Create company
- `GET /api/v1/companies` - List companies
- `GET /api/v1/companies/{id}` - Get company details
- `PATCH /api/v1/companies/{id}` - Update company
- `DELETE /api/v1/companies/{id}` - Delete company

### Document Upload
- `POST /api/v1/upload/{company_id}/financial-statement` - Upload financial statement
- `POST /api/v1/upload/{company_id}/transactions` - Upload transactions

### Financial Analysis
- `GET /api/v1/analysis/{company_id}/ratios` - Calculate financial ratios
- `GET /api/v1/analysis/{company_id}/credit-score` - Calculate credit score
- `GET /api/v1/analysis/{company_id}/health-score` - Get health score with AI insights
- `GET /api/v1/analysis/{company_id}/cash-flow` - Analyze cash flow

Full API documentation available at `/api/v1/docs` when running the server.

## Project Structure

```
sme-financial-platform/
├── backend/
│   ├── config.py                 # Configuration management
│   ├── main.py                   # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   ├── database/
│   │   ├── database.py          # DB connection
│   │   └── models.py            # SQLAlchemy models
│   ├── security/
│   │   ├── encryption.py        # AES-256 encryption
│   │   ├── authentication.py    # JWT auth
│   │   └── audit_logger.py      # Audit logging
│   ├── services/
│   │   ├── parsers.py           # Document parsers
│   │   ├── financial_analyzer.py # Financial analysis
│   │   ├── credit_scoring.py    # Credit scoring
│   │   └── ai_service.py        # AI insights
│   └── routes/
│       ├── auth_routes.py       # Auth endpoints
│       ├── company_routes.py    # Company CRUD
│       ├── upload_routes.py     # File upload
│       └── analysis_routes.py   # Analysis endpoints
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/              # React pages
│   │   ├── components/         # Reusable components
│   │   └── i18n/              # Translations
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-for-jwt
ENCRYPTION_KEY=your-32-byte-encryption-key

# AI Provider (choose one)
OPENAI_API_KEY=sk-your-openai-key
# OR
CLAUDE_API_KEY=sk-ant-your-claude-key
AI_PROVIDER=openai  # or claude

# Banking Integration
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox  # sandbox, development, or production

# Payment Integration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret

# GST (Optional)
GST_CLIENT_ID=your-gst-client-id
GST_CLIENT_SECRET=your-gst-client-secret
```

## Usage Examples

### 1. Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure123","full_name":"John Doe"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secure123"
```

### 2. Create Company Profile
```bash
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"ABC Manufacturing",
    "industry":"Manufacturing",
    "annual_revenue":5000000
  }'
```

### 3. Upload Financial Statement
```bash
curl -X POST http://localhost:8000/api/v1/upload/1/financial-statement \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@balance_sheet.xlsx" \
  -F "statement_type=balance_sheet" \
  -F "period_start=2023-01-01" \
  -F "period_end=2023-12-31"
```

### 4. Get Financial Health Score
```bash
curl -X GET http://localhost:8000/api/v1/analysis/1/health-score?language=en \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Security Best Practices

1. **Always use HTTPS in production**
2. **Change default SECRET_KEY and ENCRYPTION_KEY**
3. **Use strong passwords** (min 8 characters, mixed case, numbers, symbols)
4. **Regularly rotate API keys**
5. **Enable database backups**
6. **Monitor audit logs** for suspicious activity
7. **Keep dependencies updated**

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Python linting
flake8 backend/
black backend/

# TypeScript linting
cd frontend
npm run lint
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in config
- [ ] Use production database (not SQLite)
- [ ] Configure proper SECRET_KEY and ENCRYPTION_KEY
- [ ] Enable HTTPS/TLS
- [ ] Set up database backups
- [ ] Configure CORS for production domains
- [ ] Set up monitoring and logging
- [ ] Use environment-specific .env files
- [ ] Enable rate limiting
- [ ] Set up CDN for static assets

## Support & Documentation

- **API Documentation**: `/api/v1/docs` (Swagger UI)
- **Alternative Docs**: `/api/v1/redoc` (ReDoc)

## License

Proprietary - All Rights Reserved

## Contributors

Built for SME financial health assessment in India.

---

**Version**: 1.0.0  
**Last Updated**: February 2026
