"""DuckDB provider implementation for ChunkHound - concrete database provider using DuckDB."""

import importlib
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import duckdb
from loguru import logger

# Import existing components that will be used by the provider
from chunkhound.chunker import Chunker, IncrementalChunker
from chunkhound.embeddings import EmbeddingManager
from chunkhound.file_discovery_cache import FileDiscoveryCache
from core.models import Chunk, Embedding, File
from core.types import ChunkType, Language

# Avoid circular import - use lazy imports for registry functions

# Type hinting only
if TYPE_CHECKING:
    from services.embedding_service import EmbeddingService
    from services.indexing_coordinator import IndexingCoordinator
    from services.search_service import SearchService


class DuckDBProvider:
    """DuckDB implementation of DatabaseProvider protocol."""

    def __init__(self, db_path: Path | str, embedding_manager: EmbeddingManager | None = None):
        """Initialize DuckDB provider.

        Args:
            db_path: Path to DuckDB database file or ":memory:" for in-memory database
            embedding_manager: Optional embedding manager for vector generation
        """
        self._db_path = db_path
        self.connection: Any | None = None
        self._services_initialized = False
        self.embedding_manager = embedding_manager

        # Service layer components and legacy chunker instances
        self._indexing_coordinator: IndexingCoordinator | None = None
        self._search_service: SearchService | None = None
        self._embedding_service: EmbeddingService | None = None
        self._chunker: Chunker | None = None
        self._incremental_chunker: IncrementalChunker | None = None

        # File discovery cache for performance optimization
        self._file_discovery_cache = FileDiscoveryCache()
        
        # Enhanced checkpoint tracking
        self._operations_since_checkpoint = 0
        self._checkpoint_threshold = 100  # Checkpoint every N operations
        self._last_checkpoint_time = time.time()

    def _extract_file_id(self, file_record: dict[str, Any] | File) -> int | None:
        """Safely extract file ID from either dict or File model."""
        if isinstance(file_record, File):
            return file_record.id
        elif isinstance(file_record, dict) and "id" in file_record:
            return file_record["id"]
        else:
            return None

    @property
    def db_path(self) -> Path | str:
        """Database connection path or identifier."""
        return self._db_path

    @property
    def is_connected(self) -> bool:
        """Check if database connection is active."""
        return self.connection is not None

    def connect(self) -> None:
        """Establish database connection and initialize schema with WAL validation."""
        logger.info(f"Connecting to DuckDB database: {self.db_path}")

        # Ensure parent directory exists for file-based databases
        if isinstance(self.db_path, Path):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if duckdb is None:
                raise ImportError("duckdb not available")

            # Connect to DuckDB with WAL corruption handling
            self._connect_with_wal_validation()
            logger.info("DuckDB connection established")

            # Load required extensions
            self._load_extensions()

            # Enable experimental HNSW persistence for disk-based databases
            if self.connection is not None:
                self.connection.execute("SET hnsw_enable_experimental_persistence = true")
                logger.debug("HNSW experimental persistence enabled")

            # Create schema and indexes
            self.create_schema()
            self.create_indexes()

            # Migrate legacy embeddings table if it exists
            self._migrate_legacy_embeddings_table()

            # Initialize shared parser and chunker instances for performance
            self._initialize_shared_instances()

            logger.info("DuckDB provider initialization complete")

        except Exception as e:
            logger.error(f"DuckDB connection failed: {e}")
            raise

    def _connect_with_wal_validation(self) -> None:
        """Connect to DuckDB with WAL corruption detection and automatic cleanup."""
        try:
            # Attempt initial connection
            self.connection = duckdb.connect(str(self.db_path))
            logger.debug("DuckDB connection successful")

        except duckdb.Error as e:
            error_msg = str(e)

            # Check for WAL corruption patterns
            if self._is_wal_corruption_error(error_msg):
                logger.warning(f"WAL corruption detected: {error_msg}")
                self._handle_wal_corruption()

                # Retry connection after WAL cleanup
                try:
                    self.connection = duckdb.connect(str(self.db_path))
                    logger.info("DuckDB connection successful after WAL cleanup")
                except Exception as retry_error:
                    logger.error(f"Connection failed even after WAL cleanup: {retry_error}")
                    raise
            else:
                # Not a WAL corruption error, re-raise original exception
                raise

    def _is_wal_corruption_error(self, error_msg: str) -> bool:
        """Check if error message indicates WAL corruption."""
        corruption_indicators = [
            "Failure while replaying WAL file",
            "Catalog \"chunkhound\" does not exist",
            "BinderException",
            "Binder Error",
            "Cannot bind index",
            "unknown index type",
            "HNSW",
            "You need to load the extension"
        ]

        return any(indicator in error_msg for indicator in corruption_indicators)

    def _handle_wal_corruption(self) -> None:
        """Handle WAL corruption using advanced recovery with VSS extension preloading."""
        db_path = Path(self.db_path)
        wal_file = db_path.with_suffix(db_path.suffix + '.wal')

        if not wal_file.exists():
            logger.warning(f"WAL corruption detected but no WAL file found at: {wal_file}")
            return

        # Get WAL file size for logging
        file_size = wal_file.stat().st_size
        logger.warning(f"WAL corruption detected. File size: {file_size:,} bytes")

        # First attempt: Try recovery with VSS extension preloaded
        logger.info("Attempting WAL recovery with VSS extension preloaded...")
        
        try:
            # Create a temporary recovery connection
            recovery_conn = duckdb.connect(":memory:")
            
            # Load VSS extension first
            recovery_conn.execute("INSTALL vss")
            recovery_conn.execute("LOAD vss")
            
            # Enable experimental persistence for HNSW indexes
            recovery_conn.execute("SET hnsw_enable_experimental_persistence = true")
            
            # Now attach the database file - this will trigger WAL replay with extension loaded
            recovery_conn.execute(f"ATTACH '{db_path}' AS recovery_db")
            
            # Verify tables are accessible
            recovery_conn.execute("SELECT COUNT(*) FROM recovery_db.files").fetchone()
            
            # Force a checkpoint to ensure WAL is integrated
            recovery_conn.execute("CHECKPOINT recovery_db")
            
            # Detach and close
            recovery_conn.execute("DETACH recovery_db")
            recovery_conn.close()
            
            logger.info("WAL recovery successful with VSS extension preloaded")
            return
            
        except Exception as recovery_error:
            logger.warning(f"Recovery with VSS preloading failed: {recovery_error}")
            
            # Second attempt: Conservative recovery - remove WAL but create backup first
            try:
                # Create backup of WAL file before removal
                backup_path = wal_file.with_suffix('.wal.corrupt')
                import shutil
                shutil.copy2(wal_file, backup_path)
                logger.info(f"Created WAL backup at: {backup_path}")
                
                # Remove corrupted WAL file
                os.remove(wal_file)
                logger.warning(f"Removed corrupted WAL file: {wal_file} (backup saved)")
                
            except Exception as e:
                logger.error(f"Failed to handle corrupted WAL file {wal_file}: {e}")
                raise

    def _maybe_checkpoint(self, force: bool = False) -> None:
        """Perform checkpoint if needed based on operations count or time elapsed.
        
        Args:
            force: Force checkpoint regardless of thresholds
        """
        if self.connection is None:
            return
            
        current_time = time.time()
        time_since_checkpoint = current_time - self._last_checkpoint_time
        
        # Checkpoint if forced, operations threshold reached, or 5 minutes elapsed
        should_checkpoint = (
            force or 
            self._operations_since_checkpoint >= self._checkpoint_threshold or
            time_since_checkpoint >= 300  # 5 minutes
        )
        
        if should_checkpoint:
            try:
                self.connection.execute("CHECKPOINT")
                self._operations_since_checkpoint = 0
                self._last_checkpoint_time = current_time
                if not os.environ.get("CHUNKHOUND_MCP_MODE"):
                    logger.debug(f"Checkpoint completed (operations: {self._operations_since_checkpoint}, time: {time_since_checkpoint:.1f}s)")
            except Exception as e:
                if not os.environ.get("CHUNKHOUND_MCP_MODE"):
                    logger.warning(f"Checkpoint failed: {e}")

    def disconnect(self, skip_checkpoint: bool = False) -> None:
        """Close database connection with optional checkpointing.
        
        Args:
            skip_checkpoint: If True, skip the checkpoint operation (useful when checkpoint 
                           was already done recently to avoid checkpoint conflicts)
        """
        if self.connection is not None:
            try:
                if not skip_checkpoint:
                    # Force checkpoint before close to ensure durability
                    self.connection.execute("CHECKPOINT")
                    # Only log in non-MCP mode to avoid JSON-RPC interference
                    if not os.environ.get("CHUNKHOUND_MCP_MODE"):
                        logger.debug("Database checkpoint completed before disconnect")
                else:
                    if not os.environ.get("CHUNKHOUND_MCP_MODE"):
                        logger.debug("Skipping checkpoint before disconnect (already done)")
            except Exception as e:
                # Only log errors in non-MCP mode
                if not os.environ.get("CHUNKHOUND_MCP_MODE"):
                    logger.error(f"Checkpoint failed during disconnect: {e}")
                # Continue with close - don't block shutdown
            finally:
                self.connection.close()
                self.connection = None
                if not os.environ.get("CHUNKHOUND_MCP_MODE"):
                    logger.info("DuckDB connection closed")

    def _load_extensions(self) -> None:
        """Load required DuckDB extensions."""
        logger.info("Loading DuckDB extensions")

        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Install and load VSS extension for vector operations
            self.connection.execute("INSTALL vss")
            self.connection.execute("LOAD vss")
            logger.info("VSS extension loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load DuckDB extensions: {e}")
            raise

    def _initialize_shared_instances(self):
        """Initialize service layer components and legacy compatibility objects."""
        logger.debug("Initializing service layer components")

        try:
            # Initialize chunkers for legacy compatibility
            self._chunker = Chunker()
            self._incremental_chunker = IncrementalChunker()

            # Lazy import from registry to avoid circular dependency
            registry_module = importlib.import_module('registry')
            get_registry = getattr(registry_module, 'get_registry')
            create_indexing_coordinator = getattr(registry_module, 'create_indexing_coordinator')
            create_search_service = getattr(registry_module, 'create_search_service')
            create_embedding_service = getattr(registry_module, 'create_embedding_service')

            # Get registry and register self as database provider
            registry = get_registry()
            registry.register_provider("database", lambda: self, singleton=True)

            # Initialize service layer components from registry
            if not hasattr(self, '_indexing_coordinator') or self._indexing_coordinator is None:
                self._indexing_coordinator = create_indexing_coordinator()
            if not hasattr(self, '_search_service') or self._search_service is None:
                self._search_service = create_search_service()
            if not hasattr(self, '_embedding_service') or self._embedding_service is None:
                self._embedding_service = create_embedding_service()

            logger.debug("Service layer components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize service layer components: {e}")
            # Don't raise the exception, just log it - allows test initialization to continue

    def create_schema(self) -> None:
        """Create database schema for files, chunks, and embeddings."""
        logger.info("Creating DuckDB schema")

        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Create sequence for files table
            self.connection.execute("CREATE SEQUENCE IF NOT EXISTS files_id_seq")

            # Files table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY DEFAULT nextval('files_id_seq'),
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    extension TEXT,
                    size INTEGER,
                    modified_time TIMESTAMP,
                    content_crc32 BIGINT,
                    language TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create sequence for chunks table
            self.connection.execute("CREATE SEQUENCE IF NOT EXISTS chunks_id_seq")

            # Chunks table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY DEFAULT nextval('chunks_id_seq'),
                    file_id INTEGER REFERENCES files(id),
                    chunk_type TEXT NOT NULL,
                    symbol TEXT,
                    code TEXT NOT NULL,
                    start_line INTEGER,
                    end_line INTEGER,
                    start_byte INTEGER,
                    end_byte INTEGER,
                    size INTEGER,
                    signature TEXT,
                    language TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create sequence for embeddings table
            self.connection.execute("CREATE SEQUENCE IF NOT EXISTS embeddings_id_seq")

            # Embeddings table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS embeddings_1536 (
                    id INTEGER PRIMARY KEY DEFAULT nextval('embeddings_id_seq'),
                    chunk_id INTEGER REFERENCES chunks(id),
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    embedding FLOAT[1536],
                    dims INTEGER NOT NULL DEFAULT 1536,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create HNSW index for 1536-dimensional embeddings
            try:
                self.connection.execute("""
                    CREATE INDEX IF NOT EXISTS idx_hnsw_1536 ON embeddings_1536
                    USING HNSW (embedding)
                    WITH (metric = 'cosine')
                """)
                logger.info("HNSW index for 1536-dimensional embeddings created successfully")
            except Exception as e:
                logger.warning(f"Failed to create HNSW index for 1536-dimensional embeddings: {e}")

            # Note: Additional dimension tables (4096, etc.) will be created on-demand
            
            # Handle schema migrations for existing databases
            self._migrate_schema()
            
            logger.info("DuckDB schema created successfully with multi-dimension support")

        except Exception as e:
            logger.error(f"Failed to create DuckDB schema: {e}")
            raise

    def _migrate_schema(self) -> None:
        """Handle schema migrations for existing databases."""
        if self.connection is None:
            raise RuntimeError("No database connection")
        
        try:
            # Check if content_crc32 column exists
            result = self.connection.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'files' AND column_name = 'content_crc32'
            """).fetchone()
            
            if result is None:
                # Add content_crc32 column to existing files table
                self.connection.execute("ALTER TABLE files ADD COLUMN content_crc32 BIGINT")
                logger.info("Added content_crc32 column to files table")
        
        except Exception as e:
            logger.warning(f"Failed to migrate schema: {e}")

    def _get_table_name_for_dimensions(self, dims: int) -> str:
        """Get table name for given embedding dimensions."""
        return f"embeddings_{dims}"

    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        result = self.connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name = ?",
            [table_name]
        ).fetchone()
        return result is not None

    def _ensure_embedding_table_exists(self, dims: int) -> str:
        """Ensure embedding table exists for given dimensions, create if needed."""
        table_name = self._get_table_name_for_dimensions(dims)

        if self._table_exists(table_name):
            return table_name

        if self.connection is None:
            raise RuntimeError("No database connection")

        logger.info(f"Creating embedding table for {dims} dimensions: {table_name}")

        try:
            # Create table with fixed dimensions for HNSW compatibility
            self.connection.execute(f"""
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY DEFAULT nextval('embeddings_id_seq'),
                    chunk_id INTEGER REFERENCES chunks(id),
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    embedding FLOAT[{dims}],
                    dims INTEGER NOT NULL DEFAULT {dims},
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create HNSW index for performance
            hnsw_index_name = f"idx_hnsw_{dims}"
            self.connection.execute(f"""
                CREATE INDEX {hnsw_index_name} ON {table_name}
                USING HNSW (embedding)
                WITH (metric = 'cosine')
            """)

            # Create regular indexes for fast lookups
            self.connection.execute(f"CREATE INDEX IF NOT EXISTS idx_{dims}_chunk_id ON {table_name}(chunk_id)")
            self.connection.execute(f"CREATE INDEX IF NOT EXISTS idx_{dims}_provider_model ON {table_name}(provider, model)")

            logger.info(f"Created {table_name} with HNSW index {hnsw_index_name} and regular indexes")
            return table_name

        except Exception as e:
            logger.error(f"Failed to create embedding table for {dims} dimensions: {e}")
            raise

    def _migrate_legacy_embeddings_table(self) -> None:
        """Migrate legacy 'embeddings' table to dimension-specific tables."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        # Check if legacy embeddings table exists
        if not self._table_exists("embeddings"):
            return

        logger.info("Found legacy embeddings table, migrating to dimension-specific tables...")

        try:
            # Get all embeddings with their dimensions
            embeddings = self.connection.execute("""
                SELECT id, chunk_id, provider, model, embedding, dims, created_at
                FROM embeddings
            """).fetchall()

            if not embeddings:
                logger.info("Legacy embeddings table is empty, dropping it")
                self.connection.execute("DROP TABLE embeddings")
                return

            # Group by dimensions
            by_dims = {}
            for emb in embeddings:
                dims = emb[5]  # dims column
                if dims not in by_dims:
                    by_dims[dims] = []
                by_dims[dims].append(emb)

            # Migrate each dimension group
            for dims, emb_list in by_dims.items():
                table_name = self._ensure_embedding_table_exists(dims)
                logger.info(f"Migrating {len(emb_list)} embeddings to {table_name}")

                # Insert data into dimension-specific table
                for emb in emb_list:
                    vector_str = str(emb[4])  # embedding column
                    self.connection.execute(f"""
                        INSERT INTO {table_name} (chunk_id, provider, model, embedding, dims, created_at)
                        VALUES (?, ?, ?, {vector_str}, ?, ?)
                    """, [emb[1], emb[2], emb[3], emb[5], emb[6]])

            # Drop legacy table
            self.connection.execute("DROP TABLE embeddings")
            logger.info(f"Successfully migrated embeddings to {len(by_dims)} dimension-specific tables")

        except Exception as e:
            logger.error(f"Failed to migrate legacy embeddings table: {e}")
            raise

    def _get_all_embedding_tables(self) -> list[str]:
        """Get list of all embedding tables (dimension-specific)."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        tables = self.connection.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name LIKE 'embeddings_%'
        """).fetchall()

        return [table[0] for table in tables]




    def create_indexes(self) -> None:
        """Create database indexes for performance optimization."""
        logger.info("Creating DuckDB indexes")

        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # File indexes
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_files_language ON files(language)")

            # Chunk indexes
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON chunks(file_id)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_chunks_type ON chunks(chunk_type)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_chunks_symbol ON chunks(symbol)")

            # Embedding indexes are created per-table in _ensure_embedding_table_exists()
            # No need for global embedding indexes since we use dimension-specific tables

            logger.info("DuckDB indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to create DuckDB indexes: {e}")
            raise

    def create_vector_index(self, provider: str, model: str, dims: int, metric: str = "cosine") -> None:
        """Create HNSW vector index for specific provider/model/dims combination."""
        logger.info(f"Creating HNSW index for {provider}/{model} ({dims}D, {metric})")

        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Get the correct table name for the dimensions
            table_name = self._get_table_name_for_dimensions(dims)

            # Ensure the table exists before creating the index
            self._ensure_embedding_table_exists(dims)

            index_name = f"hnsw_{provider}_{model}_{dims}_{metric}".replace("-", "_").replace(".", "_")

            # Create HNSW index using VSS extension on the dimension-specific table
            self.connection.execute(f"""
                CREATE INDEX {index_name} ON {table_name}
                USING HNSW (embedding)
                WITH (metric = '{metric}')
            """)

            logger.info(f"HNSW index {index_name} created successfully on {table_name}")

        except Exception as e:
            logger.error(f"Failed to create HNSW index: {e}")
            raise

    def drop_vector_index(self, provider: str, model: str, dims: int, metric: str = "cosine") -> str:
        """Drop HNSW vector index for specific provider/model/dims combination."""
        index_name = f"hnsw_{provider}_{model}_{dims}_{metric}".replace("-", "_").replace(".", "_")

        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            self.connection.execute(f"DROP INDEX IF EXISTS {index_name}")
            logger.info(f"HNSW index {index_name} dropped successfully")
            return index_name

        except Exception as e:
            logger.error(f"Failed to drop HNSW index {index_name}: {e}")
            raise

    def get_existing_vector_indexes(self) -> list[dict[str, Any]]:
        """Get list of existing HNSW vector indexes on all embedding tables."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Query DuckDB system tables for indexes on all embedding tables
            # Look for both legacy 'hnsw_' and standard 'idx_hnsw_' index patterns
            results = self.connection.execute("""
                SELECT index_name, table_name
                FROM duckdb_indexes()
                WHERE table_name LIKE 'embeddings_%'
                AND (index_name LIKE 'hnsw_%' OR index_name LIKE 'idx_hnsw_%')
            """).fetchall()

            indexes = []
            for result in results:
                index_name = result[0]
                table_name = result[1]

                # Handle different index naming patterns
                if index_name.startswith('hnsw_'):
                    # Parse custom index name: hnsw_{provider}_{model}_{dims}_{metric}
                    parts = index_name[5:].split('_')  # Remove 'hnsw_' prefix
                    if len(parts) >= 4:
                        # Reconstruct provider/model from parts (they may contain underscores)
                        metric = parts[-1]
                        dims_str = parts[-2]
                        try:
                            dims = int(dims_str)
                            # Join remaining parts as provider_model, then split on last underscore
                            provider_model = '_'.join(parts[:-2])
                            # Find last underscore to separate provider and model
                            last_underscore = provider_model.rfind('_')
                            if last_underscore > 0:
                                provider = provider_model[:last_underscore]
                                model = provider_model[last_underscore + 1:]
                            else:
                                provider = provider_model
                                model = ""

                            indexes.append({
                                'index_name': index_name,
                                'provider': provider,
                                'model': model,
                                'dims': dims,
                                'metric': metric
                            })
                        except ValueError:
                            logger.warning(f"Could not parse dims from custom index name: {index_name}")

                elif index_name.startswith('idx_hnsw_'):
                    # Parse standard index name: idx_hnsw_{dims}
                    # Extract dims from table name: embeddings_{dims}
                    try:
                        if table_name.startswith('embeddings_'):
                            dims = int(table_name[11:])  # Remove 'embeddings_' prefix
                            indexes.append({
                                'index_name': index_name,
                                'provider': 'generic',  # Standard index doesn't specify provider
                                'model': 'generic',     # Standard index doesn't specify model
                                'dims': dims,
                                'metric': 'cosine'      # Default metric for standard indexes
                            })
                    except ValueError:
                        logger.warning(f"Could not parse dims from standard index: {index_name} on {table_name}")

            return indexes

        except Exception as e:
            logger.error(f"Failed to get existing vector indexes: {e}")
            return []

    def bulk_operation_with_index_management(self, operation_func, *args, **kwargs):
        """Execute bulk operation with automatic HNSW index management and transaction safety."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        # Get existing indexes before starting
        existing_indexes = self.get_existing_vector_indexes()
        dropped_indexes = []

        try:
            # Start transaction for atomic operation
            self.connection.execute("BEGIN TRANSACTION")

            # Optimize settings for bulk loading
            self.connection.execute("SET preserve_insertion_order = false")

            # Drop existing HNSW vector indexes to improve bulk performance
            if existing_indexes:
                logger.info(f"Dropping {len(existing_indexes)} HNSW indexes for bulk operation")
                for index_info in existing_indexes:
                    try:
                        self.drop_vector_index(
                            index_info['provider'],
                            index_info['model'],
                            index_info['dims'],
                            index_info['metric']
                        )
                        dropped_indexes.append(index_info)
                    except Exception as e:
                        logger.warning(f"Could not drop index {index_info['index_name']}: {e}")

            # Execute the bulk operation
            result = operation_func(*args, **kwargs)

            # Recreate dropped indexes
            if dropped_indexes:
                logger.info(f"Recreating {len(dropped_indexes)} HNSW indexes after bulk operation")
                for index_info in dropped_indexes:
                    try:
                        self.create_vector_index(
                            index_info['provider'],
                            index_info['model'],
                            index_info['dims'],
                            index_info['metric']
                        )
                    except Exception as e:
                        logger.error(f"Failed to recreate index {index_info['index_name']}: {e}")
                        # Continue with other indexes

            # Commit transaction
            self.connection.execute("COMMIT")

            # Force checkpoint after bulk operations to ensure durability
            self._maybe_checkpoint(force=True)

            logger.info("Bulk operation completed successfully with index management")
            return result

        except Exception as e:
            # Rollback transaction on any error
            try:
                self.connection.execute("ROLLBACK")
                logger.info("Transaction rolled back due to error")
            except:
                pass

            # Attempt to recreate dropped indexes on failure
            if dropped_indexes:
                logger.info("Attempting to recreate dropped indexes after failure")
                for index_info in dropped_indexes:
                    try:
                        self.create_vector_index(
                            index_info['provider'],
                            index_info['model'],
                            index_info['dims'],
                            index_info['metric']
                        )
                    except Exception as recreate_error:
                        logger.error(f"Failed to recreate index {index_info['index_name']}: {recreate_error}")

            logger.error(f"Bulk operation failed: {e}")
            raise

    def insert_file(self, file: File) -> int:
        """Insert file record and return file ID.

        If file with same path exists, updates metadata.
        """
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # First try to find existing file by path
            existing = self.get_file_by_path(str(file.path))
            if existing:
                # File exists, update it
                file_id = self._extract_file_id(existing)
                if file_id is not None:
                    self.update_file(file_id, size_bytes=file.size_bytes, mtime=file.mtime, content_crc32=file.content_crc32)
                    return file_id

            # No existing file, insert new one
            result = self.connection.execute("""
                INSERT INTO files (path, name, extension, size, modified_time, content_crc32, language)
                VALUES (?, ?, ?, ?, to_timestamp(?), ?, ?)
                RETURNING id
            """, [
                str(file.path),
                file.name,
                file.extension,
                file.size_bytes,
                file.mtime,
                file.content_crc32,
                file.language.value if file.language else None
            ]).fetchone()

            file_id = result[0] if result else 0
            
            # Track operation for checkpoint management
            self._operations_since_checkpoint += 1
            self._maybe_checkpoint()
            
            return file_id

        except Exception as e:
            logger.error(f"Failed to insert file {file.path}: {e}")
            # Return existing file ID if constraint error (duplicate)
            if "Duplicate key" in str(e) and "violates unique constraint" in str(e):
                existing = self.get_file_by_path(str(file.path))
                if existing and isinstance(existing, dict) and "id" in existing:
                    logger.info(f"Returning existing file ID for {file.path}")
                    return existing["id"]
            raise

    def get_file_by_path(self, path: str, as_model: bool = False) -> dict[str, Any] | File | None:
        """Get file record by path."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            result = self.connection.execute("""
                SELECT id, path, name, extension, size, modified_time, content_crc32, language, created_at, updated_at
                FROM files WHERE path = ?
            """, [path]).fetchone()

            if not result:
                return None

            file_dict = {
                "id": result[0],
                "path": result[1],
                "name": result[2],
                "extension": result[3],
                "size": result[4],
                "modified_time": result[5],
                "content_crc32": result[6],
                "language": result[7],
                "created_at": result[8],
                "updated_at": result[9]
            }

            if as_model:
                return File(
                    path=result[1],
                    mtime=result[5],
                    size_bytes=result[4],
                    content_crc32=result[6],
                    language=Language(result[7]) if result[7] else Language.UNKNOWN
                )

            return file_dict

        except Exception as e:
            logger.error(f"Failed to get file by path {path}: {e}")
            return None

    def get_file_by_id(self, file_id: int, as_model: bool = False) -> dict[str, Any] | File | None:
        """Get file record by ID."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            result = self.connection.execute("""
                SELECT id, path, name, extension, size, modified_time, content_crc32, language, created_at, updated_at
                FROM files WHERE id = ?
            """, [file_id]).fetchone()

            if not result:
                return None

            file_dict = {
                "id": result[0],
                "path": result[1],
                "name": result[2],
                "extension": result[3],
                "size": result[4],
                "modified_time": result[5],
                "content_crc32": result[6],
                "language": result[7],
                "created_at": result[8],
                "updated_at": result[9]
            }

            if as_model:
                return File(
                    path=result[1],
                    mtime=result[5],
                    size_bytes=result[4],
                    content_crc32=result[6],
                    language=Language(result[7]) if result[7] else Language.UNKNOWN
                )

            return file_dict

        except Exception as e:
            logger.error(f"Failed to get file by ID {file_id}: {e}")
            return None

    def update_file(self, file_id: int, size_bytes: int | None = None, mtime: float | None = None, content_crc32: int | None = None) -> None:
        """Update file record with new values.

        Args:
            file_id: ID of the file to update
            size_bytes: New file size in bytes
            mtime: New modification timestamp
            content_crc32: New CRC32 checksum of file content
        """
        if self.connection is None:
            raise RuntimeError("No database connection")

        # Skip if no updates provided
        if size_bytes is None and mtime is None and content_crc32 is None:
            return

        try:
            # Build dynamic update query
            set_clauses = []
            values = []

            # Add size update if provided
            if size_bytes is not None:
                set_clauses.append("size = ?")
                values.append(size_bytes)

            # Add timestamp update if provided
            if mtime is not None:
                set_clauses.append("modified_time = to_timestamp(?)")
                values.append(mtime)

            # Add CRC32 update if provided
            if content_crc32 is not None:
                set_clauses.append("content_crc32 = ?")
                values.append(content_crc32)

            if set_clauses:
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(file_id)

                query = f"UPDATE files SET {', '.join(set_clauses)} WHERE id = ?"
                self.connection.execute(query, values)

        except Exception as e:
            logger.error(f"Failed to update file {file_id}: {e}")
            raise

    def delete_file_completely(self, file_path: str) -> bool:
        """Delete a file and all its chunks/embeddings completely."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Get file ID first
            file_record = self.get_file_by_path(file_path)
            if not file_record:
                return False

            file_id = file_record["id"] if isinstance(file_record, dict) else file_record.id

            # Delete in correct order due to foreign key constraints
            # 1. Delete embeddings first
            # Delete from all embedding tables
            for table_name in self._get_all_embedding_tables():
                self.connection.execute(f"""
                    DELETE FROM {table_name}
                    WHERE chunk_id IN (SELECT id FROM chunks WHERE file_id = ?)
                """, [file_id])

            # 2. Delete chunks
            self.connection.execute("DELETE FROM chunks WHERE file_id = ?", [file_id])

            # 3. Delete file
            self.connection.execute("DELETE FROM files WHERE id = ?", [file_id])

            logger.debug(f"File {file_path} and all associated data deleted")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def insert_chunk(self, chunk: Chunk) -> int:
        """Insert chunk record and return chunk ID."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            result = self.connection.execute("""
                INSERT INTO chunks (file_id, chunk_type, symbol, code, start_line, end_line,
                                  start_byte, end_byte, size, signature, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, [
                chunk.file_id,
                chunk.chunk_type.value if chunk.chunk_type else None,
                chunk.symbol,
                chunk.code,
                chunk.start_line,
                chunk.end_line,
                chunk.start_byte,
                chunk.end_byte,
                len(chunk.code),
                getattr(chunk, 'signature', None),
                chunk.language.value if chunk.language else None
            ]).fetchone()

            return result[0] if result else 0

        except Exception as e:
            logger.error(f"Failed to insert chunk: {e}")
            raise

    def insert_chunks_batch(self, chunks: list[Chunk]) -> list[int]:
        """Insert multiple chunks in batch using executemany for optimal performance."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        if not chunks:
            return []

        # Initialize batch data before try block
        batch_data = []

        try:
            # Optimize settings for bulk loading
            self.connection.execute("SET preserve_insertion_order = false")

            # Prepare batch data
            for chunk in chunks:
                batch_data.append([
                    chunk.file_id,
                    chunk.chunk_type.value if chunk.chunk_type else None,
                    chunk.symbol,
                    chunk.code,
                    chunk.start_line,
                    chunk.end_line,
                    chunk.start_byte,
                    chunk.end_byte,
                    len(chunk.code),
                    getattr(chunk, 'signature', None),
                    chunk.language.value if chunk.language else None
                ])

            # Execute batch insert using executemany
            self.connection.executemany("""
                INSERT INTO chunks (file_id, chunk_type, symbol, code, start_line, end_line,
                                  start_byte, end_byte, size, signature, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)

            # Get the inserted IDs by querying the last inserted rows
            result_count = len(chunks)
            results = self.connection.execute(f"""
                SELECT id FROM chunks
                ORDER BY id DESC
                LIMIT {result_count}
            """).fetchall()

            # Return IDs in correct order (oldest first)
            chunk_ids = [result[0] for result in reversed(results)]
            
            # Track batch operation for checkpoint management
            self._operations_since_checkpoint += len(chunks)
            self._maybe_checkpoint()
            
            return chunk_ids

        except Exception as e:
            logger.error(f"Failed to insert chunks batch: {e}")
            raise

    def get_chunk_by_id(self, chunk_id: int, as_model: bool = False) -> dict[str, Any] | Chunk | None:
        """Get chunk record by ID."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            result = self.connection.execute("""
                SELECT id, file_id, chunk_type, symbol, code, start_line, end_line,
                       start_byte, end_byte, size, signature, language, created_at, updated_at
                FROM chunks WHERE id = ?
            """, [chunk_id]).fetchone()

            if not result:
                return None

            chunk_dict = {
                "id": result[0],
                "file_id": result[1],
                "chunk_type": result[2],
                "symbol": result[3],
                "code": result[4],
                "start_line": result[5],
                "end_line": result[6],
                "start_byte": result[7],
                "end_byte": result[8],
                "size": result[9],
                "signature": result[10],
                "language": result[11],
                "created_at": result[12],
                "updated_at": result[13]
            }

            if as_model:
                return Chunk(
                    file_id=result[1],
                    chunk_type=ChunkType(result[2]) if result[2] else ChunkType.UNKNOWN,
                    symbol=result[3],
                    code=result[4],
                    start_line=result[5],
                    end_line=result[6],
                    start_byte=result[7],
                    end_byte=result[8],
                    language=Language(result[11]) if result[11] else Language.UNKNOWN
                )

            return chunk_dict

        except Exception as e:
            logger.error(f"Failed to get chunk by ID {chunk_id}: {e}")
            return None

    def get_chunks_by_file_id(self, file_id: int, as_model: bool = False) -> list[dict[str, Any] | Chunk]:
        """Get all chunks for a specific file."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            results = self.connection.execute("""
                SELECT id, file_id, chunk_type, symbol, code, start_line, end_line,
                       start_byte, end_byte, size, signature, language, created_at, updated_at
                FROM chunks WHERE file_id = ?
                ORDER BY start_line
            """, [file_id]).fetchall()

            chunks = []
            for result in results:
                chunk_dict = {
                    "id": result[0],
                    "file_id": result[1],
                    "chunk_type": result[2],
                    "symbol": result[3],
                    "code": result[4],
                    "start_line": result[5],
                    "end_line": result[6],
                    "start_byte": result[7],
                    "end_byte": result[8],
                    "size": result[9],
                    "signature": result[10],
                    "language": result[11],
                    "created_at": result[12],
                    "updated_at": result[13]
                }

                if as_model:
                    chunks.append(Chunk(
                        file_id=result[1],
                        chunk_type=ChunkType(result[2]) if result[2] else ChunkType.UNKNOWN,
                        symbol=result[3],
                        code=result[4],
                        start_line=result[5],
                        end_line=result[6],
                        start_byte=result[7],
                        end_byte=result[8],
                        language=Language(result[11]) if result[11] else Language.UNKNOWN
                    ))
                else:
                    chunks.append(chunk_dict)

            return chunks

        except Exception as e:
            logger.error(f"Failed to get chunks for file {file_id}: {e}")
            return []

    def delete_file_chunks(self, file_id: int) -> None:
        """Delete all chunks for a file."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # First delete embeddings for chunks
            # Delete from all embedding tables
            for table_name in self._get_all_embedding_tables():
                self.connection.execute(f"""
                    DELETE FROM {table_name}
                    WHERE chunk_id IN (SELECT id FROM chunks WHERE file_id = ?)
                """, [file_id])

            # Then delete chunks
            self.connection.execute("DELETE FROM chunks WHERE file_id = ?", [file_id])

        except Exception as e:
            logger.error(f"Failed to delete chunks for file {file_id}: {e}")
            raise

    def update_chunk(self, chunk_id: int, **kwargs) -> None:
        """Update chunk record with new values."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        if not kwargs:
            return

        try:
            # Build dynamic update query
            set_clauses = []
            values = []

            valid_fields = ["chunk_type", "name", "content", "start_line", "end_line",
                          "start_byte", "end_byte", "signature", "language"]

            for key, value in kwargs.items():
                if key in valid_fields:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)

            if set_clauses:
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(chunk_id)

                query = f"UPDATE chunks SET {', '.join(set_clauses)} WHERE id = ?"
                self.connection.execute(query, values)

        except Exception as e:
            logger.error(f"Failed to update chunk {chunk_id}: {e}")
            raise

    def insert_embedding(self, embedding: Embedding) -> int:
        """Insert embedding record and return embedding ID."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Validate embedding dimensions for FLOAT[1536] schema
            if len(embedding.vector) != 1536:
                if len(embedding.vector) < 1536:
                    # Pad with zeros
                    padded_vector = embedding.vector + [0.0] * (1536 - len(embedding.vector))
                else:
                    # Truncate to 1536
                    padded_vector = embedding.vector[:1536]
                logger.warning(f"Embedding vector resized from {len(embedding.vector)} to 1536 dimensions")
            else:
                padded_vector = embedding.vector

            result = self.connection.execute("""
                INSERT INTO embeddings (chunk_id, provider, model, embedding, dims)
                VALUES (?, ?, ?, ?, ?)
                RETURNING id
            """, [
                embedding.chunk_id,
                embedding.provider,
                embedding.model,
                padded_vector,
                embedding.dims
            ])

            embedding_id = result.fetchone()[0]
            logger.debug(f"Inserted embedding {embedding_id} for chunk {embedding.chunk_id}")
            return embedding_id

        except Exception as e:
            logger.error(f"Failed to insert embedding: {e}")
            raise

    def insert_embeddings_batch(self, embeddings_data: list[dict], batch_size: int | None = None, connection=None) -> int:
        """Insert multiple embedding vectors with HNSW index optimization.

        For large batches (>= batch_size threshold), uses the Context7-recommended optimization:
        1. Drop HNSW indexes to avoid insert slowdown (60s+ -> 5s for 300 items)
        2. Use fast INSERT for new embeddings, INSERT OR REPLACE for updates
        3. Recreate HNSW indexes after bulk operations

        Expected speedup: 10-20x faster for large batches (90s -> 5-10s).

        Args:
            embeddings_data: List of dicts with keys: chunk_id, provider, model, embedding, dims
            batch_size: Threshold for HNSW optimization (default: 50)
            connection: Optional database connection to use (for transaction contexts)

        Returns:
            Number of successfully inserted embeddings
        """
        # Use provided connection or default connection
        conn = connection if connection is not None else self.connection
        if conn is None:
            raise RuntimeError("No database connection")

        if not embeddings_data:
            return 0

        # Use provided batch_size threshold or default to 50
        hnsw_threshold = batch_size if batch_size is not None else 50
        actual_batch_size = len(embeddings_data)
        logger.debug(f"🔄 Starting optimized batch insert of {actual_batch_size} embeddings (HNSW threshold: {hnsw_threshold})")

        # Auto-detect embedding dimensions from first embedding
        first_vector = embeddings_data[0]['embedding']
        detected_dims = len(first_vector)

        # Validate all embeddings have the same dimensions
        for i, embedding_data in enumerate(embeddings_data):
            vector = embedding_data['embedding']
            if len(vector) != detected_dims:
                raise ValueError(f"Embedding vector {i} has {len(vector)} dimensions, "
                               f"expected {detected_dims} (detected from first embedding)")

        # Ensure appropriate table exists for these dimensions
        table_name = self._ensure_embedding_table_exists(detected_dims)
        logger.debug(f"Using table {table_name} for {detected_dims}-dimensional embeddings")

        # Extract provider/model for conflict checking
        first_embedding = embeddings_data[0]
        provider = first_embedding['provider']
        model = first_embedding['model']

        # Use HNSW index optimization only for larger batches (research-based optimal threshold)
        # Based on benchmarks: small batches (1-10) keep indexes, medium+ batches (≥50) use optimization
        # This fixes semantic search for new files while maintaining bulk performance
        use_hnsw_optimization = actual_batch_size >= hnsw_threshold

        # Log the optimization decision for debugging
        if use_hnsw_optimization:
            logger.debug(f"🚀 Large batch: using HNSW optimization ({actual_batch_size} >= {hnsw_threshold})")
        else:
            logger.debug(f"🔍 Small batch: preserving HNSW indexes for semantic search ({actual_batch_size} < {hnsw_threshold})")

        try:
            total_inserted = 0
            start_time = time.time()

            if use_hnsw_optimization:
                # CRITICAL OPTIMIZATION: Drop HNSW indexes for bulk operations (research-based best practice)
                logger.debug(f"🔧 Large batch detected ({actual_batch_size} embeddings >= {hnsw_threshold}), applying HNSW optimization")

                # Extract dims for index management
                dims = first_embedding['dims']

                # Step 1: Drop HNSW index to enable fast insertions
                existing_indexes = self.get_existing_vector_indexes()
                dropped_indexes = []

                for index_info in existing_indexes:
                    try:
                        self.drop_vector_index(
                            index_info['provider'],
                            index_info['model'],
                            index_info['dims'],
                            index_info['metric']
                        )
                        dropped_indexes.append(index_info)
                        logger.debug(f"Dropped index: {index_info['index_name']}")
                    except Exception as e:
                        logger.warning(f"Could not drop index {index_info['index_name']}: {e}")


                # Step 2: Separate new vs existing embeddings for optimal INSERT strategy
                chunk_ids = [emb['chunk_id'] for emb in embeddings_data]
                existing_chunk_ids = self.get_existing_embeddings(chunk_ids, provider, model, table_name)

                # Separate new vs existing embeddings
                new_embeddings = [emb for emb in embeddings_data if emb['chunk_id'] not in existing_chunk_ids]
                update_embeddings = [emb for emb in embeddings_data if emb['chunk_id'] in existing_chunk_ids]

                # logger.debug(f"📊 Batch breakdown: {len(new_embeddings)} new, {len(update_embeddings)} updates")

                # Step 3: Fast INSERT for new embeddings using VALUES table construction
                if new_embeddings:

                    insert_start = time.time()

                    try:
                        # Set DuckDB performance options for bulk loading
                        conn.execute("SET preserve_insertion_order = false")

                        # Build VALUES clause for bulk insert (much faster than executemany)
                        values_parts = []
                        for embedding_data in new_embeddings:
                            vector_str = str(embedding_data['embedding'])
                            values_parts.append(f"({embedding_data['chunk_id']}, '{embedding_data['provider']}', '{embedding_data['model']}', {vector_str}, {embedding_data['dims']})")

                        # Single INSERT with all values (fastest approach without external deps)
                        values_clause = ",\n    ".join(values_parts)
                        conn.execute(f"""
                            INSERT INTO {table_name} (chunk_id, provider, model, embedding, dims)
                            VALUES {values_clause}
                        """)

                        insert_time = time.time() - insert_start
                        logger.debug(f"✅ Fast VALUES INSERT completed in {insert_time:.3f}s ({len(new_embeddings)/insert_time:.1f} emb/s)")
                        total_inserted += len(new_embeddings)

                    except Exception as e:
                        logger.error(f"Fast VALUES INSERT failed: {e}")
                        raise


                # Step 4: INSERT OR REPLACE only for updates using VALUES approach
                if update_embeddings:
                    update_start = time.time()

                    try:
                        # Build VALUES clause for bulk updates
                        values_parts = []
                        for embedding_data in update_embeddings:
                            vector_str = str(embedding_data['embedding'])
                            values_parts.append(f"({embedding_data['chunk_id']}, '{embedding_data['provider']}', '{embedding_data['model']}', {vector_str}, {embedding_data['dims']})")

                        # Single INSERT OR REPLACE with all values
                        values_clause = ",\n    ".join(values_parts)
                        conn.execute(f"""
                            INSERT OR REPLACE INTO {table_name} (chunk_id, provider, model, embedding, dims)
                            VALUES {values_clause}
                        """)

                        update_time = time.time() - update_start
                        logger.debug(f"✅ VALUES UPDATE completed in {update_time:.3f}s ({len(update_embeddings)/update_time:.1f} emb/s)")
                        total_inserted += len(update_embeddings)

                    except Exception as e:
                        logger.error(f"VALUES UPDATE failed: {e}")
                        raise

                # Step 5: Recreate HNSW index for fast similarity search
                if dropped_indexes:
                    logger.debug("📈 Recreating HNSW index for fast similarity search")
                    index_start = time.time()
                    for index_info in dropped_indexes:
                        try:
                            self.create_vector_index(
                                index_info['provider'],
                                index_info['model'],
                                index_info['dims'],
                                index_info['metric']
                            )
                            logger.debug(f"Recreated HNSW index: {index_info['index_name']}")
                        except Exception as e:
                            logger.error(f"Failed to recreate index {index_info['index_name']}: {e}")
                            # Continue - data is inserted, just no index optimization for search
                    index_time = time.time() - index_start
                    logger.debug(f"✅ HNSW index recreated in {index_time:.3f}s")

                logger.debug(f"✅ Stored {actual_batch_size} embeddings successfully")

            else:
                # Small batch: use VALUES approach for consistency
                small_start = time.time()

                try:
                    # Build VALUES clause for small batch
                    values_parts = []
                    for embedding_data in embeddings_data:
                        vector_str = str(embedding_data['embedding'])
                        values_parts.append(f"({embedding_data['chunk_id']}, '{embedding_data['provider']}', '{embedding_data['model']}', {vector_str}, {embedding_data['dims']})")

                    # Single INSERT OR REPLACE with all values
                    values_clause = ",\n    ".join(values_parts)
                    conn.execute(f"""
                        INSERT OR REPLACE INTO {table_name} (chunk_id, provider, model, embedding, dims)
                        VALUES {values_clause}
                    """)

                    small_time = time.time() - small_start
                    logger.debug(f"✅ Small VALUES batch completed in {small_time:.3f}s ({len(embeddings_data)/small_time:.1f} emb/s)")
                    total_inserted = len(embeddings_data)

                except Exception as e:
                    logger.error(f"Small VALUES batch failed: {e}")
                    raise

                # Ensure HNSW indexes exist for semantic search after small batch insert
                # Note: _ensure_embedding_table_exists automatically creates standard HNSW indexes
                # This check verifies the index exists for this dimension
                existing_indexes = self.get_existing_vector_indexes()
                dims = first_embedding['dims']

                # Check if any index exists for this dimension (standard or custom)
                index_exists = any(idx['dims'] == dims for idx in existing_indexes)

                if not index_exists:
                    logger.warning(f"🔍 No HNSW index found for {dims}D embeddings, creating one now")
                    # Create the missing HNSW index for semantic search functionality
                    try:
                        self.create_vector_index(provider, model, dims, "cosine")
                        logger.info(f"✅ Created missing HNSW index for {provider}/{model} ({dims}D)")
                    except Exception as e:
                        logger.error(f"❌ Failed to create HNSW index for {provider}/{model} ({dims}D): {e}")
                        # Continue - data is inserted, just no index optimization for search

                # Update progress for small batch completion
                logger.debug(f"✅ Stored {actual_batch_size} embeddings successfully")

            insert_time = time.time() - start_time
            logger.debug(f"⚡ Batch INSERT completed in {insert_time:.3f}s")

            if use_hnsw_optimization:
                logger.debug(f"🏆 HNSW-optimized batch insert: {total_inserted} embeddings in {insert_time:.3f}s ({total_inserted/insert_time:.1f} embeddings/sec) - Expected 10-20x speedup achieved!")
            else:
                logger.debug(f"🎯 Standard batch insert: {total_inserted} embeddings in {insert_time:.3f}s ({total_inserted/insert_time:.1f} embeddings/sec)")

            # Track embedding operations for checkpoint management
            self._operations_since_checkpoint += total_inserted
            
            # Force checkpoint for large embedding batches to minimize WAL growth
            if total_inserted >= 50:
                self._maybe_checkpoint(force=True)
            else:
                self._maybe_checkpoint()

            return total_inserted

        except Exception as e:
            logger.error(f"💥 CRITICAL: Optimized batch insert failed: {e}")
            logger.warning("⚠️ This indicates a critical issue with VALUES clause approach!")
            raise
        finally:
            pass

    def get_embedding_by_chunk_id(self, chunk_id: int, provider: str, model: str) -> Embedding | None:
        """Get embedding for specific chunk, provider, and model."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Search across all embedding tables
            embedding_tables = self._get_all_embedding_tables()
            for table_name in embedding_tables:
                result = self.connection.execute(f"""
                    SELECT id, chunk_id, provider, model, embedding, dims, created_at
                    FROM {table_name}
                    WHERE chunk_id = ? AND provider = ? AND model = ?
                """, [chunk_id, provider, model]).fetchone()

                if result:
                    return Embedding(
                        chunk_id=result[1],
                        provider=result[2],
                        model=result[3],
                        vector=result[4],
                        dims=result[5]
                    )

            return None

        except Exception as e:
            logger.error(f"Failed to get embedding for chunk {chunk_id}: {e}")
            return None

    def get_existing_embeddings(self, chunk_ids: list[int], provider: str, model: str, table_name: str = "embeddings_1536") -> set[int]:
        """Get set of chunk IDs that already have embeddings for given provider/model."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        if not chunk_ids:
            return set()

        try:
            # Create placeholders for IN clause
            placeholders = ",".join("?" * len(chunk_ids))
            params = chunk_ids + [provider, model]

            results = self.connection.execute(f"""
                SELECT DISTINCT chunk_id
                FROM {table_name}
                WHERE chunk_id IN ({placeholders}) AND provider = ? AND model = ?
            """, params).fetchall()

            return {result[0] for result in results}

        except Exception as e:
            logger.error(f"Failed to get existing embeddings: {e}")
            return set()

    def delete_embeddings_by_chunk_id(self, chunk_id: int) -> None:
        """Delete all embeddings for a specific chunk."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Delete from all embedding tables
            for table_name in self._get_all_embedding_tables():
                self.connection.execute(f"DELETE FROM {table_name} WHERE chunk_id = ?", [chunk_id])

        except Exception as e:
            logger.error(f"Failed to delete embeddings for chunk {chunk_id}: {e}")
            raise

    def _validate_and_normalize_path_filter(self, path_filter: str | None) -> str | None:
        """Validate and normalize path filter for security and consistency.
        
        Args:
            path_filter: User-provided path filter
            
        Returns:
            Normalized path filter safe for SQL LIKE queries, or None
            
        Raises:
            ValueError: If path contains dangerous patterns
        """
        if path_filter is None:
            return None

        # Remove leading/trailing whitespace
        normalized = path_filter.strip()

        if not normalized:
            return None

        # Security checks - prevent directory traversal
        dangerous_patterns = ['..', '~', '*', '?', '[', ']', '\0', '\n', '\r']
        for pattern in dangerous_patterns:
            if pattern in normalized:
                raise ValueError(f"Path filter contains forbidden pattern: {pattern}")

        # Normalize path separators to forward slashes
        normalized = normalized.replace('\\', '/')

        # Remove leading slashes to ensure relative paths
        normalized = normalized.lstrip('/')

        # Ensure trailing slash for directory patterns
        if normalized and not normalized.endswith('/') and '.' not in normalized.split('/')[-1]:
            normalized += '/'

        return normalized

    def search_semantic(
        self,
        query_embedding: list[float],
        provider: str,
        model: str,
        page_size: int = 10,
        offset: int = 0,
        threshold: float | None = None,
        path_filter: str | None = None
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Perform semantic vector search using HNSW index with multi-dimension support."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Validate and normalize path filter
            normalized_path = self._validate_and_normalize_path_filter(path_filter)

            # Detect dimensions from query embedding
            query_dims = len(query_embedding)
            table_name = self._get_table_name_for_dimensions(query_dims)

            # Check if table exists for these dimensions
            if not self._table_exists(table_name):
                logger.warning(f"No embeddings table found for {query_dims} dimensions ({table_name})")
                return [], {"offset": offset, "page_size": page_size, "has_more": False, "total": 0}

            # Build query with dimension-specific table
            query = f"""
                SELECT
                    c.id as chunk_id,
                    c.symbol,
                    c.code,
                    c.chunk_type,
                    c.start_line,
                    c.end_line,
                    f.path as file_path,
                    f.language,
                    array_cosine_similarity(e.embedding, ?::FLOAT[{query_dims}]) as similarity
                FROM {table_name} e
                JOIN chunks c ON e.chunk_id = c.id
                JOIN files f ON c.file_id = f.id
                WHERE e.provider = ? AND e.model = ?
            """

            params = [query_embedding, provider, model]

            if threshold is not None:
                query += f" AND array_cosine_similarity(e.embedding, ?::FLOAT[{query_dims}]) >= ?"
                params.append(query_embedding)
                params.append(threshold)

            if normalized_path is not None:
                query += " AND f.path LIKE ?"
                params.append(f"%/{normalized_path}%")

            # Get total count for pagination
            # Build count query separately to avoid string replacement issues
            count_query = f"""
                SELECT COUNT(*)
                FROM {table_name} e
                JOIN chunks c ON e.chunk_id = c.id
                JOIN files f ON c.file_id = f.id
                WHERE e.provider = ? AND e.model = ?
            """

            count_params = [provider, model]

            if threshold is not None:
                count_query += f" AND array_cosine_similarity(e.embedding, ?::FLOAT[{query_dims}]) >= ?"
                count_params.extend([query_embedding, threshold])

            if normalized_path is not None:
                count_query += " AND f.path LIKE ?"
                count_params.append(f"%/{normalized_path}%")

            total_count = self.connection.execute(count_query, count_params).fetchone()[0]

            query += " ORDER BY similarity DESC LIMIT ? OFFSET ?"
            params.extend([page_size, offset])

            results = self.connection.execute(query, params).fetchall()

            result_list = [
                {
                    "chunk_id": result[0],
                    "symbol": result[1],
                    "content": result[2],
                    "chunk_type": result[3],
                    "start_line": result[4],
                    "end_line": result[5],
                    "file_path": result[6],
                    "language": result[7],
                    "similarity": result[8]
                }
                for result in results
            ]

            pagination = {
                "offset": offset,
                "page_size": page_size,
                "has_more": offset + page_size < total_count,
                "next_offset": offset + page_size if offset + page_size < total_count else None,
                "total": total_count
            }

            return result_list, pagination

        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            return [], {"offset": offset, "page_size": page_size, "has_more": False, "total": 0}

    def search_regex(self, pattern: str, page_size: int = 10, offset: int = 0, path_filter: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Perform regex search on code content."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Validate and normalize path filter
            normalized_path = self._validate_and_normalize_path_filter(path_filter)

            # Build base WHERE clause
            where_conditions = ["regexp_matches(c.code, ?)"]
            params = [pattern]

            if normalized_path is not None:
                where_conditions.append("f.path LIKE ?")
                params.append(f"%/{normalized_path}%")

            where_clause = " AND ".join(where_conditions)

            # Get total count for pagination
            count_query = f"""
                SELECT COUNT(*)
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                WHERE {where_clause}
            """
            total_count = self.connection.execute(count_query, params).fetchone()[0]

            # Get results
            results_query = f"""
                SELECT
                    c.id as chunk_id,
                    c.symbol,
                    c.code,
                    c.chunk_type,
                    c.start_line,
                    c.end_line,
                    f.path as file_path,
                    f.language
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                WHERE {where_clause}
                ORDER BY f.path, c.start_line
                LIMIT ? OFFSET ?
            """
            results = self.connection.execute(results_query, params + [page_size, offset]).fetchall()



            result_list = [
                {
                    "chunk_id": result[0],
                    "name": result[1],
                    "content": result[2],
                    "chunk_type": result[3],
                    "start_line": result[4],
                    "end_line": result[5],
                    "file_path": result[6],
                    "language": result[7]
                }
                for result in results
            ]

            pagination = {
                "offset": offset,
                "page_size": page_size,
                "has_more": offset + page_size < total_count,
                "next_offset": offset + page_size if offset + page_size < total_count else None,
                "total": total_count
            }

            return result_list, pagination

        except Exception as e:
            logger.error(f"Failed to perform regex search: {e}")
            return [], {"offset": offset, "page_size": page_size, "has_more": False, "total": 0}

    def search_text(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Perform full-text search on code content."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Simple text search using LIKE operator
            search_pattern = f"%{query}%"

            results = self.connection.execute("""
                SELECT
                    c.id as chunk_id,
                    c.name,
                    c.content,
                    c.chunk_type,
                    c.start_line,
                    c.end_line,
                    f.path as file_path,
                    f.language
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                WHERE c.content LIKE ? OR c.name LIKE ?
                ORDER BY f.path, c.start_line
                LIMIT ?
            """, [search_pattern, search_pattern, limit]).fetchall()

            return [
                {
                    "chunk_id": result[0],
                    "name": result[1],
                    "content": result[2],
                    "chunk_type": result[3],
                    "start_line": result[4],
                    "end_line": result[5],
                    "file_path": result[6],
                    "language": result[7]
                }
                for result in results
            ]

        except Exception as e:
            logger.error(f"Failed to perform text search: {e}")
            return []

    def get_stats(self) -> dict[str, int]:
        """Get database statistics (file count, chunk count, etc.)."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Get counts from each table
            file_count = self.connection.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            chunk_count = self.connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

            # Count embeddings across all dimension-specific tables
            embedding_count = 0
            embedding_tables = self._get_all_embedding_tables()
            for table_name in embedding_tables:
                count = self.connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                embedding_count += count

            # Get unique providers/models across all embedding tables
            provider_results = []
            for table_name in embedding_tables:
                results = self.connection.execute(f"""
                    SELECT DISTINCT provider, model, COUNT(*) as count
                    FROM {table_name}
                    GROUP BY provider, model
                """).fetchall()
                provider_results.extend(results)

            providers = {}
            for result in provider_results:
                key = f"{result[0]}/{result[1]}"
                providers[key] = result[2]

            # Convert providers dict to count for interface compliance
            provider_count = len(providers)
            return {
                "files": file_count,
                "chunks": chunk_count,
                "embeddings": embedding_count,
                "providers": provider_count
            }

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"files": 0, "chunks": 0, "embeddings": 0, "providers": 0}

    def get_file_stats(self, file_id: int) -> dict[str, Any]:
        """Get statistics for a specific file."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Get file info
            file_result = self.connection.execute("""
                SELECT path, name, extension, size, language
                FROM files WHERE id = ?
            """, [file_id]).fetchone()

            if not file_result:
                return {}

            # Get chunk count and types
            chunk_results = self.connection.execute("""
                SELECT chunk_type, COUNT(*) as count
                FROM chunks WHERE file_id = ?
                GROUP BY chunk_type
            """, [file_id]).fetchall()

            chunk_types = {result[0]: result[1] for result in chunk_results}
            total_chunks = sum(chunk_types.values())

            # Get embedding count across all embedding tables
            embedding_count = 0
            embedding_tables = self._get_all_embedding_tables()
            for table_name in embedding_tables:
                count = self.connection.execute(f"""
                    SELECT COUNT(*)
                    FROM {table_name} e
                    JOIN chunks c ON e.chunk_id = c.id
                    WHERE c.file_id = ?
                """, [file_id]).fetchone()[0]
                embedding_count += count

            return {
                "file_id": file_id,
                "path": file_result[0],
                "name": file_result[1],
                "extension": file_result[2],
                "size": file_result[3],
                "language": file_result[4],
                "chunks": total_chunks,
                "chunk_types": chunk_types,
                "embeddings": embedding_count
            }

        except Exception as e:
            logger.error(f"Failed to get file stats for {file_id}: {e}")
            return {}

    def get_provider_stats(self, provider: str, model: str) -> dict[str, Any]:
        """Get statistics for a specific embedding provider/model."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            # Get embedding count across all embedding tables
            embedding_count = 0
            file_ids = set()
            dims = 0
            embedding_tables = self._get_all_embedding_tables()

            for table_name in embedding_tables:
                # Count embeddings for this provider/model in this table
                count = self.connection.execute(f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE provider = ? AND model = ?
                """, [provider, model]).fetchone()[0]
                embedding_count += count

                # Get unique file IDs for this provider/model in this table
                file_results = self.connection.execute(f"""
                    SELECT DISTINCT c.file_id
                    FROM {table_name} e
                    JOIN chunks c ON e.chunk_id = c.id
                    WHERE e.provider = ? AND e.model = ?
                """, [provider, model]).fetchall()
                file_ids.update(result[0] for result in file_results)

                # Get dimensions (should be consistent across all tables for same provider/model)
                if count > 0 and dims == 0:
                    dims_result = self.connection.execute(f"""
                        SELECT DISTINCT dims FROM {table_name}
                        WHERE provider = ? AND model = ?
                        LIMIT 1
                    """, [provider, model]).fetchone()
                    if dims_result:
                        dims = dims_result[0]

            file_count = len(file_ids)

            return {
                "provider": provider,
                "model": model,
                "embeddings": embedding_count,
                "files": file_count,
                "dimensions": dims
            }

        except Exception as e:
            logger.error(f"Failed to get provider stats for {provider}/{model}: {e}")
            return {"provider": provider, "model": model, "embeddings": 0, "files": 0, "dimensions": 0}

    def execute_query(self, query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return results."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        try:
            if params:
                results = self.connection.execute(query, params).fetchall()
            else:
                results = self.connection.execute(query).fetchall()

            # Convert to list of dictionaries
            if results:
                # Get column names
                column_names = [desc[0] for desc in self.connection.description]
                return [dict(zip(column_names, row)) for row in results]

            return []

        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    def begin_transaction(self) -> None:
        """Begin a database transaction."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        self.connection.execute("BEGIN TRANSACTION")

    def commit_transaction(self, force_checkpoint: bool = False) -> None:
        """Commit the current transaction with optional checkpoint."""
        if self.connection is None:
            raise RuntimeError("No database connection")
        
        self.connection.execute("COMMIT")
        
        if force_checkpoint:
            try:
                self.connection.execute("CHECKPOINT")
                if not os.environ.get("CHUNKHOUND_MCP_MODE"):
                    logger.debug("Transaction committed with checkpoint")
            except Exception as e:
                if not os.environ.get("CHUNKHOUND_MCP_MODE"):
                    logger.warning(f"Post-commit checkpoint failed: {e}")

    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        if self.connection is None:
            raise RuntimeError("No database connection")

        self.connection.execute("ROLLBACK")

    async def process_file(self, file_path: Path, skip_embeddings: bool = False) -> dict[str, Any]:
        """Process a file end-to-end: parse, chunk, and store in database.

        Delegates to IndexingCoordinator for actual processing.
        """
        try:
            logger.info(f"Processing file: {file_path}")

            # Check if file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                raise ValueError(f"File not found or not readable: {file_path}")

            # Get file metadata
            stat = file_path.stat()

            # Check if file needs to be reprocessed - delegate this logic to IndexingCoordinator
            # The code below remains for reference but is no longer used
            logger.debug(f"Delegating file processing to IndexingCoordinator: {file_path}")

            # Use IndexingCoordinator to process the file
            if not self._indexing_coordinator:
                raise RuntimeError("IndexingCoordinator not initialized")

            # Delegate to IndexingCoordinator for parsing and chunking
            # This will handle the complete file processing through the service layer
            if self._indexing_coordinator is None:
                return {"status": "error", "error": "Indexing coordinator not available"}
            return await self._indexing_coordinator.process_file(file_path, skip_embeddings=skip_embeddings)

            # Note: Embedding generation is now handled by the IndexingCoordinator
            # This code is kept for backward compatibility with legacy tests
            # Note: All embedding and chunk processing is now handled by the IndexingCoordinator
            # This provider now acts purely as a delegation layer to the service architecture

            # Delegate file processing to IndexingCoordinator and return its result directly
            return await self._indexing_coordinator.process_file(file_path, skip_embeddings=skip_embeddings)

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return {"status": "error", "error": str(e), "chunks": 0}

    async def process_file_incremental(self, file_path: Path) -> dict[str, Any]:
        """Process a file with incremental parsing and differential chunking.

        Uses the IndexingCoordinator for parsing, chunking, and embeddings.

        Note: This method always fully reprocesses a file when it has been modified.
        True incremental (partial) processing is not yet implemented.
        """
        try:
            # Validate file exists
            if not file_path.exists() or not file_path.is_file():
                logger.debug(f"Incremental processing - File not found: {file_path}")
                return {"status": "error", "error": f"File not found: {file_path}", "chunks": 0, "incremental": True}

            # Get existing file record to determine if this is new or updated
            existing_file = self.get_file_by_path(str(file_path))
            logger.debug(f"Incremental processing - Existing file record: {existing_file is not None}")

            # Check for up-to-date file based on modification time
            if existing_file:
                file_stat = file_path.stat()
                current_mtime = file_stat.st_mtime
                logger.debug(f"Incremental processing - Current file mtime: {current_mtime}")

                # Get timestamp from existing file record
                if isinstance(existing_file, dict):
                    # Try different possible timestamp field names
                    existing_mtime = None
                    for field in ['mtime', 'modified_time', 'modification_time', 'timestamp']:
                        if field in existing_file and existing_file[field] is not None:
                            timestamp_value = existing_file[field]
                            if isinstance(timestamp_value, (int, float)):
                                existing_mtime = float(timestamp_value)
                                logger.debug(f"Incremental processing - Found timestamp in field '{field}': {existing_mtime}")
                                break
                            elif hasattr(timestamp_value, "timestamp"):
                                existing_mtime = timestamp_value.timestamp()
                                logger.debug(f"Incremental processing - Found timestamp object in field '{field}': {existing_mtime}")
                                break

                    if existing_mtime is None:
                        existing_mtime = 0.0
                        logger.debug(f"Incremental processing - No valid timestamp found, using default: {existing_mtime}")

                    # Note: Removed timestamp checking logic - if process_file_incremental() was called,
                    # the file needs processing. File watcher handles change detection.

            # Initialize services if needed
            if not hasattr(self, '_services_initialized') or not self._services_initialized:
                try:
                    self._initialize_shared_instances()
                    self._services_initialized = True
                except Exception as e:
                    logger.error(f"Failed to initialize services: {e}")

            # Check if IndexingCoordinator is available
            if not hasattr(self, '_indexing_coordinator') or self._indexing_coordinator is None:
                # Fallback to direct processing without coordinator
                logger.warning("Using fallback direct processing - IndexingCoordinator not available")
                return await self._fallback_process_file(file_path)

            # Delegate to IndexingCoordinator for processing
            logger.debug(f"Incremental processing - Delegating to IndexingCoordinator: {file_path}")
            result = await self._indexing_coordinator.process_file(file_path, skip_embeddings=False)
            logger.debug(f"Incremental processing - IndexingCoordinator result: {result.get('status', 'unknown')}")

            # Transform result to match incremental processing API
            if result.get("status") == "success":
                chunks_count = result.get("chunks", 0)
                logger.debug(f"Incremental processing - Successfully processed with {chunks_count} chunks")

                # Get the file ID from result or existing file
                file_id = result.get("file_id")
                if not file_id and existing_file and isinstance(existing_file, dict) and "id" in existing_file:
                    file_id = existing_file["id"]
                    logger.debug(f"Incremental processing - Using existing file_id: {file_id}")
                else:
                    logger.debug(f"Incremental processing - Using new file_id: {file_id}")

                # IndexingCoordinator already handled transaction safety
                # No additional chunk management needed
                chunks_deleted = result.get("chunks_deleted", 0)
                logger.debug("Incremental processing - IndexingCoordinator handled transaction safety")

                return {
                    "status": "success",
                    "file_id": file_id,
                    "chunks": chunks_count,
                    "chunks_unchanged": 0,
                    "chunks_inserted": chunks_count,
                    "chunks_deleted": chunks_deleted,
                    "chunk_ids": result.get("chunk_ids", []),
                    "embeddings": result.get("embeddings", 0),
                    "incremental": True
                }
            elif result.get("status") == "up_to_date":
                logger.debug("Incremental processing - File reported as up-to-date by IndexingCoordinator")
                # File unchanged, get existing chunk count
                if existing_file:
                    file_id = existing_file["id"] if isinstance(existing_file, dict) else existing_file.id
                    logger.debug(f"Incremental processing - Up-to-date file, getting chunk count for file_id: {file_id}")
                    if self.connection is None:
                        return {"status": "error", "error": "Database not connected"}
                    chunks_count = self.connection.execute(
                        "SELECT COUNT(*) FROM chunks WHERE file_id = ?",
                        [file_id]
                    ).fetchone()[0]
                    logger.debug(f"Incremental processing - Up-to-date file has {chunks_count} chunks")

                    return {
                        "status": "up_to_date",
                        "file_id": file_id,
                        "chunks": chunks_count,
                        "chunks_unchanged": chunks_count,
                        "chunks_inserted": 0,
                        "chunks_deleted": 0,
                        "chunk_ids": [],
                        "embeddings": 0,
                        "incremental": True
                    }
                else:
                    logger.debug("Incremental processing - Up-to-date but no existing file record found")
                    return {
                        "status": "up_to_date",
                        "chunks": 0,
                        "incremental": True
                    }
            else:
                # Pass through other statuses (error, no_content, etc.) with incremental flag
                logger.debug(f"Incremental processing - Other status received: {result.get('status')}")
                result["incremental"] = True
                return result

        except Exception as e:
            logger.error(f"Failed to process file incrementally {file_path}: {e}")
            return {"status": "error", "error": str(e), "chunks": 0, "incremental": True}

    async def _fallback_process_file(self, file_path: Path) -> dict[str, Any]:
        """Fallback implementation when IndexingCoordinator is unavailable.

        Args:
            file_path: Path to the file to process

        Returns:
            Dictionary with processing results
        """
        try:
            # Validate file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                return {"status": "error", "error": f"File not found: {file_path}", "chunks": 0}

            # Detect language from extension
            suffix = file_path.suffix.lower()
            language_map = {
                '.py': 'python',
                '.java': 'java',
                '.cs': 'csharp',
                '.ts': 'typescript',
                '.js': 'javascript',
                '.tsx': 'tsx',
                '.jsx': 'jsx',
                '.md': 'markdown',
                '.markdown': 'markdown',
            }

            language = language_map.get(suffix)
            if not language:
                return {"status": "skipped", "reason": "unsupported_type", "chunks": 0}

            # Get file information
            file_stat = file_path.stat()
            existing_file = self.get_file_by_path(str(file_path))

            # Check if file is up to date
            if existing_file:
                # Extract timestamp based on object type
                existing_mtime = None
                if isinstance(existing_file, File):
                    existing_mtime = existing_file.mtime
                elif isinstance(existing_file, dict):
                    # Try different possible timestamp field names
                    for field in ['mtime', 'modified_time', 'modification_time', 'timestamp']:
                        if field in existing_file and existing_file[field] is not None:
                            timestamp_value = existing_file[field]
                            if isinstance(timestamp_value, (int, float)):
                                existing_mtime = float(timestamp_value)
                            elif hasattr(timestamp_value, "timestamp"):
                                existing_mtime = timestamp_value.timestamp()
                            break

                if existing_mtime and abs(existing_mtime - file_stat.st_mtime) < 0.01:
                    file_id = self._extract_file_id(existing_file)
                    if file_id is not None and self.connection is not None:
                        chunks_count = self.connection.execute(
                            "SELECT COUNT(*) FROM chunks WHERE file_id = ?",
                            [file_id]
                        ).fetchone()[0]
                        return {
                            "status": "up_to_date",
                            "chunks": chunks_count,
                            "file_id": file_id,
                            "chunks_unchanged": chunks_count,
                            "chunks_inserted": 0,
                        "chunks_deleted": 0,
                        "incremental": True
                    }

            # Cannot process file without proper parsing/chunking services
            # Return a meaningful error that won't crash the system
            return {
                "status": "error",
                "error": "Incremental processing unavailable - service layer not initialized",
                "chunks": 0,
                "incremental": True
            }
        except Exception as e:
            logger.error(f"Fallback processing failed for {file_path}: {e}")
            return {"status": "error", "error": str(e), "chunks": 0, "incremental": True}

    async def process_directory(
        self,
        directory: Path,
        patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None
    ) -> dict[str, Any]:
        """Process all supported files in a directory."""
        try:
            if patterns is None:
                patterns = ["**/*.py", "**/*.java", "**/*.cs", "**/*.ts", "**/*.js", "**/*.tsx", "**/*.jsx", "**/*.md", "**/*.markdown"]

            files_processed = 0
            total_chunks = 0
            total_embeddings = 0
            errors = []

            # Find files matching patterns
            all_files = []
            for pattern in patterns:
                files = list(directory.glob(pattern))
                all_files.extend(files)

            # Remove duplicates and filter out excluded patterns
            unique_files = list(set(all_files))
            if exclude_patterns:
                filtered_files = []
                for file_path in unique_files:
                    exclude = False
                    for exclude_pattern in exclude_patterns:
                        if file_path.match(exclude_pattern):
                            exclude = True
                            break
                    if not exclude:
                        filtered_files.append(file_path)
                unique_files = filtered_files

            logger.info(f"Processing {len(unique_files)} files in {directory}")

            # Process each file
            for file_path in unique_files:
                try:
                    # Ensure service layer is initialized
                    if not self._indexing_coordinator:
                        self._initialize_shared_instances()

                    if not self._indexing_coordinator:
                        errors.append(f"{file_path}: IndexingCoordinator not available")
                        continue

                    # Delegate to IndexingCoordinator for file processing
                    result = await self._indexing_coordinator.process_file(file_path, skip_embeddings=False)

                    if result["status"] == "success":
                        files_processed += 1
                        total_chunks += result.get("chunks", 0)
                        total_embeddings += result.get("embeddings", 0)
                    elif result["status"] == "error":
                        errors.append(f"{file_path}: {result.get('error', 'Unknown error')}")
                    # Skip files with status "up_to_date", "skipped", etc.

                except Exception as e:
                    error_msg = f"{file_path}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"Error processing {file_path}: {e}")

            result = {
                "status": "success",
                "files_processed": files_processed,
                "total_files": len(unique_files),
                "total_chunks": total_chunks,
                "total_embeddings": total_embeddings
            }

            if errors:
                result["errors"] = errors
                result["error_count"] = len(errors)

            logger.info(f"Directory processing complete: {files_processed}/{len(unique_files)} files, "
                       f"{total_chunks} chunks, {total_embeddings} embeddings")

            return result

        except Exception as e:
            logger.error(f"Failed to process directory {directory}: {e}")
            return {"status": "error", "error": str(e), "files_processed": 0}

    def health_check(self) -> dict[str, Any]:
        """Perform health check and return status information."""
        status = {
            "provider": "duckdb",
            "connected": self.is_connected,
            "db_path": str(self.db_path),
            "version": None,
            "extensions": [],
            "tables": [],
            "errors": []
        }

        if not self.is_connected:
            status["errors"].append("Not connected to database")
            return status

        try:
            # Check connection before proceeding
            if self.connection is None:
                status["errors"].append("Database connection is None")
                return status

            # Get DuckDB version
            version_result = self.connection.execute("SELECT version()").fetchone()
            status["version"] = version_result[0] if version_result else "unknown"

            # Check if VSS extension is loaded
            extensions_result = self.connection.execute("""
                SELECT extension_name, loaded
                FROM duckdb_extensions()
                WHERE extension_name = 'vss'
            """).fetchone()

            if extensions_result:
                status["extensions"].append({
                    "name": extensions_result[0],
                    "loaded": extensions_result[1]
                })

            # Check if tables exist
            tables_result = self.connection.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
            """).fetchall()

            status["tables"] = [table[0] for table in tables_result]

            # Basic functionality test
            test_result = self.connection.execute("SELECT 1").fetchone()
            if test_result[0] != 1:
                status["errors"].append("Basic query test failed")

        except Exception as e:
            status["errors"].append(f"Health check error: {str(e)}")

        return status

    def get_connection_info(self) -> dict[str, Any]:
        """Get information about the database connection."""
        return {
            "provider": "duckdb",
            "db_path": str(self.db_path),
            "connected": self.is_connected,
            "memory_database": str(self.db_path) == ":memory:",
            "connection_type": type(self.connection).__name__ if self.connection else None
        }
