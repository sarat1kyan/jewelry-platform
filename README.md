# Jewelry Customization Platform

A complete web platform for jewelry customization with CAD file matching and Monday.com integration.

## Quick Start

1. **Configure Monday.com credentials:**
   ```bash
   nano config.ini
   # Add your API key and board ID
   ```

2. **Add your Excel file:**
   ```bash
   cp /path/to/SLS-final-nam-lab\ 3.xlsx config_files/
   ```

3. **Start the platform:**

   **Option A - Development mode:**
   ```bash
   ./start.sh
   ```

   **Option B - Docker deployment:**
   ```bash
   ./deploy.sh
   ```

4. **Access the platform:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Features

- Dynamic parameter selection for jewelry specifications
- Intelligent CAD file matching with scoring algorithm
- Monday.com integration for production workflow
- RESTful API with comprehensive endpoints
- Modern React frontend with Tailwind CSS
- Docker support for easy deployment
- Production-ready with monitoring and logging
- Database support for scaling beyond CSV files

## Project Structure

```
jewelry-platform/
├── app.py                 # Flask backend
├── config.ini            # Configuration
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # Backend container
├── start.sh             # Development start script
├── deploy.sh            # Deployment script
├── test.sh              # Test runner
├── config_files/        # CSV and Excel data
│   ├── Abbreviation_Map.csv
│   ├── Reverse_Mapping.csv
│   ├── Filenames.csv
│   └── SLS-final-nam-lab 3.xlsx
├── frontend/            # React frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
└── tests/               # Test suite
```

## API Endpoints

- `GET /api/parameters` - Get available selection parameters
- `POST /api/generate-filename` - Generate CAD filename
- `POST /api/find-matches` - Find matching CAD files
- `POST /api/create-task` - Create Monday.com task
- `GET /api/health` - Health check
- `POST /api/reload-data` - Reload data files

## Configuration

Edit `config.ini` to configure:
- CAD file directory path
- Monday.com API credentials
- Data file locations

## Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install
   ```

2. **Run tests:**
   ```bash
   ./test.sh
   ```

3. **Start development servers:**
   ```bash
   ./start.sh
   ```

## Production Deployment

See the comprehensive documentation for:
- Kubernetes deployment with Helm
- CI/CD pipeline setup
- Database migration from CSV
- Monitoring with Prometheus/Grafana
- SSL/HTTPS configuration

## Support

For issues or questions, check the troubleshooting guide or contact the development team.
