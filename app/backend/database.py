from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from app.shared.config import Config
import logging
import time

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connected = False
        
    def connect(self):
        """Establish database connection with better error handling"""
        try:
            logger.info(f"Connecting to MongoDB at: {Config.MONGO_URI[:50]}...")
            
            # Create client with specific timeout settings
            self.client = MongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=10000,  # 10 second timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                maxPoolSize=10
            )
            
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[Config.DB_NAME]
            self.collection = self.db[Config.COLLECTION_NAME]
            self._connected = True
            
            # Log connection success with some stats
            doc_count = self.collection.count_documents({})
            logger.info(f"Successfully connected to MongoDB. Database: {Config.DB_NAME}, Collection: {Config.COLLECTION_NAME}")
            logger.info(f"Total documents in collection: {doc_count}")
            
            return True
            
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB server selection timeout: {str(e)}")
            logger.error("Check if MongoDB Atlas is accessible and credentials are correct")
            return False
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failure: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            logger.error(f"MongoDB URI (masked): {Config.MONGO_URI[:30]}...")
            return False
    
    def is_connected(self):
        """Check if database is connected"""
        if not self._connected or not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            self._connected = False
            return False
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Database connection closed")
    
    def get_collection(self):
        """Get the collection object with connection check"""
        if not self.is_connected():
            logger.info("Database not connected, attempting to reconnect...")
            if not self.connect():
                raise Exception("Cannot establish database connection")
        return self.collection
    
    def insert_many(self, documents):
        """Insert multiple documents with error handling"""
        try:
            collection = self.get_collection()
            result = collection.insert_many(documents)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} documents")
            return result
        except Exception as e:
            logger.error(f"Error inserting documents: {str(e)}")
            raise
    
    def find_one(self, query):
        """Find one document with error handling"""
        try:
            collection = self.get_collection()
            return collection.find_one(query)
        except Exception as e:
            logger.error(f"Error finding document: {str(e)}")
            raise
    
    def find_with_pagination(self, query, sort_field, sort_direction, skip, limit):
        """Find documents with pagination and sorting"""
        try:
            collection = self.get_collection()
            
            # Map sort fields
            sort_field_map = {
                'company_name': 'company_name',
                'amount': 'amount',
                'date': 'date'
            }
            
            mongo_sort_field = sort_field_map.get(sort_field, 'date')
            sort_order = DESCENDING if sort_direction == 'desc' else ASCENDING
            
            logger.debug(f"Executing query: {query}, sort: {mongo_sort_field} {sort_direction}, skip: {skip}, limit: {limit}")
            
            cursor = collection.find(query).sort(mongo_sort_field, sort_order).skip(skip).limit(limit)
            results = list(cursor)
            
            logger.debug(f"Query returned {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Error finding documents with pagination: {str(e)}")
            raise
    
    def count_documents(self, query):
        """Count documents matching query"""
        try:
            collection = self.get_collection()
            count = collection.count_documents(query)
            logger.debug(f"Count query returned: {count}")
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {str(e)}")
            raise
    
    def distinct(self, field):
        """Get distinct values for a field"""
        try:
            collection = self.get_collection()
            values = collection.distinct(field)
            logger.debug(f"Distinct query for '{field}' returned {len(values)} unique values")
            return values
        except Exception as e:
            logger.error(f"Error getting distinct values: {str(e)}")
            raise
    
    def test_connection(self):
        """Test database connection and return diagnostics"""
        diagnostics = {
            "connected": False,
            "database_name": Config.DB_NAME,
            "collection_name": Config.COLLECTION_NAME,
            "document_count": 0,
            "error": None
        }
        
        try:
            if self.connect():
                diagnostics["connected"] = True
                diagnostics["document_count"] = self.collection.count_documents({})
            else:
                diagnostics["error"] = "Connection failed"
        except Exception as e:
            diagnostics["error"] = str(e)
        
        return diagnostics

# Global database manager instance
db_manager = DatabaseManager()