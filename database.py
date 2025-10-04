import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from typing import List, Dict, Optional

class FuzzyDatabase:
    def __init__(self, host: str = "localhost", database: str = "fuzzy_irrigation", 
                 user: str = "root", password: str = "", port: int = 3306):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.connect()
    
    def connect(self):
        """Create connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            if self.connection.is_connected():
                print(f"Successfully connected to MySQL database: {self.database}")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            self.connection = None
    
    def get_connection(self):
        """Get database connection, reconnect if needed"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection
    
    def save_calculation(self, calculation_data: Dict) -> int:
        """Save fuzzy calculation result to database"""
        connection = self.get_connection()
        if not connection:
            raise Exception("Database connection failed")
            
        cursor = connection.cursor()
        
        try:
            insert_query = """
                INSERT INTO fuzzy_calculations 
                (kelembaban_input, cuaca_input, durasi_output, tingkat_kebutuhan,
                 kelembaban_tanah, suhu, kelembaban_udara, curah_hujan, status_pompa, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                calculation_data.get('kelembaban_input'),
                calculation_data.get('cuaca_input'),
                calculation_data.get('durasi_output'),
                calculation_data.get('tingkat_kebutuhan'),
                calculation_data.get('kelembaban_tanah'),
                calculation_data.get('suhu'),
                calculation_data.get('kelembaban_udara'),
                calculation_data.get('curah_hujan'),
                calculation_data.get('status_pompa'),
                calculation_data.get('timestamp')
            )
            
            cursor.execute(insert_query, values)
            connection.commit()
            
            calculation_id = cursor.lastrowid
            return calculation_id
            
        except Error as e:
            print(f"Database error: {e}")
            connection.rollback()
            raise e
        finally:
            cursor.close()
    
    def get_all_calculations(self, limit: int = 100) -> List[Dict]:
        """Get all calculations from database"""
        connection = self.get_connection()
        if not connection:
            return []
            
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT * FROM fuzzy_calculations 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            results = cursor.fetchall()
            return results
            
        except Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            cursor.close()
    
    def get_calculations_by_weather(self, weather_condition: str) -> List[Dict]:
        """Get calculations filtered by weather condition"""
        connection = self.get_connection()
        if not connection:
            return []
            
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT * FROM fuzzy_calculations 
                WHERE cuaca_input = %s
                ORDER BY created_at DESC
            """, (weather_condition,))
            
            results = cursor.fetchall()
            return results
            
        except Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            cursor.close()
    
    def get_calculation_statistics(self) -> Dict:
        """Get statistical insights from calculations"""
        connection = self.get_connection()
        if not connection:
            return {}
            
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Total calculations
            cursor.execute("SELECT COUNT(*) as total FROM fuzzy_calculations")
            total_result = cursor.fetchone()
            total_calculations = total_result['total'] if total_result else 0
            
            # Weather distribution
            cursor.execute("""
                SELECT cuaca_input, COUNT(*) as count 
                FROM fuzzy_calculations 
                GROUP BY cuaca_input
            """)
            weather_dist = {row['cuaca_input']: row['count'] for row in cursor.fetchall()}
            
            # Average duration by weather
            cursor.execute("""
                SELECT cuaca_input, AVG(durasi_output) as avg_duration 
                FROM fuzzy_calculations 
                GROUP BY cuaca_input
            """)
            avg_duration = {row['cuaca_input']: round(row['avg_duration'], 2) for row in cursor.fetchall()}
            
            # Need level distribution
            cursor.execute("""
                SELECT tingkat_kebutuhan, COUNT(*) as count 
                FROM fuzzy_calculations 
                GROUP BY tingkat_kebutuhan
            """)
            need_dist = {row['tingkat_kebutuhan']: row['count'] for row in cursor.fetchall()}
            
            # Recent calculations (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) as recent_count 
                FROM fuzzy_calculations 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            recent_result = cursor.fetchone()
            recent_calculations = recent_result['recent_count'] if recent_result else 0
            
            # Humidity ranges
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN kelembaban_input < 30 THEN 'Rendah (0-29%)'
                        WHEN kelembaban_input < 60 THEN 'Sedang (30-59%)'
                        ELSE 'Tinggi (60-100%)'
                    END as humidity_range,
                    COUNT(*) as count
                FROM fuzzy_calculations 
                GROUP BY humidity_range
            """)
            humidity_ranges = {row['humidity_range']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total_calculations': total_calculations,
                'weather_distribution': weather_dist,
                'avg_duration_by_weather': avg_duration,
                'need_level_distribution': need_dist,
                'recent_calculations': recent_calculations,
                'humidity_ranges': humidity_ranges,
                'generated_at': datetime.now().isoformat()
            }
            
        except Error as e:
            print(f"Database error: {e}")
            return {}
        finally:
            cursor.close()
    
    def get_recent_calculations(self, limit: int = 10) -> List[Dict]:
        """Get recent calculations"""
        connection = self.get_connection()
        if not connection:
            return []
            
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT * FROM fuzzy_calculations 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            results = cursor.fetchall()
            return results
            
        except Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            cursor.close()
    
    def delete_old_calculations(self, days_old: int = 30) -> int:
        """Delete calculations older than specified days"""
        connection = self.get_connection()
        if not connection:
            return 0
            
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM fuzzy_calculations 
                WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
            """, (days_old,))
            
            connection.commit()
            deleted_count = cursor.rowcount
            return deleted_count
            
        except Error as e:
            print(f"Database error: {e}")
            connection.rollback()
            return 0
        finally:
            cursor.close()
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close_connection()