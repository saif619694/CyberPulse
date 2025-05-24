# 🛡️ CyberPulse - Security Funding Intelligence

A comprehensive Python application for tracking and analyzing cybersecurity funding data in real-time. Built with Flask backend and Streamlit frontend, providing professional-grade market intelligence.

## ✨ Features

### 🔍 Data Collection & Management
- **Automated web scraping** from security funding sources
- **Real-time data collection** with configurable scheduling
- **MongoDB integration** for robust data storage
- **Duplicate detection** and data validation

### 📊 Advanced Analytics
- **Interactive data visualization** with Plotly charts
- **Multiple view modes**: Cards, Table, and Chart views
- **Advanced search & filtering** capabilities
- **Real-time statistics** and market insights

### 🎨 Modern User Interface
- **Professional Streamlit frontend** with cyberpunk-inspired design
- **Responsive layout** optimized for desktop and mobile
- **Dark theme** with customizable preferences
- **Intuitive navigation** and user experience

### ⚡ High Performance
- **Asynchronous processing** for data collection
- **Efficient pagination** for large datasets
- **Caching mechanisms** for improved performance
- **Background scheduling** for automated updates

## 🏗️ Architecture

```
security-funded-python/
├── app/
│   ├── backend/          # Flask API & Data Processing
│   │   ├── main.py       # Flask application
│   │   ├── security_funded.py  # Web scraping logic
│   │   ├── models.py     # Data models
│   │   └── database.py   # MongoDB interface
│   ├── frontend/         # Streamlit Application
│   │   ├── streamlit_app.py    # Main Streamlit app
│   │   ├── components/   # UI components
│   │   └── utils/        # Utilities & API client
│   └── shared/           # Shared configuration
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-service setup
└── requirements.txt      # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB Atlas account or local MongoDB
- Docker & Docker Compose (optional)

### 1. Clone Repository

```bash
git clone <repository-url>
cd security-funded-python
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your MongoDB credentials
nano .env
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install requirements
pip install -r requirements.txt
```

### 4. Run Application

#### Option A: Using Startup Script
```bash
chmod +x start.sh
./start.sh
```

#### Option B: Manual Start
```bash
# Terminal 1 - Start Flask API
python -m app.backend.main

# Terminal 2 - Start Streamlit Frontend
streamlit run app/frontend/streamlit_app.py
```

#### Option C: Using Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### 5. Access Application

- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health

## 📋 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USERNAME` | MongoDB username | Required |
| `DB_PASSWORD` | MongoDB password | Required |
| `FLASK_HOST` | Flask server host | 127.0.0.1 |
| `FLASK_PORT` | Flask server port | 8000 |
| `STREAMLIT_HOST` | Streamlit host | 127.0.0.1 |
| `STREAMLIT_PORT` | Streamlit port | 8501 |
| `API_BASE_URL` | API base URL | http://127.0.0.1:8000 |
| `DEFAULT_PAGE_SIZE` | Default pagination size | 12 |
| `SCHEDULER_INTERVAL_HOURS` | Data collection interval | 4 |

## 🔧 API Endpoints

### Data Endpoints
- `GET /api/funding-data` - Get paginated funding data
- `GET /api/funding-rounds` - Get available funding rounds
- `GET /api/stats` - Get database statistics

### Management Endpoints
- `GET /api/get_data` - Trigger data collection
- `GET /api/health` - Health check

### Query Parameters
- `page` - Page number (default: 1)
- `itemsPerPage` - Items per page (default: 12)
- `sortField` - Sort field (date, company_name, amount)
- `sortDirection` - Sort direction (asc, desc)
- `search` - Search term
- `filterRound` - Filter by funding round

## 📊 Data Sources

The application currently scrapes data from:
- **Return on Security** - Primary cybersecurity funding source
- **Public funding announcements**
- **Venture capital databases**

### Data Fields
- Company name and URL
- Funding amount and round
- Investor information
- Company type (Product/Service)
- Funding date
- Source links

## 🛠️ Development

### Project Structure

```
app/
├── backend/
│   ├── main.py              # Flask API server
│   ├── security_funded.py   # Web scraping engine
│   ├── models.py            # Data models & validation
│   └── database.py          # MongoDB operations
├── frontend/
│   ├── streamlit_app.py     # Main Streamlit application
│   ├── components/          # Reusable UI components
│   │   ├── header.py        # Header & branding
│   │   ├── search_bar.py    # Search & filters
│   │   ├── data_display.py  # Data visualization
│   │   └── sidebar.py       # Navigation & settings
│   └── utils/
│       ├── api_client.py    # API communication
│       └── formatters.py    # Data formatting utilities
└── shared/
    └── config.py            # Shared configuration
```

### Adding New Features

1. **Backend**: Add new endpoints in `app/backend/main.py`
2. **Frontend**: Create components in `app/frontend/components/`
3. **Data Models**: Extend models in `app/backend/models.py`
4. **Styling**: Update CSS in `app/frontend/streamlit_app.py`

### Testing

```bash
# Run API tests
python -m pytest tests/test_api.py

# Run scraping tests
python -m pytest tests/test_scraping.py

# Manual testing
python -m app.backend.security_funded
```

## 📦 Deployment

### Docker Deployment

```bash
# Build image
docker build -t cyberpulse .

# Run container
docker run -p 8000:8000 -p 8501:8501 --env-file .env cyberpulse
```

### Production Deployment

1. **Set environment variables** for production
2. **Configure MongoDB** connection string
3. **Set up reverse proxy** (Nginx) if needed
4. **Enable HTTPS** for security
5. **Configure monitoring** and logging

### Docker Compose Production

```bash
# Run with production profile
docker-compose --profile production up -d
```

## 🔒 Security Considerations

- **Environment Variables**: Never commit `.env` files
- **MongoDB**: Use strong credentials and connection encryption
- **Rate Limiting**: Implement rate limiting for API endpoints
- **CORS**: Configure CORS properly for production
- **HTTPS**: Use HTTPS in production environments

## 📈 Performance Optimization

- **Database Indexing**: Optimize MongoDB queries with proper indexes
- **Caching**: Implement Redis caching for frequently accessed data
- **Lazy Loading**: Use pagination and lazy loading for large datasets
- **Background Processing**: Use Celery for heavy data processing tasks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check the wiki for detailed documentation
- **Discord**: Join our community Discord server

## 🙏 Acknowledgments

- **Return on Security** for providing funding data
- **Streamlit** for the amazing frontend framework
- **Flask** for the robust backend framework
- **MongoDB** for reliable data storage

---

**Built with ❤️ by the CyberPulse Team**

🛡️ *Tracking the pulse of cybersecurity innovation*