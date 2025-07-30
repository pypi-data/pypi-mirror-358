"""
Main image migration orchestrator
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from tqdm import tqdm
from urllib.parse import urljoin
import tempfile

from .config import Config
from .logger import ProgressLogger
from .utils import (
    validate_path, is_zip_file, extract_zip, create_backup,
    find_files_by_extension, is_url, safe_read_file, safe_write_file,
    get_relative_path, is_image_file
)
from .parsers import ParserRegistry, ImageReference
from .cloudflare_client import CloudflareImagesClient, ImageUploadResult


class MigrationResult:
    """Result of a migration operation."""
    
    def __init__(self):
        self.success = False
        self.files_processed = 0
        self.images_found = 0
        self.images_uploaded = 0
        self.images_failed = 0
        self.files_modified = 0
        self.errors = []
        self.backup_path = None
        self.temp_dir = None
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
    
    def get_summary(self) -> Dict:
        """Get a summary of the migration results."""
        return {
            'success': self.success,
            'files_processed': self.files_processed,
            'images_found': self.images_found,
            'images_uploaded': self.images_uploaded,
            'images_failed': self.images_failed,
            'files_modified': self.files_modified,
            'error_count': len(self.errors),
            'backup_path': str(self.backup_path) if self.backup_path else None
        }


class ImageMigrator:
    """Main class for migrating images to Cloudflare Images."""
    
    def __init__(self, config: Config, logger):
        self.config = config
        self.logger = logger
        self.progress_logger = ProgressLogger(logger)
        self.parser_registry = ParserRegistry()
        self.cf_client = CloudflareImagesClient(config, logger)
        
        # Tracking
        self.processed_files = set()
        self.image_mapping = {}  # original_path -> cloudflare_url
        self.failed_images = set()
    
    def migrate(self, source_path: Path) -> bool:
        """
        Main migration function.
        
        Args:
            source_path: Path to source directory or zip file
            
        Returns:
            True if migration was successful
        """
        result = MigrationResult()
        
        try:
            self.logger.info(f"Starting migration of: {source_path}")
            
            # Test Cloudflare connection
            if not self.config.dry_run:
                self.logger.info("Testing Cloudflare Images API connection...")
                if not self.cf_client.test_connection():
                    result.add_error("Failed to connect to Cloudflare Images API")
                    return False
                self.logger.info("✓ Successfully connected to Cloudflare Images API")
            
            # Prepare working directory
            working_dir = self._prepare_working_directory(source_path, result)
            if not working_dir:
                return False
            
            self.logger.info(f"Working directory: {working_dir}")
            
            # Create backup if requested
            if self.config.backup and not self.config.dry_run:
                result.backup_path = self._create_backup(source_path)
                self.logger.info(f"Created backup: {result.backup_path}")
            
            # Phase 1: Scan and collect all image references
            self.logger.info("Phase 1: Scanning for image references...")
            image_references = self._scan_for_images(working_dir, result)
            
            if not image_references:
                self.logger.info("No image references found.")
                return True
            
            self.logger.info(f"Found {len(image_references)} image references")
            
            # Phase 2: Process and upload images
            self.logger.info("Phase 2: Processing and uploading images...")
            if not self.config.dry_run:
                success = self._process_images(image_references, working_dir, result)
                if not success:
                    return False
            else:
                self.logger.info("Dry run mode - skipping uploads")
                result.images_found = len(image_references)
            
            # Phase 3: Replace references in code
            self.logger.info("Phase 3: Replacing image references in code...")
            self._replace_image_references(image_references, working_dir, result)
            
            # Phase 4: Copy results back if working with zip
            if result.temp_dir and not self.config.dry_run:
                self._copy_results_back(working_dir, source_path, result)
            
            # Final summary
            result.success = True
            self.progress_logger.log_progress_summary(self.config.dry_run)
            
            # Cleanup
            self._cleanup(result)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            result.add_error(str(e))
            self._cleanup(result)
            return False
    
    def _prepare_working_directory(self, source_path: Path, result: MigrationResult) -> Optional[Path]:
        """Prepare the working directory for migration."""
        try:
            if source_path.is_file() and is_zip_file(source_path):
                # Extract zip to temporary directory
                self.logger.info(f"Extracting zip file: {source_path}")
                temp_dir = Path(tempfile.mkdtemp(prefix="cf_images_migration_"))
                extracted_dir = extract_zip(source_path, temp_dir)
                result.temp_dir = temp_dir
                return extracted_dir
            elif source_path.is_dir():
                # Use directory directly
                return source_path
            else:
                result.add_error(f"Invalid source path: {source_path}")
                return None
        except Exception as e:
            result.add_error(f"Failed to prepare working directory: {str(e)}")
            return None
    
    def _create_backup(self, source_path: Path) -> Optional[Path]:
        """Create a backup of the source."""
        try:
            return create_backup(source_path)
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {str(e)}")
            return None
    
    def _scan_for_images(self, working_dir: Path, result: MigrationResult) -> List[Tuple[Path, List[ImageReference]]]:
        """Scan the working directory for image references."""
        image_references = []
        
        # Find files to process
        files_to_process = find_files_by_extension(
            working_dir,
            self.config.file_types,
            self.config.exclude_dirs
        )
        
        self.logger.info(f"Scanning {len(files_to_process)} files...")
        
        # Process files with progress bar
        with tqdm(files_to_process, desc="Scanning files", disable=not self.logger) as pbar:
            for file_path in pbar:
                try:
                    pbar.set_description(f"Scanning {file_path.name}")
                    
                    # Parse file for image references
                    refs = self.parser_registry.parse_file(file_path)
                    
                    if refs:
                        image_references.append((file_path, refs))
                        self.progress_logger.log_file_processed(
                            get_relative_path(file_path, working_dir),
                            len(refs)
                        )
                    
                    result.files_processed += 1
                    
                except Exception as e:
                    error_msg = f"Error scanning {file_path}: {str(e)}"
                    self.logger.warning(error_msg)
                    result.add_error(error_msg)
        
        return image_references
    
    def _process_images(self, image_references: List[Tuple[Path, List[ImageReference]]], 
                       working_dir: Path, result: MigrationResult) -> bool:
        """Process and upload images to Cloudflare."""
        
        # Collect all unique images
        unique_images = self._collect_unique_images(image_references, working_dir)
        result.images_found = len(unique_images)
        
        if not unique_images:
            self.logger.info("No images to upload.")
            return True
        
        self.logger.info(f"Found {len(unique_images)} unique images to upload")
        
        # Upload images with progress bar
        with tqdm(unique_images, desc="Uploading images", disable=not self.logger) as pbar:
            for image_info in pbar:
                original_path = image_info['original_path']
                pbar.set_description(f"Uploading {Path(original_path).name}")
                
                try:
                    if image_info['is_url']:
                        # Upload from URL
                        upload_result = self.cf_client.upload_image_from_url(original_path)
                    else:
                        # Upload local file
                        local_path = working_dir / original_path if not Path(original_path).is_absolute() else Path(original_path)
                        if local_path.exists():
                            upload_result = self.cf_client.upload_image_from_path(local_path)
                        else:
                            upload_result = None
                    
                    if upload_result and upload_result.success:
                        self.image_mapping[original_path] = upload_result.delivery_url
                        self.progress_logger.log_image_uploaded(original_path, upload_result.image_id)
                        result.images_uploaded += 1
                    else:
                        error_msg = upload_result.error if upload_result else "Upload failed"
                        self.failed_images.add(original_path)
                        self.progress_logger.log_image_failed(original_path, error_msg)
                        result.images_failed += 1
                        result.add_error(f"Upload failed for {original_path}: {error_msg}")
                
                except Exception as e:
                    error_msg = f"Exception uploading {original_path}: {str(e)}"
                    self.logger.error(error_msg)
                    self.failed_images.add(original_path)
                    result.add_error(error_msg)
                    result.images_failed += 1
        
        success_rate = result.images_uploaded / result.images_found if result.images_found > 0 else 0
        self.logger.info(f"Upload complete: {result.images_uploaded}/{result.images_found} images uploaded ({success_rate:.1%} success rate)")
        
        return result.images_uploaded > 0 or result.images_found == 0
    
    def _collect_unique_images(self, image_references: List[Tuple[Path, List[ImageReference]]], 
                              working_dir: Path) -> List[Dict]:
        """Collect all unique images that need to be uploaded."""
        unique_images = {}
        
        for file_path, refs in image_references:
            for ref in refs:
                image_path = ref.path
                
                # Skip if already processed or failed
                if image_path in unique_images or image_path in self.failed_images:
                    continue
                
                # Skip data URLs
                if image_path.startswith('data:'):
                    continue
                
                # Determine if it's a URL or local file
                if is_url(image_path):
                    unique_images[image_path] = {
                        'original_path': image_path,
                        'is_url': True,
                        'references': []
                    }
                else:
                    # Handle local file
                    # Resolve relative paths
                    if not Path(image_path).is_absolute():
                        full_path = (file_path.parent / image_path).resolve()
                        # Try to make it relative to working directory
                        try:
                            rel_path = full_path.relative_to(working_dir)
                            normalized_path = str(rel_path)
                        except ValueError:
                            normalized_path = str(full_path)
                    else:
                        normalized_path = image_path
                    
                    # Check if file exists and is an image
                    local_path = working_dir / normalized_path if not Path(normalized_path).is_absolute() else Path(normalized_path)
                    if local_path.exists() and is_image_file(local_path, self.config.supported_image_formats):
                        unique_images[image_path] = {
                            'original_path': normalized_path,
                            'is_url': False,
                            'references': []
                        }
        
        return list(unique_images.values())
    
    def _replace_image_references(self, image_references: List[Tuple[Path, List[ImageReference]]], 
                                 working_dir: Path, result: MigrationResult):
        """Replace image references in files with Cloudflare URLs."""
        
        files_to_modify = {}  # file_path -> list of replacements
        
        # Collect all replacements needed
        for file_path, refs in image_references:
            replacements = []
            
            for ref in refs:
                original_path = ref.path
                
                # Skip if upload failed or no mapping
                if original_path in self.failed_images or original_path not in self.image_mapping:
                    continue
                
                cloudflare_url = self.image_mapping[original_path]
                replacements.append((ref, cloudflare_url))
            
            if replacements:
                files_to_modify[file_path] = replacements
        
        if not files_to_modify:
            self.logger.info("No files need modification.")
            return
        
        self.logger.info(f"Modifying {len(files_to_modify)} files...")
        
        # Apply replacements
        with tqdm(files_to_modify.items(), desc="Modifying files", disable=not self.logger) as pbar:
            for file_path, replacements in pbar:
                pbar.set_description(f"Modifying {file_path.name}")
                
                try:
                    if not self.config.dry_run:
                        success = self._modify_file(file_path, replacements)
                        if success:
                            result.files_modified += 1
                            self.progress_logger.log_file_modified(
                                get_relative_path(file_path, working_dir),
                                len(replacements)
                            )
                    else:
                        # Dry run - just log what would be changed
                        rel_path = get_relative_path(file_path, working_dir)
                        self.logger.info(f"Would modify {rel_path}: {len(replacements)} replacements")
                        result.files_modified += 1
                
                except Exception as e:
                    error_msg = f"Error modifying {file_path}: {str(e)}"
                    self.logger.error(error_msg)
                    result.add_error(error_msg)
    
    def _modify_file(self, file_path: Path, replacements: List[Tuple[ImageReference, str]]) -> bool:
        """Modify a file by replacing image references."""
        try:
            # Read file content
            content = safe_read_file(file_path)
            if content is None:
                self.logger.error(f"Could not read file: {file_path}")
                return False
            
            # Apply replacements
            modified_content = content
            replacement_count = 0
            
            # Sort replacements by line number and column (descending) to avoid offset issues
            sorted_replacements = sorted(replacements, key=lambda x: (x[0].line_number, x[0].column), reverse=True)
            
            for ref, cloudflare_url in sorted_replacements:
                # Replace the original text with the new URL
                old_text = ref.original_text
                
                # Create new text with Cloudflare URL
                if ref.ref_type == 'url' or is_url(ref.path):
                    # Replace URL directly
                    new_text = old_text.replace(ref.path, cloudflare_url)
                else:
                    # Replace local path
                    new_text = old_text.replace(ref.path, cloudflare_url)
                
                # Apply replacement
                if old_text in modified_content:
                    modified_content = modified_content.replace(old_text, new_text, 1)
                    replacement_count += 1
                else:
                    # Try fuzzy matching for more complex cases
                    if self._fuzzy_replace(ref, cloudflare_url, modified_content):
                        replacement_count += 1
            
            # Write modified content back
            if replacement_count > 0:
                success = safe_write_file(file_path, modified_content)
                if success:
                    self.logger.debug(f"Applied {replacement_count} replacements to {file_path}")
                    return True
                else:
                    self.logger.error(f"Failed to write modified content to {file_path}")
                    return False
            else:
                self.logger.warning(f"No replacements applied to {file_path}")
                return False
        
        except Exception as e:
            self.logger.error(f"Exception modifying file {file_path}: {str(e)}")
            return False
    
    def _fuzzy_replace(self, ref: ImageReference, cloudflare_url: str, content: str) -> bool:
        """Try to perform fuzzy replacement when exact match fails."""
        try:
            # Try different patterns
            patterns = [
                f'["\']({re.escape(ref.path)})["\']',
                f'src\\s*=\\s*["\']({re.escape(ref.path)})["\']',
                f'url\\s*\\(\\s*["\']?({re.escape(ref.path)})["\']?\\s*\\)',
                f'\\!\\[.*?\\]\\(({re.escape(ref.path)})\\)',
            ]
            
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Replace using regex
                    content = re.sub(pattern, lambda m: m.group(0).replace(ref.path, cloudflare_url), content, count=1, flags=re.IGNORECASE)
                    return True
            
            return False
        except Exception:
            return False
    
    def _copy_results_back(self, working_dir: Path, original_path: Path, result: MigrationResult):
        """Copy results back when working with extracted zip."""
        try:
            if self.config.output_dir:
                output_path = Path(self.config.output_dir)
            else:
                output_path = original_path.parent / f"{original_path.stem}_migrated"
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all files from working directory to output
            for item in working_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, output_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, output_path / item.name)
            
            self.logger.info(f"Results copied to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to copy results: {str(e)}")
            result.add_error(f"Failed to copy results: {str(e)}")
    
    def _cleanup(self, result: MigrationResult):
        """Clean up temporary files."""
        if result.temp_dir and result.temp_dir.exists():
            try:
                shutil.rmtree(result.temp_dir)
                self.logger.debug(f"Cleaned up temporary directory: {result.temp_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to clean up temporary directory: {str(e)}")
    
    def get_migration_stats(self) -> Dict:
        """Get statistics about the migration process."""
        cf_stats = self.cf_client.get_upload_stats()
        progress_stats = self.progress_logger.get_stats()
        
        return {
            'cloudflare_uploads': cf_stats,
            'progress': progress_stats,
            'image_mappings': len(self.image_mapping),
            'failed_images': len(self.failed_images)
        } 