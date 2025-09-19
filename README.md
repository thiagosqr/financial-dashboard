# Financial Dashboard Multi-Agent System

A sophisticated financial analysis web application built with LangGraph multi-agent architecture, featuring AI-powered insights and interactive visualizations.

## 🏗️ Architecture

This application uses a multi-agent system based on LangGraph, inspired by the [Phoenix LangGraph tutorial](https://github.com/Arize-ai/phoenix/tree/main/tutorials/agents/langgraph):

- **Data Ingest Agent**: Processes CSV files and validates transaction data
- **Financial Analysis Agent**: Calculates metrics and generates AI-powered insights
- **LangGraph Workflow**: Orchestrates the agents using a state-based workflow
- **React Frontend**: Interactive dashboard with real-time visualizations
- **FastAPI Backend**: RESTful API connecting frontend to agents

## 🚀 Features

### Dashboard Tiles
- **Revenue**: Current vs previous month with trend analysis
- **Expenses**: Expense tracking with category breakdown
- **Profitability**: Net profit/loss calculations
- **Cash Flow**: Cash flow analysis and projections

### Interactive Features
- Click any tile to view detailed time series charts
- AI-generated insights and recommendations for each metric
- Month-over-month comparison analysis
- Responsive design for desktop and mobile

### AI-Powered Analysis
- Intelligent transaction categorization using LLM
- Narrative insights explaining financial trends
- Actionable recommendations based on data patterns
- Trend analysis (increasing, decreasing, stable)

## 📁 Project Structure

```
financial-dashboard/
├── backend/
│   ├── agents/
│   │   ├── data_ingest_agent.py      # CSV processing agent
│   │   ├── financial_analysis_agent.py # Financial calculations agent
│   │   └── financial_workflow.py     # LangGraph workflow orchestration
│   ├── main.py                       # FastAPI application
│   ├── requirements.txt              # Python dependencies
│   └── env_example.txt              # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FinancialTile.tsx     # Dashboard tile component
│   │   │   ├── TimeSeriesChart.tsx   # Chart visualization component
│   │   │   └── FileUpload.tsx        # File upload component
│   │   ├── services/
│   │   │   └── api.ts               # API service layer
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript type definitions
│   │   ├── App.tsx                  # Main application component
│   │   └── App.css                  # Application styles
│   └── package.json                 # Node.js dependencies
├── data/
│   └── sample_transactions.csv      # Sample data for testing
└── README.md                        # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Quick Start (Recommended)

1. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **Run the demo to test the system:**
   ```bash
   python demo.py
   ```

3. **Start the full application:**
   ```bash
   ./start.sh
   ```

### Manual Setup

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your OpenAI API key
   ```

4. **Start the backend server:**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`

### Docker Setup (Alternative)

1. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **Start with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

## 📊 Usage

1. **Upload Data**: Upload a CSV file with your business transactions
2. **View Dashboard**: See the four key financial metrics in the dashboard tiles
3. **Explore Insights**: Click any tile to view detailed charts and AI insights
4. **Analyze Trends**: Review month-over-month comparisons and recommendations

### CSV Format Requirements

Your CSV file should include these columns:
- `date`: Transaction date (YYYY-MM-DD format)
- `description`: Transaction description
- `amount`: Transaction amount (positive for income, negative for expenses)
- `category`: Transaction category
- `account`: Account name

## 🤖 Multi-Agent System Details

### Data Ingest Agent
- Validates CSV file format and data quality
- Cleans and standardizes transaction data
- Uses LLM for intelligent transaction categorization
- Handles missing or malformed data gracefully

### Financial Analysis Agent
- Calculates monthly financial metrics
- Performs month-over-month comparisons
- Generates time series data for visualizations
- Creates AI-powered insights and recommendations

### LangGraph Workflow
- Orchestrates agent execution using state management
- Handles error recovery and data flow
- Enables parallel processing where possible
- Provides traceability for debugging

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
PHOENIX_API_KEY=your_phoenix_api_key_here  # Optional for tracing
PHOENIX_COLLECTOR_ENDPOINT=your_phoenix_endpoint_here  # Optional
```

### API Configuration

The frontend connects to the backend API. Update the API URL in `frontend/src/services/api.ts` if needed:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

## 🧪 Testing

Use the provided sample data file (`data/sample_transactions.csv`) to test the application:

1. Start both backend and frontend servers
2. Open the application in your browser
3. Upload the sample CSV file
4. Explore the dashboard and insights

## 🚀 Deployment

### Backend Deployment
- Deploy to cloud platforms (AWS, GCP, Azure)
- Use containerization with Docker
- Set up environment variables in production

### Frontend Deployment
- Build for production: `npm run build`
- Deploy to static hosting (Netlify, Vercel, AWS S3)
- Update API URL for production backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for the multi-agent framework
- [Phoenix](https://github.com/Arize-ai/phoenix) for the LangGraph tutorial inspiration
- [Recharts](https://recharts.org/) for data visualization
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API
- [React](https://reactjs.org/) for the frontend framework
