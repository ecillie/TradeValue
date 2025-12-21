# TradeValue - NHL Contract Value Prediction

A full-stack web application that predicts NHL player contract values using machine learning. The application scrapes player data, contract information, and statistics from public sources, stores them in a PostgreSQL database, and uses ML models to predict contract cap hits based on player performance metrics.

## Features

- **Player Database**: Browse and search through NHL players with their statistics and contract information
- **Contract Analysis**: View detailed contract information including cap hits, duration, and total value
- **ML Predictions**: Predict contract values based on player statistics using trained machine learning models
- **Data Scraping**: Automated data collection from CapWages and NHL API
- **Web Interface**: Modern React frontend with responsive design

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **scikit-learn** - Machine learning models
- **pandas** - Data manipulation and analysis
- **Requests** - HTTP library for web scraping

### Frontend
- **React** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## Project Structure

```
TradeValue/
├── backend/
│   ├── app/
│   │   ├── ml/                    # Machine learning pipeline
│   │   │   ├── data/              # Dataset building and feature engineering
│   │   │   ├── training/          # Model training scripts
│   │   │   ├── inference/         # Prediction logic
│   │   │   └── artifacts/         # Trained models
│   │   ├── routers/               # API route handlers
│   │   ├── ScriptingFiles/        # Data scraping scripts
│   │   ├── config.py              # Configuration
│   │   ├── database.py            # Database setup
│   │   ├── models.py              # SQLAlchemy models
│   │   └── main.py                # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── common/           # Reusable UI components
│   │   │   ├── players/          # Player-related components
│   │   │   ├── contracts/        # Contract-related components
│   │   │   └── Layout/           # Layout components
│   │   ├── pages/                # Page components
│   │   ├── services/             # API service layer
│   │   ├── utils/                # Utility functions
│   │   └── config/               # Configuration
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Database Schema

The application uses three main tables:

### player_info
Stores basic player information:
- `id` (Primary Key)
- `firstname`, `lastname`
- `team`
- `position`
- `age`

### contracts
Stores contract details:
- `id` (Primary Key)
- `player_id` (Foreign Key → player_info.id)
- `team`, `start_year`, `end_year`, `duration`
- `cap_hit` (target variable for ML models)
- `rfa`, `elc` (boolean flags)
- `cap_pct`, `total_value`

### basic_player_stats
Stores player statistics by season:
- `id` (Primary Key)
- `player_id` (Foreign Key → player_info.id)
- `contract_id` (Foreign Key → contracts.id)
- `season`, `playoff` (boolean), `team`
- `gp`, `goals`, `assists`, `points`
- `plus_minus`, `pim`, `shots`, `shootpct`

## Setup

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (can run locally or use Docker)
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Environment Variables

Create a `.env` file in the root directory:

```env
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_database_name
```

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd TradeValue
```

2. Create `.env` file with database credentials (see above)

3. Start the services:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development Setup

#### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in backend directory with database credentials

5. Initialize database:
```bash
python3 -c "from app.database import init_db; init_db()"
```

6. Run the development server:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

## Data Collection

### Scraping Players

Scrape active players from CapWages:
```bash
cd backend
python3 -m app.ScriptingFiles.save_players_to_db
```

### Scraping Contracts

Scrape contract data for all players:
```bash
python3 -m app.ScriptingFiles.save_contracts_to_db
```

### Scraping Statistics

Scrape player statistics from NHL API:
```bash
python3 -m app.ScriptingFiles.save_basic_player_stats
```

Note: The NHL API has rate limits. The scripts include delays and retry logic to handle this.

## Machine Learning Pipeline

### Training Models

Train models for forwards and defensemen:
```bash
cd backend
python3 -m app.ml.training.train_player_model
```

This will:
- Load player data from the database
- Build features from historical statistics
- Train separate models for forwards and defensemen
- Save models to `backend/app/ml/artifacts/`

### Evaluating Models

Evaluate trained models:
```bash
python3 -m app.ml.training.evaluate
```

### Making Predictions

Use the prediction API endpoint or the web interface to make predictions based on player statistics.

## API Endpoints

### Players
- `GET /api/players` - Get all players
- `GET /api/players/{id}` - Get player by ID
- `GET /api/players/search` - Search players (query params: name, team, position)

### Contracts
- `GET /api/players/contracts` - Get all contracts
- `GET /api/players/contracts/{id}` - Get contract by ID
- `GET /api/players/{player_id}/contracts` - Get contracts for a player

### Statistics
- `GET /api/players/{player_id}/stats` - Get player statistics (query params: season, team, playoff)

### ML/Predictions
- `POST /api/ml/predict` - Predict contract value
  - Body: `{ position, gp, goals, assists, points, plus_minus, pim, shots, shootpct }`

See http://localhost:8000/docs for interactive API documentation.

## Usage

1. **Browse Players**: Navigate to the Players page to view and search through the player database
2. **View Contracts**: Check the Contracts page to see contract details and values
3. **Make Predictions**: Use the Predictions page to input player statistics and get contract value predictions

## Development

### Database Configuration

The backend connects to PostgreSQL. Configure connection in `backend/app/config.py` or via environment variables:
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

### Running Tests

Tests can be added to verify data scraping, model training, and API endpoints.

## Notes

- The application scrapes data from public APIs. Respect rate limits and terms of service.
- Models are trained on historical data and may not reflect current market conditions.
- Contract predictions are estimates based on statistical analysis and should not be considered financial advice.

