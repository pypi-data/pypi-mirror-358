"""
Enterprise Image Tracking System

Provides persistent duplicate detection, comprehensive tracking,
and CSV/database management for uploaded images.
"""

import sqlite3
import csv
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ImageRecord:
    """Represents a tracked image record."""
    
    # Core identification
    original_path: str              # Original file path or URL
    cloudflare_id: str              # Cloudflare image ID
    cloudflare_url: str             # Cloudflare delivery URL
    
    # Hashing and deduplication
    file_hash: Optional[str] = None         # SHA256 hash of file content
    url_hash: Optional[str] = None          # MD5 hash of URL
    
    # Metadata
    original_filename: str = ""             # Original filename
    file_size_bytes: int = 0                # File size in bytes
    mime_type: str = ""                     # MIME type
    upload_timestamp: float = 0             # Unix timestamp
    upload_date: str = ""                   # Human readable date
    
    # Source tracking
    source_project: str = ""                # Project name/path
    source_file: str = ""                   # File that referenced this image
    migration_session: str = ""             # Migration session ID
    
    # Quality and optimization
    was_optimized: bool = False             # Whether image was optimized
    original_size_bytes: int = 0            # Size before optimization
    compression_ratio: float = 0.0          # Compression ratio achieved
    quality_score: float = 0.0              # Quality analysis score
    
    # Security
    security_level: str = ""                # Security validation level
    security_issues: str = ""               # JSON string of issues found
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON/CSV export."""
        return asdict(self)


class ImageTracker:
    """Enterprise image tracking system with persistent storage."""
    
    def __init__(self, database_path: str = "cloudflare_images.db", 
                 csv_export_path: str = "cloudflare_images.csv"):
        self.database_path = Path(database_path)
        self.csv_export_path = Path(csv_export_path)
        self.session_id = self._generate_session_id()
        
        # In-memory cache for fast lookups
        self._hash_cache: Dict[str, ImageRecord] = {}
        self._url_cache: Dict[str, ImageRecord] = {}
        self._id_cache: Dict[str, ImageRecord] = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing records into cache
        self._load_cache()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID for this migration run."""
        timestamp = int(time.time())
        return f"migration_{timestamp}_{hashlib.md5(str(timestamp).encode()).hexdigest()[:8]}"
    
    def _init_database(self):
        """Initialize SQLite database with proper schema."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    -- Core identification
                    original_path TEXT NOT NULL,
                    cloudflare_id TEXT UNIQUE NOT NULL,
                    cloudflare_url TEXT NOT NULL,
                    
                    -- Hashing and deduplication
                    file_hash TEXT,
                    url_hash TEXT,
                    
                    -- Metadata
                    original_filename TEXT,
                    file_size_bytes INTEGER DEFAULT 0,
                    mime_type TEXT,
                    upload_timestamp REAL NOT NULL,
                    upload_date TEXT NOT NULL,
                    
                    -- Source tracking
                    source_project TEXT,
                    source_file TEXT,
                    migration_session TEXT,
                    
                    -- Quality and optimization
                    was_optimized BOOLEAN DEFAULT FALSE,
                    original_size_bytes INTEGER DEFAULT 0,
                    compression_ratio REAL DEFAULT 0.0,
                    quality_score REAL DEFAULT 0.0,
                    
                    -- Security
                    security_level TEXT,
                    security_issues TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for fast lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON uploaded_images(file_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_url_hash ON uploaded_images(url_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cloudflare_id ON uploaded_images(cloudflare_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_original_path ON uploaded_images(original_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON uploaded_images(migration_session)")
            
            conn.commit()
    
    def _load_cache(self):
        """Load existing records into memory cache for fast lookups."""
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM uploaded_images")
            
            for row in cursor:
                record = ImageRecord(
                    original_path=row['original_path'],
                    cloudflare_id=row['cloudflare_id'],
                    cloudflare_url=row['cloudflare_url'],
                    file_hash=row['file_hash'],
                    url_hash=row['url_hash'],
                    original_filename=row['original_filename'] or "",
                    file_size_bytes=row['file_size_bytes'] or 0,
                    mime_type=row['mime_type'] or "",
                    upload_timestamp=row['upload_timestamp'],
                    upload_date=row['upload_date'],
                    source_project=row['source_project'] or "",
                    source_file=row['source_file'] or "",
                    migration_session=row['migration_session'] or "",
                    was_optimized=bool(row['was_optimized']),
                    original_size_bytes=row['original_size_bytes'] or 0,
                    compression_ratio=row['compression_ratio'] or 0.0,
                    quality_score=row['quality_score'] or 0.0,
                    security_level=row['security_level'] or "",
                    security_issues=row['security_issues'] or ""
                )
                
                # Cache by different keys for fast lookups
                if record.file_hash:
                    self._hash_cache[record.file_hash] = record
                if record.url_hash:
                    self._url_cache[record.url_hash] = record
                self._id_cache[record.cloudflare_id] = record
    
    def check_duplicate_by_hash(self, file_hash: str) -> Optional[ImageRecord]:
        """Check if an image with this hash already exists."""
        return self._hash_cache.get(file_hash)
    
    def check_duplicate_by_url(self, url: str) -> Optional[ImageRecord]:
        """Check if an image from this URL already exists."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self._url_cache.get(url_hash)
    
    def check_duplicate_by_path(self, path: str) -> Optional[ImageRecord]:
        """Check if an image with this exact path already exists."""
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM uploaded_images WHERE original_path = ? LIMIT 1",
                (path,)
            )
            row = cursor.fetchone()
            if row:
                return ImageRecord(
                    original_path=row['original_path'],
                    cloudflare_id=row['cloudflare_id'],
                    cloudflare_url=row['cloudflare_url'],
                    file_hash=row['file_hash'],
                    url_hash=row['url_hash'],
                    original_filename=row['original_filename'] or "",
                    file_size_bytes=row['file_size_bytes'] or 0,
                    mime_type=row['mime_type'] or "",
                    upload_timestamp=row['upload_timestamp'],
                    upload_date=row['upload_date'],
                    source_project=row['source_project'] or "",
                    source_file=row['source_file'] or "",
                    migration_session=row['migration_session'] or "",
                    was_optimized=bool(row['was_optimized']),
                    original_size_bytes=row['original_size_bytes'] or 0,
                    compression_ratio=row['compression_ratio'] or 0.0,
                    quality_score=row['quality_score'] or 0.0,
                    security_level=row['security_level'] or "",
                    security_issues=row['security_issues'] or ""
                )
        return None
    
    def add_image_record(self, record: ImageRecord) -> bool:
        """Add a new image record to the tracking system."""
        try:
            # Ensure timestamp and date are set
            if not record.upload_timestamp:
                record.upload_timestamp = time.time()
            if not record.upload_date:
                record.upload_date = datetime.fromtimestamp(record.upload_timestamp).isoformat()
            if not record.migration_session:
                record.migration_session = self.session_id
            
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO uploaded_images (
                        original_path, cloudflare_id, cloudflare_url,
                        file_hash, url_hash, original_filename, file_size_bytes,
                        mime_type, upload_timestamp, upload_date,
                        source_project, source_file, migration_session,
                        was_optimized, original_size_bytes, compression_ratio,
                        quality_score, security_level, security_issues
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.original_path, record.cloudflare_id, record.cloudflare_url,
                    record.file_hash, record.url_hash, record.original_filename,
                    record.file_size_bytes, record.mime_type, record.upload_timestamp,
                    record.upload_date, record.source_project, record.source_file,
                    record.migration_session, record.was_optimized, record.original_size_bytes,
                    record.compression_ratio, record.quality_score, record.security_level,
                    record.security_issues
                ))
                conn.commit()
            
            # Update caches
            if record.file_hash:
                self._hash_cache[record.file_hash] = record
            if record.url_hash:
                self._url_cache[record.url_hash] = record
            self._id_cache[record.cloudflare_id] = record
            
            return True
            
        except Exception as e:
            print(f"Error adding image record: {e}")
            return False
    
    def get_all_records(self) -> List[ImageRecord]:
        """Get all image records from the database."""
        records = []
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM uploaded_images ORDER BY upload_timestamp DESC")
            
            for row in cursor:
                record = ImageRecord(
                    original_path=row['original_path'],
                    cloudflare_id=row['cloudflare_id'],
                    cloudflare_url=row['cloudflare_url'],
                    file_hash=row['file_hash'],
                    url_hash=row['url_hash'],
                    original_filename=row['original_filename'] or "",
                    file_size_bytes=row['file_size_bytes'] or 0,
                    mime_type=row['mime_type'] or "",
                    upload_timestamp=row['upload_timestamp'],
                    upload_date=row['upload_date'],
                    source_project=row['source_project'] or "",
                    source_file=row['source_file'] or "",
                    migration_session=row['migration_session'] or "",
                    was_optimized=bool(row['was_optimized']),
                    original_size_bytes=row['original_size_bytes'] or 0,
                    compression_ratio=row['compression_ratio'] or 0.0,
                    quality_score=row['quality_score'] or 0.0,
                    security_level=row['security_level'] or "",
                    security_issues=row['security_issues'] or ""
                )
                records.append(record)
        
        return records
    
    def export_to_csv(self, include_session_only: bool = False) -> bool:
        """Export image records to CSV file."""
        try:
            records = self.get_all_records()
            
            if include_session_only:
                records = [r for r in records if r.migration_session == self.session_id]
            
            if not records:
                return True
            
            # Ensure parent directory exists
            self.csv_export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.csv_export_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'original_path', 'cloudflare_id', 'cloudflare_url',
                    'file_hash', 'url_hash', 'original_filename',
                    'file_size_bytes', 'mime_type', 'upload_timestamp',
                    'upload_date', 'source_project', 'source_file',
                    'migration_session', 'was_optimized', 'original_size_bytes',
                    'compression_ratio', 'quality_score', 'security_level',
                    'security_issues'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in records:
                    writer.writerow(record.to_dict())
            
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about tracked images."""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute("SELECT COUNT(*) FROM uploaded_images")
            total_images = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM uploaded_images WHERE migration_session = ?", (self.session_id,))
            session_images = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT migration_session) FROM uploaded_images")
            total_sessions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM uploaded_images WHERE was_optimized = 1")
            optimized_images = cursor.fetchone()[0]
            
            # Size statistics
            cursor.execute("SELECT SUM(file_size_bytes), AVG(file_size_bytes) FROM uploaded_images")
            size_stats = cursor.fetchone()
            total_size = size_stats[0] or 0
            avg_size = size_stats[1] or 0
            
            # Compression statistics
            cursor.execute("SELECT AVG(compression_ratio) FROM uploaded_images WHERE compression_ratio > 0")
            avg_compression = cursor.fetchone()[0] or 0
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM uploaded_images 
                WHERE upload_timestamp > ?
            """, (time.time() - 86400,))  # Last 24 hours
            recent_uploads = cursor.fetchone()[0]
            
            return {
                'total_images': total_images,
                'session_images': session_images,
                'total_sessions': total_sessions,
                'optimized_images': optimized_images,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'average_size_mb': round(avg_size / (1024 * 1024), 2),
                'average_compression_ratio': round(avg_compression, 3),
                'recent_uploads_24h': recent_uploads,
                'current_session_id': self.session_id
            }
    
    def cleanup_old_sessions(self, keep_sessions: int = 10):
        """Clean up old migration session data, keeping only the most recent ones."""
        with sqlite3.connect(self.database_path) as conn:
            # Get session IDs ordered by newest first
            cursor = conn.execute("""
                SELECT DISTINCT migration_session 
                FROM uploaded_images 
                ORDER BY MAX(upload_timestamp) DESC
            """)
            sessions = [row[0] for row in cursor.fetchall()]
            
            if len(sessions) > keep_sessions:
                sessions_to_delete = sessions[keep_sessions:]
                
                # Delete old sessions
                placeholders = ','.join(['?'] * len(sessions_to_delete))
                conn.execute(f"""
                    DELETE FROM uploaded_images 
                    WHERE migration_session IN ({placeholders})
                """, sessions_to_delete)
                
                conn.commit()
                
                # Reload cache
                self._hash_cache.clear()
                self._url_cache.clear()
                self._id_cache.clear()
                self._load_cache() 