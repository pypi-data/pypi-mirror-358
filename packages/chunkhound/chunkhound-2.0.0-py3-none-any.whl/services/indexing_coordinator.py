"""Indexing coordinator service for ChunkHound - orchestrates file indexing workflows."""

import zlib
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

from loguru import logger
from tqdm import tqdm

from core.models import File
from core.types import FileId, FilePath, Language
from interfaces.database_provider import DatabaseProvider
from interfaces.embedding_provider import EmbeddingProvider
from interfaces.language_parser import LanguageParser, ParseResult

from .base_service import BaseService


class IndexingCoordinator(BaseService):
    """Coordinates file indexing workflows with parsing, chunking, and embedding generation."""

    # Default exclude patterns for file discovery
    DEFAULT_EXCLUDE_PATTERNS = [
        "*/__pycache__/*", 
        "*/node_modules/*", 
        "*/.git/*", 
        "*/venv/*", 
        "*/.venv/*", 
        "*/.mypy_cache/*"
    ]

    def __init__(
        self,
        database_provider: DatabaseProvider,
        embedding_provider: EmbeddingProvider | None = None,
        language_parsers: dict[Language, LanguageParser] | None = None
    ):
        """Initialize indexing coordinator.

        Args:
            database_provider: Database provider for persistence
            embedding_provider: Optional embedding provider for vector generation
            language_parsers: Optional mapping of language to parser implementations
        """
        super().__init__(database_provider)
        self._embedding_provider = embedding_provider
        self._language_parsers = language_parsers or {}

        # Performance optimization: shared instances
        self._parser_cache: dict[Language, LanguageParser] = {}

    def add_language_parser(self, language: Language, parser: LanguageParser) -> None:
        """Add or update a language parser.

        Args:
            language: Programming language identifier
            parser: Parser implementation for the language
        """
        self._language_parsers[language] = parser
        # Clear cache for this language
        if language in self._parser_cache:
            del self._parser_cache[language]

    def get_parser_for_language(self, language: Language) -> LanguageParser | None:
        """Get parser for specified language with caching.

        Args:
            language: Programming language identifier

        Returns:
            Parser instance or None if not supported
        """
        if language not in self._parser_cache:
            if language in self._language_parsers:
                parser = self._language_parsers[language]
                # Ensure parser is initialized if setup method exists
                if hasattr(parser, 'setup') and callable(getattr(parser, 'setup')):
                    parser.setup()
                self._parser_cache[language] = parser
            else:
                return None

        return self._parser_cache[language]

    def detect_file_language(self, file_path: Path) -> Language | None:
        """Detect programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language enum value or None if unsupported
        """
        language = Language.from_file_extension(file_path)
        return language if language != Language.UNKNOWN else None

    def _calculate_file_crc32(self, file_path: Path) -> int | None:
        """Calculate CRC32 checksum of file content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            CRC32 checksum as integer, or None if file cannot be read
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return zlib.crc32(content) & 0xffffffff  # Ensure unsigned 32-bit
        except Exception as e:
            logger.warning(f"Failed to calculate CRC32 for {file_path}: {e}")
            return None

    async def process_file(self, file_path: Path, skip_embeddings: bool = False) -> dict[str, Any]:
        """Process a single file through the complete indexing pipeline.

        Args:
            file_path: Path to the file to process
            skip_embeddings: If True, skip embedding generation for batch processing

        Returns:
            Dictionary with processing results including status, chunks, and embeddings
        """

        try:
            # Validate file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                return {"status": "error", "error": f"File not found: {file_path}", "chunks": 0}

            # Detect language
            language = self.detect_file_language(file_path)
            if not language:
                return {"status": "skipped", "reason": "unsupported_type", "chunks": 0}

            # Get parser for language
            parser = self.get_parser_for_language(language)
            if not parser:
                return {"status": "error", "error": f"No parser available for {language}", "chunks": 0}

            # Get file stats for storage/update operations
            file_stat = file_path.stat()

            logger.debug(f"Processing file: {file_path}")
            logger.debug(f"File stat: mtime={file_stat.st_mtime}, size={file_stat.st_size}")

            # Note: Removed timestamp checking logic - if IndexingCoordinator.process_file()
            # was called, the file needs processing. File watcher handles change detection.

            # Parse file content - can return ParseResult or List[Dict[str, Any]]
            parsed_data = parser.parse_file(file_path)
            if not parsed_data:
                return {"status": "no_content", "chunks": 0}

            # Extract chunks from ParseResult object or direct list
            raw_chunks: list[dict[str, Any]]
            if isinstance(parsed_data, ParseResult):
                # New parser providers return ParseResult object
                raw_chunks = parsed_data.chunks
            elif isinstance(parsed_data, list):
                # Legacy parsers return chunks directly
                raw_chunks = parsed_data
            else:
                # Fallback for unexpected types
                raw_chunks = []

            # Filter empty chunks early to reduce storage warnings
            chunks = self._filter_valid_chunks(raw_chunks)

            if not chunks:
                return {"status": "no_chunks", "chunks": 0}

            # Check if this is an existing file that has been modified BEFORE storing the record
            existing_file = self._db.get_file_by_path(str(file_path))
            is_file_modified = False

            if existing_file:
                # Check if file was actually modified (different mtime)
                # Use same field resolution logic as process_file_incremental
                existing_mtime = 0
                current_mtime = file_stat.st_mtime

                if isinstance(existing_file, dict):
                    # Try different possible timestamp field names
                    for field in ['mtime', 'modified_time', 'modification_time', 'timestamp']:
                        if field in existing_file and existing_file[field] is not None:
                            timestamp_value = existing_file[field]
                            if isinstance(timestamp_value, (int, float)):
                                existing_mtime = float(timestamp_value)
                                break
                            elif hasattr(timestamp_value, "timestamp"):
                                existing_mtime = timestamp_value.timestamp()
                                break
                else:
                    # Handle File model objects
                    if hasattr(existing_file, 'mtime'):
                        existing_mtime = float(existing_file.mtime)

                # Two-tier change detection: mtime first, then CRC32 if needed
                if abs(current_mtime - existing_mtime) > 0.001:
                    # mtime changed, file is definitely modified
                    is_file_modified = True
                    logger.debug(f"File modification check: {file_path} - mtime changed (existing: {existing_mtime}, current: {current_mtime})")
                else:
                    # mtime unchanged, check CRC32 for robust content detection
                    current_crc32 = self._calculate_file_crc32(file_path)
                    existing_crc32 = existing_file.get('content_crc32') if isinstance(existing_file, dict) else getattr(existing_file, 'content_crc32', None)
                    
                    if current_crc32 is None:
                        # Can't calculate CRC32, assume modified for safety
                        is_file_modified = True
                        logger.debug(f"File modification check: {file_path} - CRC32 calculation failed, assuming modified")
                    elif existing_crc32 is None:
                        # No existing CRC32, file needs processing to store CRC32
                        is_file_modified = True
                        logger.debug(f"File modification check: {file_path} - no existing CRC32, needs processing")
                    else:
                        # Compare CRC32 checksums
                        is_file_modified = (current_crc32 != existing_crc32)
                        logger.debug(f"File modification check: {file_path} - CRC32 comparison (existing: {existing_crc32}, current: {current_crc32}, modified: {is_file_modified})")

                # If file hasn't been modified, return up_to_date status
                if not is_file_modified:
                    # Get existing chunk count for consistency
                    file_id = existing_file.get('id') if isinstance(existing_file, dict) else existing_file.id
                    existing_chunks = self._db.get_chunks_by_file_id(file_id)
                    return {
                        "status": "up_to_date",
                        "file_id": file_id,
                        "chunks": len(existing_chunks) if existing_chunks else 0,
                        "embeddings": 0  # No new embeddings generated
                    }

            # Store or update file record
            file_id = self._store_file_record(file_path, file_stat, language)
            if file_id is None:
                return {"status": "error", "chunks": 0, "error": "Failed to store file record"}

            # Delete old chunks only if file was actually modified
            if existing_file and is_file_modified:
                self._db.delete_file_chunks(file_id)
                logger.debug(f"Deleted existing chunks for modified file: {file_path}")

            # Store chunks and generate embeddings
            # Note: Transaction safety is handled by the database provider layer
            chunk_ids = self._store_chunks(file_id, chunks, language)
            embeddings_generated = 0
            if not skip_embeddings and self._embedding_provider and chunk_ids:
                embeddings_generated = await self._generate_embeddings(chunk_ids, chunks)

            result = {
                "status": "success",
                "file_id": file_id,
                "chunks": len(chunks),
                "chunk_ids": chunk_ids,
                "embeddings": embeddings_generated
            }

            # Include chunk data for batch processing
            if skip_embeddings:
                result["chunk_data"] = chunks

            return result

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return {"status": "error", "error": str(e), "chunks": 0}

    async def _process_file_modification_safe(
        self,
        file_id: int,
        file_path: Path,
        file_stat,
        chunks: list[dict[str, Any]],
        language: Language,
        skip_embeddings: bool
    ) -> tuple[list[int], int]:
        """Process file modification with transaction safety to prevent data loss.

        This method ensures that old content is preserved if new content processing fails.
        Uses database transactions and backup tables for rollback capability.

        Args:
            file_id: Existing file ID in database
            file_path: Path to the file being processed
            file_stat: File stat object with mtime and size
            chunks: New chunks to store
            language: File language type
            skip_embeddings: Whether to skip embedding generation

        Returns:
            Tuple of (chunk_ids, embeddings_generated)

        Raises:
            Exception: If transaction-safe processing fails and rollback is needed
        """
        import time

        logger.debug(f"Transaction-safe processing - Starting for file_id: {file_id}")

        # Create unique backup table names using timestamp
        timestamp = int(time.time() * 1000000)  # microseconds for uniqueness
        chunks_backup_table = f"chunks_backup_{timestamp}"
        embeddings_backup_table = f"embeddings_1536_backup_{timestamp}"

        connection = self._db.connection
        if connection is None:
            raise RuntimeError("Database connection not available")

        try:
            # Start transaction
            connection.execute("BEGIN TRANSACTION")
            logger.debug("Transaction-safe processing - Transaction started")

            # Get count of existing chunks for reporting
            existing_chunks_count = connection.execute(
                "SELECT COUNT(*) FROM chunks WHERE file_id = ?", [file_id]
            ).fetchone()[0]
            logger.debug(f"Transaction-safe processing - Found {existing_chunks_count} existing chunks")

            # Create backup table for chunks
            connection.execute(f"""
                CREATE TABLE {chunks_backup_table} AS
                SELECT * FROM chunks WHERE file_id = ?
            """, [file_id])
            logger.debug(f"Transaction-safe processing - Created backup table: {chunks_backup_table}")

            # Create backup table for embeddings
            connection.execute(f"""
                CREATE TABLE {embeddings_backup_table} AS
                SELECT e.* FROM embeddings_1536 e
                JOIN chunks c ON e.chunk_id = c.id
                WHERE c.file_id = ?
            """, [file_id])
            logger.debug(f"Transaction-safe processing - Created embedding backup: {embeddings_backup_table}")

            # Update file metadata first
            self._db.update_file(file_id, size_bytes=file_stat.st_size, mtime=file_stat.st_mtime)

            # Remove old content (but backup preserved in transaction)
            self._db.delete_file_chunks(file_id)
            logger.debug("Transaction-safe processing - Removed old content")

            # Store new chunks
            chunk_ids = self._store_chunks(file_id, chunks, language)
            if not chunk_ids:
                raise Exception("Failed to store new chunks")
            logger.debug(f"Transaction-safe processing - Stored {len(chunk_ids)} new chunks")

            # Generate embeddings if requested
            embeddings_generated = 0
            if not skip_embeddings and self._embedding_provider and chunk_ids:
                embeddings_generated = await self._generate_embeddings(chunk_ids, chunks, connection)
                logger.debug(f"Transaction-safe processing - Generated {embeddings_generated} embeddings")

            # Commit transaction
            connection.execute("COMMIT")
            logger.debug("Transaction-safe processing - Transaction committed successfully")

            # Cleanup backup tables
            try:
                connection.execute(f"DROP TABLE {chunks_backup_table}")
                connection.execute(f"DROP TABLE {embeddings_backup_table}")
                logger.debug("Transaction-safe processing - Backup tables cleaned up")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup backup tables: {cleanup_error}")

            return chunk_ids, embeddings_generated

        except Exception as e:
            logger.error(f"Transaction-safe processing failed: {e}")

            try:
                # Rollback transaction
                connection.execute("ROLLBACK")
                logger.debug("Transaction-safe processing - Transaction rolled back")

                # Restore from backup tables if they exist
                try:
                    # Check if backup tables still exist
                    backup_exists = connection.execute(f"""
                        SELECT COUNT(*) FROM sqlite_master
                        WHERE type='table' AND name='{chunks_backup_table}'
                    """).fetchone()[0] > 0

                    if backup_exists:
                        # Restore chunks from backup
                        connection.execute(f"""
                            INSERT INTO chunks SELECT * FROM {chunks_backup_table}
                        """)

                        # Restore embeddings from backup
                        connection.execute(f"""
                            INSERT INTO embeddings_1536 SELECT * FROM {embeddings_backup_table}
                        """)

                        logger.info("Transaction-safe processing - Original content restored from backup")

                        # Cleanup backup tables
                        connection.execute(f"DROP TABLE {chunks_backup_table}")
                        connection.execute(f"DROP TABLE {embeddings_backup_table}")

                except Exception as restore_error:
                    logger.error(f"Failed to restore from backup: {restore_error}")

            except Exception as rollback_error:
                logger.error(f"Failed to rollback transaction: {rollback_error}")

            # Re-raise the original exception
            raise e

    async def process_directory(
        self,
        directory: Path,
        patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None
    ) -> dict[str, Any]:
        """Process all supported files in a directory with batch optimization and consistency checks.

        Args:
            directory: Directory path to process
            patterns: Optional file patterns to include
            exclude_patterns: Optional file patterns to exclude

        Returns:
            Dictionary with processing statistics
        """
        try:
            # Phase 1: Discovery - Discover files in directory
            files = self._discover_files(directory, patterns, exclude_patterns)

            if not files:
                return {"status": "no_files", "files_processed": 0, "total_chunks": 0}

            # Phase 2: Reconciliation - Ensure database consistency by removing orphaned files
            cleaned_files = self._cleanup_orphaned_files(directory, files, exclude_patterns)

            logger.info(f"Directory consistency: {len(files)} files discovered, {cleaned_files} orphaned files cleaned")

            # Phase 3: Update - Process files with enhanced cache logic
            total_files = 0
            total_chunks = 0

            # Create progress bar for file processing
            with tqdm(total=len(files), desc="Processing files", unit="file") as pbar:
                for file_path in files:
                    result = await self.process_file(file_path, skip_embeddings=True)

                    if result["status"] in ["success", "up_to_date"]:
                        total_files += 1
                        total_chunks += result["chunks"]
                        pbar.set_postfix_str(f"{total_chunks} chunks")
                    elif result["status"] in ["skipped", "no_content", "no_chunks"]:
                        # Still update progress for skipped files
                        pass
                    else:
                        # Log errors but continue processing
                        logger.warning(f"Failed to process {file_path}: {result.get('error', 'unknown error')}")

                    pbar.update(1)

            # Note: Embedding generation is handled separately via generate_missing_embeddings()
            # to provide a unified progress experience

            return {
                "status": "success",
                "files_processed": total_files,
                "total_chunks": total_chunks
            }

        except Exception as e:
            logger.error(f"Failed to process directory {directory}: {e}")
            return {"status": "error", "error": str(e)}

    def _extract_file_id(self, file_record: dict[str, Any] | File) -> int | None:
        """Safely extract file ID from either dict or File model."""
        if isinstance(file_record, File):
            return file_record.id
        elif isinstance(file_record, dict) and "id" in file_record:
            return file_record["id"]
        else:
            return None


    def _store_file_record(self, file_path: Path, file_stat: Any, language: Language) -> int:
        """Store or update file record in database with CRC32."""
        # Calculate CRC32 for content tracking
        content_crc32 = self._calculate_file_crc32(file_path)
        
        # Check if file already exists
        existing_file = self._db.get_file_by_path(str(file_path))

        if existing_file:
            # Update existing file with new metadata including CRC32
            if isinstance(existing_file, dict) and "id" in existing_file:
                file_id = existing_file["id"]
                self._db.update_file(file_id, size_bytes=file_stat.st_size, mtime=file_stat.st_mtime, content_crc32=content_crc32)
                return file_id

        # Create new File model instance with CRC32
        file_model = File(
            path=FilePath(str(file_path)),
            size_bytes=file_stat.st_size,
            mtime=file_stat.st_mtime,
            language=language,
            content_crc32=content_crc32
        )
        return self._db.insert_file(file_model)

    def _filter_valid_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter out chunks with empty content early in the process."""
        valid_chunks = []
        filtered_count = 0

        for chunk in chunks:
            code_content = chunk.get("code", "")
            if code_content and code_content.strip():
                valid_chunks.append(chunk)
            else:
                filtered_count += 1

        # Log summary instead of individual warnings to reduce noise
        if filtered_count > 0:
            logger.debug(f"Filtered {filtered_count} empty chunks during parsing")

        return valid_chunks

    def _store_chunks(self, file_id: int, chunks: list[dict[str, Any]], language: Language) -> list[int]:
        """Store chunks in database and return chunk IDs."""
        chunk_ids = []
        for chunk in chunks:
            # Create Chunk model instance
            from core.models import Chunk
            from core.types import ChunkType

            # Convert chunk_type string to enum
            chunk_type_str = chunk.get("chunk_type", "function")
            try:
                chunk_type_enum = ChunkType(chunk_type_str)
            except ValueError:
                chunk_type_enum = ChunkType.FUNCTION  # default fallback

            chunk_model = Chunk(
                file_id=FileId(file_id),
                symbol=chunk.get("symbol", ""),
                start_line=chunk.get("start_line", 0),
                end_line=chunk.get("end_line", 0),
                code=chunk.get("code", ""),
                chunk_type=chunk_type_enum,
                language=language,  # Use the file's detected language
                parent_header=chunk.get("parent_header")
            )
            chunk_id = self._db.insert_chunk(chunk_model)
            chunk_ids.append(chunk_id)
        return chunk_ids

    async def get_stats(self) -> dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with file, chunk, and embedding counts
        """
        return self._db.get_stats()

    async def remove_file(self, file_path: str) -> int:
        """Remove a file and all its chunks from the database.

        Args:
            file_path: Path to the file to remove

        Returns:
            Number of chunks removed
        """
        try:
            # Get file record to get chunk count before deletion
            file_record = self._db.get_file_by_path(file_path)
            if not file_record:
                return 0

            # Get file ID
            file_id = self._extract_file_id(file_record)
            if file_id is None:
                return 0

            # Count chunks before deletion
            chunks = self._db.get_chunks_by_file_id(file_id)
            chunk_count = len(chunks) if chunks else 0

            # Delete the file completely (this will also delete chunks and embeddings)
            success = self._db.delete_file_completely(file_path)
            return chunk_count if success else 0

        except Exception as e:
            logger.error(f"Failed to remove file {file_path}: {e}")
            return 0

    async def generate_missing_embeddings(self) -> dict[str, Any]:
        """Generate embeddings for chunks that don't have them.

        Returns:
            Dictionary with generation results
        """
        if not self._embedding_provider:
            return {"status": "error", "error": "No embedding provider configured", "generated": 0}

        try:
            # Use EmbeddingService for embedding generation
            from .embedding_service import EmbeddingService

            embedding_service = EmbeddingService(
                database_provider=self._db,
                embedding_provider=self._embedding_provider
            )

            return await embedding_service.generate_missing_embeddings()

        except Exception as e:
            logger.error(f"Failed to generate missing embeddings: {e}")
            return {"status": "error", "error": str(e), "generated": 0}

    async def _generate_embeddings(self, chunk_ids: list[int], chunks: list[dict[str, Any]], connection=None) -> int:
        """Generate embeddings for chunks."""
        if not self._embedding_provider:
            return 0

        try:
            # Filter out chunks with empty text content before embedding
            valid_chunk_data = []
            empty_count = 0
            for chunk_id, chunk in zip(chunk_ids, chunks):
                text = chunk.get("code", "").strip()
                if text:  # Only include chunks with actual content
                    valid_chunk_data.append((chunk_id, chunk, text))
                else:
                    empty_count += 1

            # Log metrics for empty chunks
            if empty_count > 0:
                logger.info(f"Filtered {empty_count} empty text chunks before embedding generation")

            if not valid_chunk_data:
                logger.debug("No valid chunks with text content for embedding generation")
                return 0

            # Extract data for embedding generation
            valid_chunk_ids = [chunk_id for chunk_id, _, _ in valid_chunk_data]
            valid_chunks = [chunk for _, chunk, _ in valid_chunk_data]
            texts = [text for _, _, text in valid_chunk_data]

            # Generate embeddings (progress tracking handled by missing embeddings phase)
            embedding_results = await self._embedding_provider.embed(texts)

            # Store embeddings in database
            embeddings_data = []
            for chunk_id, vector in zip(valid_chunk_ids, embedding_results):
                embeddings_data.append({
                    "chunk_id": chunk_id,
                    "provider": self._embedding_provider.name,
                    "model": self._embedding_provider.model,
                    "dims": len(vector),
                    "embedding": vector
                })

            # Database storage - use provided connection for transaction context
            result = self._db.insert_embeddings_batch(embeddings_data, connection=connection)

            return result

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return 0

    async def _generate_embeddings_batch(self, file_chunks: list[tuple[int, dict[str, Any]]]) -> int:
        """Generate embeddings for chunks in optimized batches."""
        if not self._embedding_provider or not file_chunks:
            return 0

        # Extract chunk IDs and text content
        chunk_ids = [chunk_id for chunk_id, _ in file_chunks]
        chunks = [chunk_data for _, chunk_data in file_chunks]

        return await self._generate_embeddings(chunk_ids, chunks)

    def _discover_files(
        self,
        directory: Path,
        patterns: list[str] | None,
        exclude_patterns: list[str] | None
    ) -> list[Path]:
        """Discover files in directory matching patterns."""
        files = []

        # Default patterns for supported languages
        if not patterns:
            # Get patterns from Language enum
            patterns = []
            for ext in Language.get_all_extensions():
                patterns.append(f"*{ext}")
            # Add special filenames
            patterns.extend(["Makefile", "makefile", "GNUmakefile", "gnumakefile"])

        # Default exclude patterns
        if not exclude_patterns:
            exclude_patterns = self.DEFAULT_EXCLUDE_PATTERNS

        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    # Check exclude patterns using proper fnmatch against both absolute and relative paths
                    should_exclude = False
                    rel_path = file_path.relative_to(directory)

                    for exclude_pattern in exclude_patterns:
                        # Test both relative path and absolute path for pattern matching
                        if (fnmatch(str(rel_path), exclude_pattern) or
                            fnmatch(str(file_path), exclude_pattern)):
                            should_exclude = True
                            break

                    if not should_exclude:
                        files.append(file_path)

        return sorted(files)

    def _cleanup_orphaned_files(self, directory: Path, current_files: list[Path], exclude_patterns: list[str] | None = None) -> int:
        """Remove database entries for files that no longer exist in the directory.
        
        Args:
            directory: Directory being processed
            current_files: List of files currently in the directory
            exclude_patterns: Optional list of exclude patterns to check against
            
        Returns:
            Number of orphaned files cleaned up
        """
        try:
            # Create set of absolute paths for fast lookup
            current_file_paths = {str(file_path.absolute()) for file_path in current_files}
            
            # Get all files in database that are under this directory
            directory_str = str(directory.absolute())
            query = """
                SELECT id, path 
                FROM files 
                WHERE path LIKE ? || '%'
            """
            db_files = self._db.execute_query(query, [directory_str])
            
            # Find orphaned files (in DB but not on disk or excluded by patterns)
            orphaned_files = []
            patterns_to_check = exclude_patterns if exclude_patterns else self.DEFAULT_EXCLUDE_PATTERNS
            
            for db_file in db_files:
                file_path = db_file['path']
                
                # Check if file should be excluded based on current patterns
                should_exclude = False
                
                # Convert to Path for relative path calculation
                file_path_obj = Path(file_path)
                try:
                    rel_path = file_path_obj.relative_to(directory)
                except ValueError:
                    # File is not under the directory, use absolute path
                    rel_path = file_path_obj
                
                for exclude_pattern in patterns_to_check:
                    # Check both relative and absolute paths
                    if (fnmatch(str(rel_path), exclude_pattern) or 
                        fnmatch(file_path, exclude_pattern)):
                        should_exclude = True
                        break
                
                # Mark for removal if not in current files or should be excluded
                if file_path not in current_file_paths or should_exclude:
                    orphaned_files.append(file_path)
            
            # Remove orphaned files with progress bar
            orphaned_count = 0
            if orphaned_files:
                with tqdm(total=len(orphaned_files), desc="Cleaning orphaned files", unit="file") as pbar:
                    for file_path in orphaned_files:
                        if self._db.delete_file_completely(file_path):
                            orphaned_count += 1
                        pbar.update(1)
                
                logger.info(f"Cleaned up {orphaned_count} orphaned files from database")
            
            return orphaned_count
            
        except Exception as e:
            logger.warning(f"Failed to cleanup orphaned files: {e}")
            return 0
