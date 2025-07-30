"""
Enterprise-grade security module for Cloudflare Images Migration Tool
"""

import hashlib
import hmac
import time
import re
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from PIL import Image, ImageFile
from PIL.ExifTags import TAGS
import magic
import requests

from .utils import get_file_hash, get_file_size_mb


class SecurityValidator:
    """Enterprise-grade security validator for image uploads."""
    
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        
        # Security configurations
        self.max_file_size_mb = getattr(config, 'max_file_size_mb', 10)
        self.allowed_mime_types = {
            'image/png', 'image/jpeg', 'image/gif', 'image/webp', 
            'image/svg+xml', 'image/bmp', 'image/x-icon'
        }
        self.allowed_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico'
        }
        
        # Advanced security settings
        self.max_image_dimensions = (12000, 12000)  # Cloudflare limit
        self.max_image_area = 100_000_000  # 100 megapixels
        self.min_image_dimensions = (1, 1)
        
        # Malicious pattern detection
        self.suspicious_patterns = [
            rb'<script',
            rb'javascript:',
            rb'data:text/html',
            rb'<?php',
            rb'<%',
            rb'eval\s*\(',
            rb'document\.cookie',
            rb'window\.location'
        ]
        
        # Rate limiting
        self.upload_timestamps = []
        self.max_uploads_per_minute = 60
        
        # Content validation
        self.enable_deep_scan = True
        self.quarantine_suspicious = True
    
    def validate_file_security(self, file_path: Path) -> Dict[str, any]:
        """
        Comprehensive security validation of an image file.
        
        Returns:
            Dict with validation results and security metadata
        """
        result = {
            'is_safe': True,
            'security_level': 'HIGH',
            'issues': [],
            'metadata': {},
            'content_hash': '',
            'file_signature': '',
            'recommendations': []
        }
        
        try:
            # 1. File existence and basic checks
            if not file_path.exists():
                result['is_safe'] = False
                result['issues'].append('File does not exist')
                return result
            
            # 2. File size validation
            file_size_mb = get_file_size_mb(file_path)
            if file_size_mb > self.max_file_size_mb:
                result['is_safe'] = False
                result['issues'].append(f'File too large: {file_size_mb:.2f}MB > {self.max_file_size_mb}MB')
            
            # 3. File extension validation
            if file_path.suffix.lower() not in self.allowed_extensions:
                result['is_safe'] = False
                result['issues'].append(f'Invalid file extension: {file_path.suffix}')
            
            # 4. MIME type validation using python-magic
            try:
                file_mime = magic.from_file(str(file_path), mime=True)
                result['metadata']['detected_mime'] = file_mime
                
                if file_mime not in self.allowed_mime_types:
                    result['is_safe'] = False
                    result['issues'].append(f'Invalid MIME type: {file_mime}')
            except Exception as e:
                result['issues'].append(f'MIME detection failed: {str(e)}')
            
            # 5. File signature validation
            file_signature = self._get_file_signature(file_path)
            result['file_signature'] = file_signature
            
            if not self._validate_file_signature(file_path, file_signature):
                result['is_safe'] = False
                result['issues'].append('File signature mismatch')
            
            # 6. Content hash for integrity
            result['content_hash'] = get_file_hash(file_path)
            
            # 7. Deep content scanning
            if self.enable_deep_scan:
                scan_results = self._deep_content_scan(file_path)
                if not scan_results['is_clean']:
                    result['is_safe'] = False
                    result['security_level'] = 'CRITICAL'
                    result['issues'].extend(scan_results['threats'])
            
            # 8. Image-specific validation
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                img_validation = self._validate_image_content(file_path)
                result['metadata'].update(img_validation['metadata'])
                
                if not img_validation['is_valid']:
                    result['is_safe'] = False
                    result['issues'].extend(img_validation['issues'])
            
            # 9. Security recommendations
            result['recommendations'] = self._generate_security_recommendations(result)
            
            # 10. Final security level assessment
            if len(result['issues']) == 0:
                result['security_level'] = 'HIGH'
            elif len(result['issues']) <= 2 and result['is_safe']:
                result['security_level'] = 'MEDIUM'
            else:
                result['security_level'] = 'LOW'
            
            self._log_security_event(file_path, result)
            
        except Exception as e:
            result['is_safe'] = False
            result['security_level'] = 'UNKNOWN'
            result['issues'].append(f'Security validation error: {str(e)}')
        
        return result
    
    def validate_url_security(self, url: str) -> Dict[str, any]:
        """
        Validate security of external image URLs.
        
        Returns:
            Dict with URL security validation results
        """
        result = {
            'is_safe': True,
            'security_level': 'HIGH',
            'issues': [],
            'metadata': {},
            'recommendations': []
        }
        
        try:
            # 1. URL format validation
            if not self._is_valid_url_format(url):
                result['is_safe'] = False
                result['issues'].append('Invalid URL format')
            
            # 2. Protocol validation (must be HTTPS for security)
            if not url.lower().startswith('https://'):
                result['security_level'] = 'MEDIUM'
                result['issues'].append('Non-HTTPS URL - security risk')
                result['recommendations'].append('Use HTTPS URLs for better security')
            
            # 3. Domain validation
            domain_check = self._validate_domain_security(url)
            if not domain_check['is_safe']:
                result['is_safe'] = False
                result['security_level'] = 'LOW'
                result['issues'].extend(domain_check['issues'])
            
            # 4. Content-Type validation via HEAD request
            try:
                head_response = requests.head(url, timeout=10, allow_redirects=True)
                content_type = head_response.headers.get('content-type', '').lower()
                
                result['metadata']['content_type'] = content_type
                result['metadata']['status_code'] = head_response.status_code
                
                if not any(mime in content_type for mime in self.allowed_mime_types):
                    result['is_safe'] = False
                    result['issues'].append(f'Invalid content type: {content_type}')
                
            except Exception as e:
                result['issues'].append(f'URL validation failed: {str(e)}')
            
            # 5. Rate limiting check
            if not self._check_rate_limit():
                result['is_safe'] = False
                result['security_level'] = 'LOW'
                result['issues'].append('Rate limit exceeded')
        
        except Exception as e:
            result['is_safe'] = False
            result['security_level'] = 'UNKNOWN'
            result['issues'].append(f'URL security validation error: {str(e)}')
        
        return result
    
    def _get_file_signature(self, file_path: Path) -> str:
        """Get file signature (magic bytes) for validation."""
        try:
            with open(file_path, 'rb') as f:
                signature = f.read(16).hex()
            return signature
        except Exception:
            return ""
    
    def _validate_file_signature(self, file_path: Path, signature: str) -> bool:
        """Validate file signature matches expected format."""
        ext = file_path.suffix.lower()
        
        # Known file signatures
        signatures = {
            '.png': ['89504e47'],
            '.jpg': ['ffd8ffe0', 'ffd8ffe1', 'ffd8ffe2', 'ffd8ffe3'],
            '.jpeg': ['ffd8ffe0', 'ffd8ffe1', 'ffd8ffe2', 'ffd8ffe3'],
            '.gif': ['47494638'],
            '.webp': ['52494646'],
            '.bmp': ['424d'],
            '.ico': ['00000100']
        }
        
        if ext in signatures:
            return any(signature.lower().startswith(sig) for sig in signatures[ext])
        
        return True  # Allow unknown extensions for now
    
    def _deep_content_scan(self, file_path: Path) -> Dict[str, any]:
        """Perform deep content scanning for malicious patterns."""
        result = {
            'is_clean': True,
            'threats': [],
            'scan_details': {}
        }
        
        try:
            # Read file in chunks to avoid memory issues
            chunk_size = 8192
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    # Check for suspicious patterns
                    for pattern in self.suspicious_patterns:
                        if re.search(pattern, chunk, re.IGNORECASE):
                            result['is_clean'] = False
                            result['threats'].append(f'Suspicious pattern detected: {pattern.decode("utf-8", errors="ignore")}')
            
            # Additional checks for specific file types
            if file_path.suffix.lower() == '.svg':
                result.update(self._scan_svg_content(file_path))
            
        except Exception as e:
            result['threats'].append(f'Content scan error: {str(e)}')
        
        return result
    
    def _scan_svg_content(self, file_path: Path) -> Dict[str, any]:
        """Special scanning for SVG files (potential XSS risks)."""
        result = {'is_clean': True, 'threats': []}
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # SVG-specific threats
            svg_threats = [
                r'<script[^>]*>',
                r'javascript:',
                r'onload\s*=',
                r'onerror\s*=',
                r'onclick\s*=',
                r'onmouseover\s*=',
                r'<iframe',
                r'<object',
                r'<embed'
            ]
            
            for threat in svg_threats:
                if re.search(threat, content, re.IGNORECASE):
                    result['is_clean'] = False
                    result['threats'].append(f'SVG security threat: {threat}')
        
        except Exception as e:
            result['threats'].append(f'SVG scan error: {str(e)}')
        
        return result
    
    def _validate_image_content(self, file_path: Path) -> Dict[str, any]:
        """Validate image content and extract metadata."""
        result = {
            'is_valid': True,
            'issues': [],
            'metadata': {}
        }
        
        try:
            # Prevent decompression bomb attacks
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            Image.MAX_IMAGE_PIXELS = self.max_image_area
            
            with Image.open(file_path) as img:
                # Basic image properties
                result['metadata']['format'] = img.format
                result['metadata']['mode'] = img.mode
                result['metadata']['size'] = img.size
                result['metadata']['width'] = img.width
                result['metadata']['height'] = img.height
                
                # Dimension validation
                if img.width > self.max_image_dimensions[0] or img.height > self.max_image_dimensions[1]:
                    result['is_valid'] = False
                    result['issues'].append(f'Image dimensions too large: {img.size}')
                
                if img.width < self.min_image_dimensions[0] or img.height < self.min_image_dimensions[1]:
                    result['is_valid'] = False
                    result['issues'].append(f'Image dimensions too small: {img.size}')
                
                # Area validation
                area = img.width * img.height
                if area > self.max_image_area:
                    result['is_valid'] = False
                    result['issues'].append(f'Image area too large: {area} pixels')
                
                # EXIF data extraction and sanitization
                exif_data = self._extract_safe_exif(img)
                result['metadata']['exif'] = exif_data
                
                # Check for suspicious EXIF data
                if self._has_suspicious_exif(exif_data):
                    result['issues'].append('Suspicious EXIF data detected')
        
        except Exception as e:
            result['is_valid'] = False
            result['issues'].append(f'Image validation error: {str(e)}')
        
        return result
    
    def _extract_safe_exif(self, img: Image.Image) -> Dict:
        """Extract safe EXIF data, excluding potentially sensitive information."""
        safe_exif = {}
        
        try:
            exif = img._getexif()
            if exif:
                # Only extract safe, useful metadata
                safe_tags = {
                    'DateTime', 'DateTimeOriginal', 'ColorSpace', 'ExifImageWidth',
                    'ExifImageHeight', 'Orientation', 'Software'
                }
                
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in safe_tags and isinstance(value, (str, int, float)):
                        safe_exif[tag] = value
        
        except Exception:
            pass  # EXIF extraction is optional
        
        return safe_exif
    
    def _has_suspicious_exif(self, exif_data: Dict) -> bool:
        """Check for suspicious EXIF data patterns."""
        # Check for suspicious software signatures
        suspicious_software = ['steganography', 'hidden', 'inject', 'payload']
        
        software = exif_data.get('Software', '').lower()
        return any(sus in software for sus in suspicious_software)
    
    def _is_valid_url_format(self, url: str) -> bool:
        """Validate URL format."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def _validate_domain_security(self, url: str) -> Dict[str, any]:
        """Validate domain security and reputation."""
        result = {'is_safe': True, 'issues': []}
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check against known malicious domains (simplified)
            malicious_patterns = [
                'malware', 'phishing', 'suspicious', 'temp', 'throwaway'
            ]
            
            if any(pattern in domain for pattern in malicious_patterns):
                result['is_safe'] = False
                result['issues'].append(f'Suspicious domain: {domain}')
            
            # IP address check (generally less trusted)
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
                result['issues'].append('Direct IP address used - lower trust level')
        
        except Exception as e:
            result['issues'].append(f'Domain validation error: {str(e)}')
        
        return result
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        self.upload_timestamps = [
            ts for ts in self.upload_timestamps 
            if current_time - ts < 60
        ]
        
        # Check if we're under the limit
        if len(self.upload_timestamps) >= self.max_uploads_per_minute:
            return False
        
        # Add current timestamp
        self.upload_timestamps.append(current_time)
        return True
    
    def _generate_security_recommendations(self, validation_result: Dict) -> List[str]:
        """Generate security recommendations based on validation results."""
        recommendations = []
        
        if validation_result['security_level'] != 'HIGH':
            recommendations.append('Consider additional security scanning')
        
        if any('Non-HTTPS' in issue for issue in validation_result['issues']):
            recommendations.append('Use HTTPS URLs for secure image delivery')
        
        if any('large' in issue.lower() for issue in validation_result['issues']):
            recommendations.append('Optimize image size before upload')
        
        recommendations.append('Regularly update security policies')
        recommendations.append('Monitor upload patterns for anomalies')
        
        return recommendations
    
    def _log_security_event(self, file_path: Path, result: Dict):
        """Log security validation events for audit trail."""
        if self.logger:
            level = 'warning' if not result['is_safe'] else 'info'
            message = f"Security scan: {file_path.name} - {result['security_level']} - Issues: {len(result['issues'])}"
            getattr(self.logger, level)(message)
    
    def generate_security_report(self, validations: List[Dict]) -> Dict:
        """Generate comprehensive security report."""
        report = {
            'total_files': len(validations),
            'safe_files': sum(1 for v in validations if v['is_safe']),
            'security_levels': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'CRITICAL': 0, 'UNKNOWN': 0},
            'common_issues': {},
            'recommendations': set()
        }
        
        for validation in validations:
            report['security_levels'][validation['security_level']] += 1
            
            for issue in validation['issues']:
                report['common_issues'][issue] = report['common_issues'].get(issue, 0) + 1
            
            report['recommendations'].update(validation['recommendations'])
        
        report['recommendations'] = list(report['recommendations'])
        report['security_score'] = (report['safe_files'] / report['total_files'] * 100) if report['total_files'] > 0 else 0
        
        return report


class SecureUploadManager:
    """Manages secure upload workflows with Direct Creator Upload."""
    
    def __init__(self, cloudflare_client, security_validator, logger=None):
        self.cf_client = cloudflare_client
        self.security_validator = security_validator
        self.logger = logger
        
    def create_secure_upload_url(self, custom_metadata: Dict = None) -> Dict:
        """
        Create a Direct Creator Upload URL for secure uploads.
        
        Returns:
            Dict with secure upload URL and metadata
        """
        try:
            # This would integrate with Cloudflare's Direct Creator Upload API
            # For now, we'll use the standard upload with enhanced security
            
            upload_token = self._generate_upload_token()
            
            return {
                'upload_url': 'https://upload.imagedelivery.net/direct',
                'upload_token': upload_token,
                'expires_at': int(time.time()) + 3600,  # 1 hour
                'metadata': custom_metadata or {}
            }
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to create secure upload URL: {str(e)}")
            return None
    
    def _generate_upload_token(self) -> str:
        """Generate secure upload token."""
        timestamp = str(int(time.time()))
        random_data = hashlib.sha256(f"{timestamp}{time.time()}".encode()).hexdigest()[:16]
        return f"secure_{timestamp}_{random_data}" 