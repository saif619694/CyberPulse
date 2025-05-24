from pymongo import MongoClient, ASCENDING, DESCENDING
from app.shared.config import Config
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client[Config.DB_NAME]
            self.collection = self.db[Config.COLLECTION_NAME]
            logger.info("Successfully connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    def get_collection(self):
        """Get the collection object"""
        if not self.collection:
            self.connect()
        return self.collection
    
    def insert_many(self, documents):
        """Insert multiple documents"""
        try:
            collection = self.get_collection()
            result = collection.insert_many(documents)
            return result
        except Exception as e:
            logger.error(f"Error inserting documents: {str(e)}")
            raise
    
    def find_one(self, query):
        """Find one document"""
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
            
            cursor = collection.find(query).sort(mongo_sort_field, sort_order).skip(skip).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error finding documents with pagination: {str(e)}")
            raise
    
    def count_documents(self, query):
        """Count documents matching query"""
        try:
            collection = self.get_collection()
            return collection.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting documents: {str(e)}")
            raise
    
    def distinct(self, field):
        """Get distinct values for a field"""
        try:
            collection = self.get_collection()
            return collection.distinct(field)
        except Exception as e:
            logger.error(f"Error getting distinct values: {str(e)}")
            raise

# Global database manager instance
db_manager = DatabaseManager()