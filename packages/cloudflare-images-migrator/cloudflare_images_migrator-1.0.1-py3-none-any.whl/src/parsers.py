"""
Image reference parsers for different file formats
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from .utils import is_url, normalize_path, safe_read_file


class ImageReference:
    """Represents an image reference found in a file."""
    
    def __init__(self, path: str, line_number: int, column: int, 
                 context: str, ref_type: str, original_text: str):
        self.path = path  # Image path or URL
        self.line_number = line_number
        self.column = column
        self.context = context  # Surrounding text for replacement
        self.ref_type = ref_type  # 'local', 'url', 'data'
        self.original_text = original_text  # Original reference text
        self.is_url = is_url(path)
    
    def __str__(self):
        return f"ImageRef({self.path}, line {self.line_number}, {self.ref_type})"
    
    def __repr__(self):
        return self.__str__()


class BaseParser:
    """Base class for image reference parsers."""
    
    def __init__(self, supported_formats: List[str]):
        self.supported_formats = [fmt.lower() for fmt in supported_formats]
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.suffix.lower() in self.supported_formats
    
    def parse(self, file_path: Path, content: str = None) -> List[ImageReference]:
        """Parse a file and extract image references."""
        raise NotImplementedError


class HTMLParser(BaseParser):
    """Parser for HTML and similar markup files."""
    
    def __init__(self):
        super().__init__(['.html', '.htm', '.xhtml', '.xml'])
    
    def parse(self, file_path: Path, content: str = None) -> List[ImageReference]:
        if content is None:
            content = safe_read_file(file_path)
            if content is None:
                return []
        
        references = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find img tags
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    line_num = self._find_line_number(content, str(img))
                    references.append(ImageReference(
                        path=src,
                        line_number=line_num,
                        column=0,
                        context=str(img),
                        ref_type='url' if is_url(src) else 'local',
                        original_text=str(img)
                    ))
            
            # Find CSS background images in style attributes
            for element in soup.find_all(attrs={'style': True}):
                style = element.get('style', '')
                css_refs = self._parse_css_urls(style)
                for ref in css_refs:
                    line_num = self._find_line_number(content, str(element))
                    references.append(ImageReference(
                        path=ref,
                        line_number=line_num,
                        column=0,
                        context=str(element),
                        ref_type='url' if is_url(ref) else 'local',
                        original_text=style
                    ))
            
            # Find inline CSS
            for style_tag in soup.find_all('style'):
                if style_tag.string:
                    css_refs = self._parse_css_urls(style_tag.string)
                    for ref in css_refs:
                        line_num = self._find_line_number(content, style_tag.string)
                        references.append(ImageReference(
                            path=ref,
                            line_number=line_num,
                            column=0,
                            context=style_tag.string,
                            ref_type='url' if is_url(ref) else 'local',
                            original_text=style_tag.string
                        ))
        
        except Exception as e:
            # Fallback to regex parsing if BeautifulSoup fails
            references = self._regex_parse(content)
        
        return references
    
    def _parse_css_urls(self, css_content: str) -> List[str]:
        """Extract URLs from CSS content."""
        url_pattern = r'url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)'
        matches = re.findall(url_pattern, css_content, re.IGNORECASE)
        return [match for match in matches if self._is_image_url(match)]
    
    def _is_image_url(self, url: str) -> bool:
        """Enhanced image URL detection - catches way more image URLs."""
        if not url or len(url.strip()) == 0:
            return False
            
        url_lower = url.lower().strip()
        
        # Traditional image extensions
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico', '.avif', '.heic']
        if any(url_lower.endswith(ext) for ext in image_extensions):
            return True
            
        # Data URLs
        if url_lower.startswith('data:image'):
            return True
            
        # Common image hosting domains and services
        image_domains = [
            'img.shields.io',           # Badge service
            'github.com',               # GitHub assets
            'githubusercontent.com',     # GitHub raw content
            'imagedelivery.net',        # Cloudflare Images
            'imgur.com',               # Imgur
            'gravatar.com',            # Gravatar
            'unsplash.com',            # Unsplash
            'pexels.com',              # Pexels
            'pixabay.com',             # Pixabay
            'jsdelivr.net',            # CDN images
            'cloudfront.net',          # AWS CloudFront
            'fastly.com',              # Fastly CDN
            'shopify.com',             # Shopify assets
            'squarespace.com',         # Squarespace assets
            'wix.com',                 # Wix assets
            'wordpress.com',           # WordPress assets
            'medium.com',              # Medium images
            'assets',                  # Generic assets path
        ]
        
        # Check if it's from known image hosting domains
        parsed_url = urlparse(url_lower)
        if parsed_url.netloc:
            for domain in image_domains:
                if domain in parsed_url.netloc:
                    return True
        
        # GitHub asset patterns (specific patterns for GitHub)
        if 'github.com' in url_lower and '/assets/' in url_lower:
            return True
        if 'githubusercontent.com' in url_lower:
            return True
            
        # Badge services (img.shields.io, badgen.net, etc.)
        badge_indicators = ['badge', 'shield', 'logo=', 'style=', 'color=']
        if any(indicator in url_lower for indicator in badge_indicators):
            return True
            
        # SVG files in URLs (often don't have .svg extension)
        if 'svg' in url_lower:
            return True
            
        # Image-like paths (contain image keywords)
        image_keywords = ['/images/', '/img/', '/pics/', '/photos/', '/assets/', '/media/', 
                         '/uploads/', '/content/', '/static/', '/public/', 'icon', 'logo', 
                         'banner', 'avatar', 'thumbnail', 'cover', 'screenshot']
        if any(keyword in url_lower for keyword in image_keywords):
            return True
            
        # URLs with image-like query parameters
        if '?' in url and any(param in url_lower for param in ['width=', 'height=', 'size=', 'format=', 'quality=']):
            return True
            
        return False
    
    def _find_line_number(self, content: str, search_text: str) -> int:
        """Find line number of text in content."""
        try:
            index = content.find(search_text)
            if index != -1:
                return content[:index].count('\n') + 1
        except Exception:
            pass
        return 1
    
    def _regex_parse(self, content: str) -> List[ImageReference]:
        """Fallback regex parsing."""
        references = []
        
        # HTML img src pattern
        img_pattern = r'<img[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>'
        for match in re.finditer(img_pattern, content, re.IGNORECASE):
            src = match.group(1)
            if self._is_image_url(src):
                line_num = content[:match.start()].count('\n') + 1
                references.append(ImageReference(
                    path=src,
                    line_number=line_num,
                    column=match.start(),
                    context=match.group(0),
                    ref_type='url' if is_url(src) else 'local',
                    original_text=match.group(0)
                ))
        
        return references


class CSSParser(BaseParser):
    """Parser for CSS files."""
    
    def __init__(self):
        super().__init__(['.css', '.scss', '.sass', '.less'])
    
    def parse(self, file_path: Path, content: str = None) -> List[ImageReference]:
        if content is None:
            content = safe_read_file(file_path)
            if content is None:
                return []
        
        references = []
        
        # URL pattern for CSS
        url_pattern = r'url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)'
        
        for match in re.finditer(url_pattern, content, re.IGNORECASE):
            url = match.group(1)
            if self._is_image_url(url):
                line_num = content[:match.start()].count('\n') + 1
                references.append(ImageReference(
                    path=url,
                    line_number=line_num,
                    column=match.start() - content.rfind('\n', 0, match.start()),
                    context=match.group(0),
                    ref_type='url' if is_url(url) else 'local',
                    original_text=match.group(0)
                ))
        
        return references
    
    def _is_image_url(self, url: str) -> bool:
        """Enhanced image URL detection - catches way more image URLs."""
        if not url or len(url.strip()) == 0:
            return False
            
        url_lower = url.lower().strip()
        
        # Traditional image extensions
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico', '.avif', '.heic']
        if any(url_lower.endswith(ext) for ext in image_extensions):
            return True
            
        # Data URLs
        if url_lower.startswith('data:image'):
            return True
            
        # Common image hosting domains and services
        image_domains = [
            'img.shields.io',           # Badge service
            'github.com',               # GitHub assets
            'githubusercontent.com',     # GitHub raw content
            'imagedelivery.net',        # Cloudflare Images
            'imgur.com',               # Imgur
            'gravatar.com',            # Gravatar
            'unsplash.com',            # Unsplash
            'pexels.com',              # Pexels
            'pixabay.com',             # Pixabay
            'jsdelivr.net',            # CDN images
            'cloudfront.net',          # AWS CloudFront
            'fastly.com',              # Fastly CDN
            'shopify.com',             # Shopify assets
            'squarespace.com',         # Squarespace assets
            'wix.com',                 # Wix assets
            'wordpress.com',           # WordPress assets
            'medium.com',              # Medium images
            'assets',                  # Generic assets path
        ]
        
        # Check if it's from known image hosting domains
        parsed_url = urlparse(url_lower)
        if parsed_url.netloc:
            for domain in image_domains:
                if domain in parsed_url.netloc:
                    return True
        
        # GitHub asset patterns (specific patterns for GitHub)
        if 'github.com' in url_lower and '/assets/' in url_lower:
            return True
        if 'githubusercontent.com' in url_lower:
            return True
            
        # Badge services (img.shields.io, badgen.net, etc.)
        badge_indicators = ['badge', 'shield', 'logo=', 'style=', 'color=']
        if any(indicator in url_lower for indicator in badge_indicators):
            return True
            
        # SVG files in URLs (often don't have .svg extension)
        if 'svg' in url_lower:
            return True
            
        # Image-like paths (contain image keywords)
        image_keywords = ['/images/', '/img/', '/pics/', '/photos/', '/assets/', '/media/', 
                         '/uploads/', '/content/', '/static/', '/public/', 'icon', 'logo', 
                         'banner', 'avatar', 'thumbnail', 'cover', 'screenshot']
        if any(keyword in url_lower for keyword in image_keywords):
            return True
            
        # URLs with image-like query parameters
        if '?' in url and any(param in url_lower for param in ['width=', 'height=', 'size=', 'format=', 'quality=']):
            return True
            
        return False


class JavaScriptParser(BaseParser):
    """Parser for JavaScript/TypeScript files."""
    
    def __init__(self):
        super().__init__(['.js', '.jsx', '.ts', '.tsx', '.mjs'])
    
    def parse(self, file_path: Path, content: str = None) -> List[ImageReference]:
        if content is None:
            content = safe_read_file(file_path)
            if content is None:
                return []
        
        references = []
        
        # String literals that might contain image paths
        patterns = [
            # Import statements
            r'import\s+.*?from\s+["\']([^"\']+\.(png|jpg|jpeg|gif|webp|svg))["\']',
            # Require statements
            r'require\s*\(\s*["\']([^"\']+\.(png|jpg|jpeg|gif|webp|svg))["\']',
            # String literals with image extensions
            r'["\']([^"\']*\.(png|jpg|jpeg|gif|webp|svg))["\']',
            # JSX img src
            r'<img[^>]+src\s*=\s*[{"\'][^}"\']*["\']([^"\']+)["\']',
            # React Image component
            r'<Image[^>]+src\s*=\s*[{"\'][^}"\']*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                # Get the image path (usually the first capture group)
                img_path = match.group(1) if match.groups() else match.group(0)
                
                if self._is_image_path(img_path):
                    line_num = content[:match.start()].count('\n') + 1
                    references.append(ImageReference(
                        path=img_path,
                        line_number=line_num,
                        column=match.start() - content.rfind('\n', 0, match.start()),
                        context=match.group(0),
                        ref_type='url' if is_url(img_path) else 'local',
                        original_text=match.group(0)
                    ))
        
        return references
    
    def _is_image_path(self, path: str) -> bool:
        """Check if path points to an image."""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico']
        path_lower = path.lower()
        return any(path_lower.endswith(ext) for ext in image_extensions)


class MarkdownParser(BaseParser):
    """Parser for Markdown files."""
    
    def __init__(self):
        super().__init__(['.md', '.markdown', '.mdown', '.mkd'])
    
    def parse(self, file_path: Path, content: str = None) -> List[ImageReference]:
        if content is None:
            content = safe_read_file(file_path)
            if content is None:
                return []
        
        references = []
        
        # Enhanced Markdown image patterns
        patterns = [
            # ![alt](image.jpg) or ![alt](any-url)
            r'!\[([^\]]*)\]\(([^)]+)\)',
            # ![alt][ref] with [ref]: image.jpg
            r'!\[([^\]]*)\]\[([^\]]+)\]',
            # HTML img tags in markdown - enhanced to catch more variations
            r'<img[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>',
            # img src= without img tag (common in HTML snippets)
            r'src\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                if pattern.startswith('!\\['):
                    # Standard markdown image
                    img_path = match.group(2)
                elif pattern.startswith('<img') or pattern.startswith('src'):
                    # HTML img tag or src attribute
                    img_path = match.group(1)
                else:
                    continue
                
                # Enhanced image detection - much more permissive
                if self._is_image_path(img_path):
                    line_num = content[:match.start()].count('\n') + 1
                    references.append(ImageReference(
                        path=img_path,
                        line_number=line_num,
                        column=match.start() - content.rfind('\n', 0, match.start()),
                        context=match.group(0),
                        ref_type='url' if is_url(img_path) else 'local',
                        original_text=match.group(0)
                    ))
        
        return references
    
    def _is_image_path(self, path: str) -> bool:
        """Enhanced image detection - catches way more image URLs."""
        if not path or len(path.strip()) == 0:
            return False
            
        path_lower = path.lower().strip()
        
        # Traditional image extensions
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico', '.avif', '.heic']
        if any(path_lower.endswith(ext) for ext in image_extensions):
            return True
            
        # Data URLs
        if path_lower.startswith('data:image'):
            return True
            
        # Common image hosting domains and services
        image_domains = [
            'img.shields.io',           # Badge service
            'github.com',               # GitHub assets
            'githubusercontent.com',     # GitHub raw content
            'imagedelivery.net',        # Cloudflare Images
            'imgur.com',               # Imgur
            'gravatar.com',            # Gravatar
            'unsplash.com',            # Unsplash
            'pexels.com',              # Pexels
            'pixabay.com',             # Pixabay
            'jsdelivr.net',            # CDN images
            'cloudfront.net',          # AWS CloudFront
            'fastly.com',              # Fastly CDN
            'shopify.com',             # Shopify assets
            'squarespace.com',         # Squarespace assets
            'wix.com',                 # Wix assets
            'wordpress.com',           # WordPress assets
            'medium.com',              # Medium images
            'assets',                  # Generic assets path
        ]
        
        # Check if it's from known image hosting domains
        parsed_url = urlparse(path_lower)
        if parsed_url.netloc:
            for domain in image_domains:
                if domain in parsed_url.netloc:
                    return True
        
        # GitHub asset patterns (specific patterns for GitHub)
        if 'github.com' in path_lower and '/assets/' in path_lower:
            return True
        if 'githubusercontent.com' in path_lower:
            return True
            
        # Badge services (img.shields.io, badgen.net, etc.)
        badge_indicators = ['badge', 'shield', 'logo=', 'style=', 'color=']
        if any(indicator in path_lower for indicator in badge_indicators):
            return True
            
        # SVG files in URLs (often don't have .svg extension)
        if 'svg' in path_lower:
            return True
            
        # Image-like paths (contain image keywords)
        image_keywords = ['/images/', '/img/', '/pics/', '/photos/', '/assets/', '/media/', 
                         '/uploads/', '/content/', '/static/', '/public/', 'icon', 'logo', 
                         'banner', 'avatar', 'thumbnail', 'cover', 'screenshot']
        if any(keyword in path_lower for keyword in image_keywords):
            return True
            
        # URLs with image-like query parameters
        if '?' in path and any(param in path_lower for param in ['width=', 'height=', 'size=', 'format=', 'quality=']):
            return True
            
        return False


class JSONParser(BaseParser):
    """Parser for JSON configuration files."""
    
    def __init__(self):
        super().__init__(['.json'])
    
    def parse(self, file_path: Path, content: str = None) -> List[ImageReference]:
        if content is None:
            content = safe_read_file(file_path)
            if content is None:
                return []
        
        references = []
        
        try:
            # Parse JSON and look for image references
            data = json.loads(content)
            self._extract_from_json(data, content, references)
        except json.JSONDecodeError:
            # Fallback to regex parsing
            pattern = r'["\']([^"\']*\.(png|jpg|jpeg|gif|webp|svg))["\']'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                img_path = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                references.append(ImageReference(
                    path=img_path,
                    line_number=line_num,
                    column=match.start() - content.rfind('\n', 0, match.start()),
                    context=match.group(0),
                    ref_type='url' if is_url(img_path) else 'local',
                    original_text=match.group(0)
                ))
        
        return references
    
    def _extract_from_json(self, data, content: str, references: List[ImageReference], path: str = ""):
        """Recursively extract image references from JSON data."""
        if isinstance(data, dict):
            for key, value in data.items():
                self._extract_from_json(value, content, references, f"{path}.{key}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._extract_from_json(item, content, references, f"{path}[{i}]")
        elif isinstance(data, str) and self._is_image_path(data):
            # Find the string in the content to get line number
            escaped_data = re.escape(data)
            pattern = f'["\']({escaped_data})["\']'
            match = re.search(pattern, content)
            if match:
                line_num = content[:match.start()].count('\n') + 1
                references.append(ImageReference(
                    path=data,
                    line_number=line_num,
                    column=match.start() - content.rfind('\n', 0, match.start()),
                    context=match.group(0),
                    ref_type='url' if is_url(data) else 'local',
                    original_text=match.group(0)
                ))
    
    def _is_image_path(self, path: str) -> bool:
        """Check if path points to an image."""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico']
        path_lower = path.lower()
        return any(path_lower.endswith(ext) for ext in image_extensions)


class ParserRegistry:
    """Registry for all image reference parsers."""
    
    def __init__(self):
        self.parsers = [
            HTMLParser(),
            CSSParser(),
            JavaScriptParser(),
            MarkdownParser(),
            JSONParser(),
        ]
    
    def get_parser(self, file_path: Path) -> Optional[BaseParser]:
        """Get appropriate parser for a file."""
        for parser in self.parsers:
            if parser.can_parse(file_path):
                return parser
        return None
    
    def parse_file(self, file_path: Path) -> List[ImageReference]:
        """Parse a file and return image references."""
        parser = self.get_parser(file_path)
        if parser:
            return parser.parse(file_path)
        return []
    
    def get_supported_extensions(self) -> Set[str]:
        """Get all supported file extensions."""
        extensions = set()
        for parser in self.parsers:
            extensions.update(parser.supported_formats)
        return extensions 