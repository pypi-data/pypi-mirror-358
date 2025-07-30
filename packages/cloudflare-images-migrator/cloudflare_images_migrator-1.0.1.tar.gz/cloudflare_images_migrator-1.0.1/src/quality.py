"""
Premium quality enhancement module for Cloudflare Images Migration Tool
"""

import io
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class QualityOptimizer:
    """Premium quality optimizer for images before upload."""
    
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        
        # Quality settings
        self.optimization_levels = {
            'conservative': {'quality': 95, 'optimize': True, 'progressive': True},
            'balanced': {'quality': 85, 'optimize': True, 'progressive': True},
            'aggressive': {'quality': 75, 'optimize': True, 'progressive': True}
        }
        
        self.default_level = getattr(config, 'optimization_level', 'balanced')
        
        # Advanced settings
        self.enable_lossless_optimization = True
        self.enable_format_conversion = True
        self.enable_responsive_variants = True
        self.max_dimension_optimization = 2048
        
        # Quality thresholds
        self.quality_thresholds = {
            'file_size_mb': 5.0,
            'dimensions': (4000, 4000),
            'compression_ratio': 0.7
        }
    
    def analyze_image_quality(self, file_path: Path) -> Dict[str, Any]:
        """
        Comprehensive image quality analysis.
        
        Returns:
            Dict with quality metrics and recommendations
        """
        analysis = {
            'quality_score': 0.0,
            'metrics': {},
            'recommendations': [],
            'optimization_potential': {},
            'estimated_savings': {}
        }
        
        try:
            with Image.open(file_path) as img:
                original_size = file_path.stat().st_size
                
                # Basic metrics
                analysis['metrics'] = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'file_size_bytes': original_size,
                    'file_size_mb': original_size / (1024 * 1024),
                    'compression_ratio': self._calculate_compression_ratio(img, original_size),
                    'color_depth': self._analyze_color_depth(img),
                    'has_transparency': self._has_transparency(img),
                    'estimated_quality': self._estimate_jpeg_quality(img, file_path)
                }
                
                # Quality scoring
                analysis['quality_score'] = self._calculate_quality_score(analysis['metrics'])
                
                # Optimization analysis
                analysis['optimization_potential'] = self._analyze_optimization_potential(img, file_path)
                
                # Size reduction estimates
                analysis['estimated_savings'] = self._estimate_savings(img, file_path)
                
                # Recommendations
                analysis['recommendations'] = self._generate_quality_recommendations(analysis)
                
        except Exception as e:
            analysis['error'] = f"Quality analysis failed: {str(e)}"
            if self.logger:
                self.logger.error(f"Quality analysis error for {file_path}: {str(e)}")
        
        return analysis
    
    def optimize_image(self, file_path: Path, output_path: Optional[Path] = None, 
                      optimization_level: str = None) -> Dict[str, Any]:
        """
        Optimize image with premium quality settings.
        
        Returns:
            Dict with optimization results
        """
        if optimization_level is None:
            optimization_level = self.default_level
        
        result = {
            'success': False,
            'original_size': 0,
            'optimized_size': 0,
            'size_reduction': 0.0,
            'quality_maintained': True,
            'optimizations_applied': [],
            'output_path': output_path or file_path
        }
        
        try:
            original_size = file_path.stat().st_size
            result['original_size'] = original_size
            
            with Image.open(file_path) as img:
                optimized_img = self._apply_optimizations(img, file_path, optimization_level)
                
                # Save optimized image
                save_path = output_path or file_path
                self._save_optimized_image(optimized_img, save_path, img.format, optimization_level)
                
                # Calculate results
                optimized_size = save_path.stat().st_size
                result['optimized_size'] = optimized_size
                result['size_reduction'] = (original_size - optimized_size) / original_size
                result['success'] = True
                
                if self.logger:
                    reduction_pct = result['size_reduction'] * 100
                    self.logger.info(f"Optimized {file_path.name}: {reduction_pct:.1f}% size reduction")
                
        except Exception as e:
            result['error'] = f"Optimization failed: {str(e)}"
            if self.logger:
                self.logger.error(f"Optimization error for {file_path}: {str(e)}")
        
        return result
    
    def create_responsive_variants(self, file_path: Path, 
                                 sizes: List[Tuple[int, int]] = None) -> List[Dict[str, Any]]:
        """
        Create responsive image variants for different screen sizes.
        
        Returns:
            List of variant creation results
        """
        if sizes is None:
            sizes = [(320, 240), (768, 576), (1024, 768), (1920, 1080)]
        
        variants = []
        
        try:
            with Image.open(file_path) as img:
                original_width, original_height = img.size
                
                for target_width, target_height in sizes:
                    # Skip if target is larger than original
                    if target_width > original_width or target_height > original_height:
                        continue
                    
                    variant_result = self._create_variant(
                        img, file_path, target_width, target_height
                    )
                    variants.append(variant_result)
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Variant creation error for {file_path}: {str(e)}")
        
        return variants
    
    def enhance_image_quality(self, file_path: Path) -> Dict[str, Any]:
        """
        Apply AI-powered quality enhancements.
        
        Returns:
            Dict with enhancement results
        """
        result = {
            'success': False,
            'enhancements_applied': [],
            'quality_improvement': 0.0
        }
        
        try:
            with Image.open(file_path) as img:
                enhanced_img = img.copy()
                
                # Auto-level adjustment
                if self._needs_level_adjustment(img):
                    enhanced_img = ImageOps.autocontrast(enhanced_img)
                    result['enhancements_applied'].append('auto_contrast')
                
                # Sharpening for web display
                if self._needs_sharpening(img):
                    enhanced_img = enhanced_img.filter(ImageFilter.UnsharpMask(
                        radius=1.0, percent=120, threshold=1
                    ))
                    result['enhancements_applied'].append('unsharp_mask')
                
                # Color enhancement
                if self._needs_color_enhancement(img):
                    enhancer = ImageEnhance.Color(enhanced_img)
                    enhanced_img = enhancer.enhance(1.1)
                    result['enhancements_applied'].append('color_enhancement')
                
                # Save enhanced image
                enhanced_img.save(file_path, quality=95, optimize=True)
                result['success'] = True
                
        except Exception as e:
            result['error'] = f"Enhancement failed: {str(e)}"
            if self.logger:
                self.logger.error(f"Enhancement error for {file_path}: {str(e)}")
        
        return result
    
    def _apply_optimizations(self, img: Image.Image, file_path: Path, 
                           optimization_level: str) -> Image.Image:
        """Apply comprehensive optimizations to image."""
        optimized = img.copy()
        settings = self.optimization_levels[optimization_level]
        
        # Format-specific optimizations
        if img.format == 'PNG':
            # PNG optimizations
            if not self._has_transparency(img) and self.enable_format_conversion:
                # Convert to RGB if no transparency needed
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    optimized = background
        
        elif img.format in ('JPEG', 'JPG'):
            # JPEG optimizations
            if img.mode != 'RGB':
                optimized = optimized.convert('RGB')
        
        # Dimension optimization
        if max(optimized.size) > self.max_dimension_optimization:
            ratio = self.max_dimension_optimization / max(optimized.size)
            new_size = tuple(int(dim * ratio) for dim in optimized.size)
            optimized = optimized.resize(new_size, Image.Resampling.LANCZOS)
        
        return optimized
    
    def _save_optimized_image(self, img: Image.Image, save_path: Path, 
                            original_format: str, optimization_level: str):
        """Save image with optimal settings."""
        settings = self.optimization_levels[optimization_level]
        
        save_kwargs = {
            'optimize': settings['optimize'],
            'quality': settings['quality']
        }
        
        if original_format == 'JPEG':
            save_kwargs.update({
                'progressive': settings['progressive'],
                'subsampling': 0  # Best quality subsampling
            })
        elif original_format == 'PNG':
            save_kwargs.update({
                'compress_level': 9,  # Maximum compression
                'optimize': True
            })
        
        img.save(save_path, **save_kwargs)
    
    def _calculate_compression_ratio(self, img: Image.Image, file_size: int) -> float:
        """Calculate current compression ratio."""
        try:
            # Estimate uncompressed size (width * height * channels * bytes_per_channel)
            channels = len(img.getbands())
            uncompressed_size = img.width * img.height * channels
            return file_size / uncompressed_size if uncompressed_size > 0 else 1.0
        except:
            return 1.0
    
    def _analyze_color_depth(self, img: Image.Image) -> Dict[str, Any]:
        """Analyze color depth and usage."""
        colors = img.getcolors(maxcolors=256*256*256)
        
        return {
            'unique_colors': len(colors) if colors else 'many',
            'mode': img.mode,
            'has_palette': hasattr(img, 'palette') and img.palette is not None
        }
    
    def _has_transparency(self, img: Image.Image) -> bool:
        """Check if image has transparency."""
        return img.mode in ('RGBA', 'LA') or 'transparency' in img.info
    
    def _estimate_jpeg_quality(self, img: Image.Image, file_path: Path) -> Optional[int]:
        """Estimate JPEG quality level."""
        if img.format != 'JPEG':
            return None
        
        try:
            # This is a simplified estimation
            # In practice, you'd use more sophisticated methods
            file_size = file_path.stat().st_size
            pixels = img.width * img.height
            bytes_per_pixel = file_size / pixels
            
            # Rough quality estimation based on bytes per pixel
            if bytes_per_pixel > 2.0:
                return 95
            elif bytes_per_pixel > 1.5:
                return 85
            elif bytes_per_pixel > 1.0:
                return 75
            elif bytes_per_pixel > 0.5:
                return 60
            else:
                return 40
        except:
            return None
    
    def _calculate_quality_score(self, metrics: Dict) -> float:
        """Calculate overall quality score (0-100)."""
        score = 100.0
        
        # File size penalty
        if metrics['file_size_mb'] > self.quality_thresholds['file_size_mb']:
            score -= 20
        
        # Dimension efficiency
        max_dimension = max(metrics['size'])
        if max_dimension > self.quality_thresholds['dimensions'][0]:
            score -= 15
        
        # Compression efficiency
        if metrics['compression_ratio'] > self.quality_thresholds['compression_ratio']:
            score -= 10
        
        # Format efficiency
        if metrics['format'] == 'BMP':
            score -= 30  # Uncompressed format
        elif metrics['format'] == 'PNG' and not metrics['has_transparency']:
            score -= 5   # Could potentially be JPEG
        
        return max(0.0, min(100.0, score))
    
    def _analyze_optimization_potential(self, img: Image.Image, file_path: Path) -> Dict:
        """Analyze potential for optimization."""
        potential = {
            'format_conversion': False,
            'dimension_reduction': False,
            'quality_reduction': False,
            'metadata_removal': False
        }
        
        # Format conversion potential
        if img.format == 'PNG' and not self._has_transparency(img):
            potential['format_conversion'] = True
        
        # Dimension reduction potential
        if max(img.size) > self.max_dimension_optimization:
            potential['dimension_reduction'] = True
        
        # Quality reduction potential
        if img.format == 'JPEG':
            estimated_quality = self._estimate_jpeg_quality(img, file_path)
            if estimated_quality and estimated_quality > 85:
                potential['quality_reduction'] = True
        
        # Metadata removal potential
        if hasattr(img, '_getexif') and img._getexif():
            potential['metadata_removal'] = True
        
        return potential
    
    def _estimate_savings(self, img: Image.Image, file_path: Path) -> Dict:
        """Estimate potential file size savings."""
        current_size = file_path.stat().st_size
        
        savings = {
            'format_conversion': 0,
            'dimension_reduction': 0,
            'quality_optimization': 0,
            'total_estimated': 0
        }
        
        # Format conversion savings (PNG to JPEG)
        if img.format == 'PNG' and not self._has_transparency(img):
            savings['format_conversion'] = current_size * 0.3  # ~30% savings
        
        # Dimension reduction savings
        if max(img.size) > self.max_dimension_optimization:
            ratio = self.max_dimension_optimization / max(img.size)
            savings['dimension_reduction'] = current_size * (1 - ratio * ratio)
        
        # Quality optimization savings
        if img.format == 'JPEG':
            estimated_quality = self._estimate_jpeg_quality(img, file_path)
            if estimated_quality and estimated_quality > 85:
                savings['quality_optimization'] = current_size * 0.15  # ~15% savings
        
        savings['total_estimated'] = sum(savings.values()) - savings['total_estimated']
        
        return savings
    
    def _generate_quality_recommendations(self, analysis: Dict) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        metrics = analysis['metrics']
        potential = analysis.get('optimization_potential', {})
        
        if potential.get('format_conversion'):
            recommendations.append('Convert PNG to JPEG for better compression (no transparency needed)')
        
        if potential.get('dimension_reduction'):
            recommendations.append(f'Reduce dimensions to max {self.max_dimension_optimization}px for web usage')
        
        if potential.get('quality_reduction'):
            recommendations.append('Reduce JPEG quality to 85% for optimal web performance')
        
        if metrics['file_size_mb'] > 2.0:
            recommendations.append('Consider aggressive optimization for files over 2MB')
        
        if analysis['quality_score'] < 70:
            recommendations.append('Multiple optimizations recommended for significant improvements')
        
        return recommendations
    
    def _create_variant(self, img: Image.Image, file_path: Path, 
                       target_width: int, target_height: int) -> Dict:
        """Create a responsive variant."""
        result = {
            'size': (target_width, target_height),
            'success': False,
            'file_path': None
        }
        
        try:
            # Calculate aspect ratio preserving resize
            img_ratio = img.width / img.height
            target_ratio = target_width / target_height
            
            if img_ratio > target_ratio:
                # Image is wider, fit to width
                new_height = int(target_width / img_ratio)
                new_size = (target_width, new_height)
            else:
                # Image is taller, fit to height
                new_width = int(target_height * img_ratio)
                new_size = (new_width, target_height)
            
            # Resize with high quality
            variant = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Generate variant filename
            stem = file_path.stem
            suffix = file_path.suffix
            variant_path = file_path.parent / f"{stem}_{target_width}x{target_height}{suffix}"
            
            # Save variant
            self._save_optimized_image(variant, variant_path, img.format, 'balanced')
            
            result['success'] = True
            result['file_path'] = variant_path
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _needs_level_adjustment(self, img: Image.Image) -> bool:
        """Check if image needs level adjustment."""
        # Simple histogram analysis
        if img.mode == 'RGB':
            histogram = img.histogram()
            # Check if histogram is heavily skewed
            total_pixels = img.width * img.height
            dark_pixels = sum(histogram[:64])  # First quarter of histogram
            return (dark_pixels / total_pixels) > 0.7
        return False
    
    def _needs_sharpening(self, img: Image.Image) -> bool:
        """Check if image needs sharpening."""
        # This is a simplified check
        # In practice, you'd analyze edge detection or Laplacian variance
        return max(img.size) > 500  # Apply sharpening to larger images
    
    def _needs_color_enhancement(self, img: Image.Image) -> bool:
        """Check if image needs color enhancement."""
        if img.mode != 'RGB':
            return False
        
        # Simple saturation check
        try:
            # Convert to HSV and check saturation
            hsv = img.convert('HSV')
            saturation_histogram = hsv.split()[1].histogram()
            avg_saturation = sum(i * saturation_histogram[i] for i in range(256)) / sum(saturation_histogram)
            return avg_saturation < 100  # Low saturation threshold
        except:
            return False


