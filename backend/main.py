"""
FastAPI backend for Financial Dashboard Multi-Agent System
"""
import os
import logging
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
import tempfile
import shutil
from dotenv import load_dotenv

from agents.financial_workflow import FinancialWorkflow

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
numeric_level = getattr(logging, log_level, logging.DEBUG)

# Clear any existing handlers to avoid duplicates
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('financial_dashboard.log')
    ],
    force=True  # Force reconfiguration
)

# Create logger
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Dashboard API",
    description="Multi-agent system for financial analysis using LangGraph",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the financial workflow
financial_workflow = None

@app.on_event("startup")
async def startup_event():
    """Initialize the financial workflow on startup"""
    logger.info("Starting Financial Dashboard API")
    logger.debug("Initializing financial workflow")
    
    global financial_workflow
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is required")
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    logger.debug(f"OpenAI API key found: {openai_api_key[:8]}...")
    financial_workflow = FinancialWorkflow(openai_api_key)
    logger.info("Financial workflow initialized successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.debug("Root endpoint accessed")
    return {"message": "Financial Dashboard API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "service": "financial-dashboard-api"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a CSV file"""
    logger.info(f"File upload request received: {file.filename}")
    logger.debug(f"File size: {file.size} bytes, content type: {file.content_type}")
    
    if not file.filename.endswith('.csv'):
        logger.warning(f"Invalid file type uploaded: {file.filename}")
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    if not financial_workflow:
        logger.error("Financial workflow not initialized")
        raise HTTPException(status_code=500, detail="Financial workflow not initialized")
    
    # Create temporary file
    temp_file = None
    try:
        logger.debug("Creating temporary file for uploaded CSV")
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        logger.debug(f"Temporary file created: {temp_file_path}")
        logger.info("Starting file processing with financial workflow")
        
        # Process the file with timeout handling
        import asyncio
        try:
            # Run the processing in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            dashboard_data = await loop.run_in_executor(
                None, 
                financial_workflow.process_file, 
                temp_file_path
            )
        except asyncio.TimeoutError:
            logger.error("File processing timed out")
            raise HTTPException(status_code=408, detail="File processing timed out. Please try with a smaller file.")
        except Exception as e:
            logger.error(f"Error during file processing: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        
        logger.info("File processing completed successfully")
        logger.debug(f"Dashboard data keys: {list(dashboard_data.keys())}")
        
        return JSONResponse(content=dashboard_data)
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error processing file: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            logger.debug(f"Cleaning up temporary file: {temp_file.name}")
            os.unlink(temp_file.name)

@app.post("/analyze")
async def analyze_data(data: Dict[str, Any]):
    """Analyze financial data (for testing with sample data)"""
    logger.debug("Analyze endpoint accessed")
    logger.debug(f"Data received: {data}")
    
    if not financial_workflow:
        logger.error("Financial workflow not initialized")
        raise HTTPException(status_code=500, detail="Financial workflow not initialized")
    
    try:
        # This endpoint can be used for testing with sample data
        # For now, it returns a placeholder response
        logger.info("Analysis endpoint called with sample data")
        return JSONResponse(content={
            "message": "Analysis endpoint - use /upload for CSV file processing",
            "sample_data": data
        })
    
    except Exception as e:
        logger.error(f"Error analyzing data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Get available financial metrics"""
    logger.debug("Metrics endpoint accessed")
    return {
        "available_metrics": [
            "revenue",
            "expenses", 
            "income",
            "free_cash_flow"
        ],
        "time_periods": [
            "monthly",
            "quarterly",
            "yearly"
        ]
    }

if __name__ == "__main__":
    logger.info("Starting Financial Dashboard API server")
    logger.info(f"Log level set to: {log_level}")
    logger.debug("Uvicorn configuration: host=0.0.0.0, port=8000, reload=True")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
