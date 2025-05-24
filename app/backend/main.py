from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import logging
import traceback
import os
from typing import Dict, Any

from app.backend.security_funded import get_data
from app.backend.database import db_manager
from app.backend.models import PaginationParams, PaginatedResponse, CompanyData
from app.shared.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS more specifically
CORS(app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type"])

def create_query(search_term: str = None, filter_round: str = None) -> Dict[str, Any]:
    """Create MongoDB query from search and filter parameters"""
    query = {}
    
    if search_term:
        query['$or'] = [
            {'company_name': {'$regex': search_term, '$options': 'i'}},
            {'description': {'$regex': search_term, '$options': 'i'}},
            {'company_type': {'$regex': search_term, '$options': 'i'}}
        ]
    
    if filter_round:
        query['round'] = filter_round
    
    logger.debug(f"Created query: {query}")
    return query

def format_company_data(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Format MongoDB document for API response"""
    # Process investors properly
    investors = doc.get('investors', [])
    processed_investors = []
    
    for inv in investors:
        if isinstance(inv, dict):
            processed_investors.append({
                'name': inv.get('name', ''),
                'url': inv.get('url', '')
            })
        else:
            processed_investors.append({
                'name': str(inv),
                'url': ''
            })
    
    return {
        'id': str(doc.get('_id')),
        'description': doc.get('description', ''),
        'company_name': doc.get('company_name', ''),
        'company_url': doc.get('company_url', ''),
        'amount': doc.get('amount', 0),
        'round': doc.get('round', ''),
        'investors': processed_investors,
        'story_link': doc.get('story_link', ''),
        'source': doc.get('Source', doc.get('source', '')),
        'date': doc.get('date', ''),
        'company_type': doc.get('company_type', ''),
        'reference': doc.get('reference', '')
    }

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'error': 'Internal server error',
        'message': str(e) if app.debug else 'An unexpected error occurred'
    }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    try:
        # Test database connection
        db_diagnostics = db_manager.test_connection()
        
        health_status = {
            'status': 'healthy' if db_diagnostics['connected'] else 'unhealthy',
            'timestamp': str(db_manager),
            'database': {
                'connected': db_diagnostics['connected'],
                'database_name': db_diagnostics['database_name'],
                'collection_name': db_diagnostics['collection_name'],
                'document_count': db_diagnostics['document_count']
            },
            'environment': {
                'flask_host': Config.FLASK_HOST,
                'flask_port': Config.FLASK_PORT,
                'api_base_url': Config.API_BASE_URL
            }
        }
        
        if db_diagnostics.get('error'):
            health_status['database']['error'] = db_diagnostics['error']
        
        status_code = 200 if db_diagnostics['connected'] else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@app.route('/api/funding-data', methods=['GET'])
def get_funding_data():
    """API endpoint to fetch paginated funding data"""
    try:
        logger.info("Received funding data request")
        
        # Parse query parameters
        params = PaginationParams(
            page=int(request.args.get('page', 1)),
            items_per_page=min(int(request.args.get('itemsPerPage', Config.DEFAULT_PAGE_SIZE)), Config.MAX_PAGE_SIZE),
            sort_field=request.args.get('sortField', 'date'),
            sort_direction=request.args.get('sortDirection', 'desc'),
            search=request.args.get('search', '').strip() or None,
            filter_round=request.args.get('filterRound', '').strip() or None
        )
        
        logger.info(f"Query params: page={params.page}, items_per_page={params.items_per_page}, sort={params.sort_field}, search='{params.search}', filter='{params.filter_round}'")
        
        # Build query
        query = create_query(params.search, params.filter_round)
        
        # Get total count
        total_count = db_manager.count_documents(query)
        logger.info(f"Total documents matching query: {total_count}")
        
        # Calculate pagination
        skip = params.get_skip()
        total_pages = (total_count + params.items_per_page - 1) // params.items_per_page
        
        # Fetch data
        documents = db_manager.find_with_pagination(
            query, 
            params.sort_field, 
            params.sort_direction, 
            skip, 
            params.items_per_page
        )
        
        logger.info(f"Retrieved {len(documents)} documents")
        
        # Format data
        formatted_data = [format_company_data(doc) for doc in documents]
        
        # Create response
        response = PaginatedResponse(
            data=formatted_data,
            total_count=total_count,
            total_pages=total_pages,
            current_page=params.page,
            items_per_page=params.items_per_page
        )
        
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error fetching funding data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'type': 'funding_data_error'
        }), 500

@app.route('/api/funding-rounds', methods=['GET'])
def get_funding_rounds():
    """API endpoint to get unique funding rounds for filter"""
    try:
        logger.info("Fetching funding rounds")
        rounds = db_manager.distinct('round')
        rounds = [r for r in rounds if r]  # Filter out empty values
        rounds.sort()
        
        logger.info(f"Found {len(rounds)} unique funding rounds")
        return jsonify({'rounds': rounds}), 200
        
    except Exception as e:
        logger.error(f"Error fetching funding rounds: {str(e)}")
        return jsonify({
            'error': str(e),
            'type': 'funding_rounds_error'
        }), 500

@app.route('/api/get_data', methods=['GET'])
def api_get_data():
    """API endpoint to trigger data collection"""
    try:
        logger.info("Manual data collection triggered")
        result = get_data()
        
        message = f"Data collection complete. Processed: {result['processed']}, Skipped: {result['skipped']}, Errors: {result['errors']}"
        logger.info(message)
        
        return jsonify({
            "message": message,
            "details": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in data collection: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "type": "data_collection_error"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API endpoint to get database statistics"""
    try:
        logger.info("Fetching database statistics")
        
        total_companies = db_manager.count_documents({})
        total_funding = 0
        
        # Calculate total funding (this might be expensive for large datasets)
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        collection = db_manager.get_collection()
        result = list(collection.aggregate(pipeline))
        if result:
            total_funding = result[0]['total']
        
        # Get funding by type
        type_pipeline = [
            {"$group": {"_id": "$company_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        type_stats = list(collection.aggregate(type_pipeline))
        
        stats = {
            'total_companies': total_companies,
            'total_funding': total_funding,
            'funding_by_type': type_stats
        }
        
        logger.info(f"Stats: {total_companies} companies, ${total_funding:,} total funding")
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({
            'error': str(e),
            'type': 'stats_error'
        }), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check configuration and connections"""
    try:
        debug_data = {
            'config': {
                'flask_host': Config.FLASK_HOST,
                'flask_port': Config.FLASK_PORT,
                'api_base_url': Config.API_BASE_URL,
                'db_name': Config.DB_NAME,
                'collection_name': Config.COLLECTION_NAME
            },
            'environment': {
                'docker_env': os.getenv('DOCKER_ENV', 'false'),
                'flask_debug': Config.FLASK_DEBUG
            },
            'database': db_manager.test_connection()
        }
        
        return jsonify(debug_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def scheduled_data_collection():
    """Scheduled data collection function"""
    try:
        logger.info("Scheduled data collection started")
        result = get_data()
        logger.info(f"Scheduled data collection completed: {result}")
    except Exception as e:
        logger.error(f"Error in scheduled data collection: {str(e)}")

def create_app():
    """Create and configure Flask app"""
    logger.info("Initializing Flask application...")
    
    # Initialize database connection
    logger.info("Testing database connection...")
    if not db_manager.connect():
        logger.error("Failed to connect to database - API will continue but may not function properly")
        # Don't raise exception - let the app start for debugging
    
    # Initialize and start the scheduler
    logger.info("Starting background scheduler...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=scheduled_data_collection,
        trigger=IntervalTrigger(hours=Config.SCHEDULER_INTERVAL_HOURS),
        id='data_collection_job',
        name='Collect data every 4 hours',
        replace_existing=True
    )
    scheduler.start()
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    logger.info(f"Flask app created and configured on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    logger.info(f"API base URL: {Config.API_BASE_URL}")
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting Flask server on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)