class QualityMonitor:
    """Monitor and track quality metrics across uploads."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.quality_metrics = []
        self.performance_benchmarks = {
            'optimization_time': [],
            'size_reductions': [],
            'quality_scores': []
        }
    
    def record_quality_metrics(self, file_path: Path, analysis: Dict, optimization: Dict):
        """Record quality metrics for monitoring."""
        metrics = {
            'timestamp': time.time(),
            'file_path': str(file_path),
            'original_size': analysis['metrics']['file_size_mb'],
            'quality_score': analysis['quality_score'],
            'optimization_success': optimization.get('success', False),
            'size_reduction': optimization.get('size_reduction', 0.0)
        }
        
        self.quality_metrics.append(metrics)
        self._update_benchmarks(metrics)
    
    def _update_benchmarks(self, metrics: Dict):
        """Update performance benchmarks."""
        self.performance_benchmarks['size_reductions'].append(metrics['size_reduction'])
        self.performance_benchmarks['quality_scores'].append(metrics['quality_score'])
    
    def get_quality_report(self) -> Dict:
        """Generate quality performance report."""
        if not self.quality_metrics:
            return {'message': 'No quality data available'}
        
        total_files = len(self.quality_metrics)
        successful_optimizations = sum(1 for m in self.quality_metrics if m['optimization_success'])
        
        avg_quality_score = sum(m['quality_score'] for m in self.quality_metrics) / total_files
        avg_size_reduction = sum(m['size_reduction'] for m in self.quality_metrics) / total_files
        
        return {
            'total_files_processed': total_files,
            'successful_optimizations': successful_optimizations,
            'success_rate': successful_optimizations / total_files * 100,
            'average_quality_score': avg_quality_score,
            'average_size_reduction': avg_size_reduction * 100,
            'total_data_saved_mb': sum(
                m['original_size'] * m['size_reduction'] 
                for m in self.quality_metrics
            )
        } 