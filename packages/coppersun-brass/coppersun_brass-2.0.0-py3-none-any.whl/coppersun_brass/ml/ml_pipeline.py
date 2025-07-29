"""
ML Pipeline - Efficient two-tier filtering with cost optimization

Implements:
- Quick heuristic filtering (80% of cases)
- Batch ML processing for uncertain cases
- Cost tracking and optimization
- Graceful degradation
"""
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from .quick_filter import QuickHeuristicFilter, QuickResult
from .efficient_classifier import EfficientMLClassifier
from .semantic_analyzer import SemanticAnalyzer, HAS_EMBEDDINGS
from ..core.storage import BrassStorage
from ..integrations.claude_api import ClaudeAnalyzer

logger = logging.getLogger(__name__)


class MLPipeline:
    """Efficient ML pipeline with two-tier filtering.
    
    Process:
    1. Quick heuristics catch 80% (instant)
    2. ML classification for uncertain cases
    3. Batch processing for efficiency
    4. Cost tracking for optimization
    """
    
    def __init__(self, model_dir: Path, storage: BrassStorage):
        """Initialize ML pipeline.
        
        Args:
            model_dir: Directory for ML models
            storage: Storage backend for tracking
        """
        self.storage = storage
        self.model_dir = model_dir
        
        # Initialize components
        self.quick_filter = QuickHeuristicFilter()
        self.ml_classifier = EfficientMLClassifier(model_dir)
        
        # Initialize semantic analyzer if available
        self.semantic_analyzer = None
        if HAS_EMBEDDINGS:
            self.semantic_analyzer = SemanticAnalyzer(model_dir)
            logger.info("Semantic analyzer initialized")
        
        # Initialize pre-trained adapter if available
        self.pretrained_adapter = None
        try:
            from .pretrained_adapter import PretrainedKnowledgeAdapter
            self.pretrained_adapter = PretrainedKnowledgeAdapter(model_dir)
            status = self.pretrained_adapter.get_bootstrap_status()
            if status['encoder_available'] or status['pattern_matcher_available']:
                logger.info(f"Pre-trained models initialized: {status['models_available']}")
        except Exception as e:
            logger.debug(f"Pre-trained adapter not available: {e}")
        
        # Initialize Claude analyzer
        self.claude_analyzer = ClaudeAnalyzer()
        if self.claude_analyzer.api_key:
            logger.info("Claude API initialized for validation")
        
        # Threading for ML (keep it off main async loop)
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ml_worker")
        
        # Batching configuration
        self.batch_size = 32
        self.batch_timeout = 1.0  # seconds
        self.pending_batch = []
        self.batch_lock = asyncio.Lock()
        self.batch_task = None
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'quick_filtered': 0,
            'ml_processed': 0,
            'cache_hits': 0,
            'total_time_ms': 0
        }
    
    async def process_observations(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process observations through two-tier filtering.
        
        Args:
            observations: List of observations to classify
            
        Returns:
            Classified observations with added 'classification' field
        """
        if not observations:
            return []
        
        start_time = time.time()
        results = []
        needs_ml = []
        
        # Phase 1: Quick filtering
        for obs in observations:
            self.stats['total_processed'] += 1
            
            # Quick classification
            quick_result = self.quick_filter.classify(obs)
            
            if quick_result.confidence >= 0.9:
                # Very confident - skip ML
                obs['classification'] = quick_result.label
                obs['confidence'] = quick_result.confidence
                obs['ml_used'] = False
                obs['classification_reason'] = quick_result.reason
                results.append(obs)
                self.stats['quick_filtered'] += 1
                
                logger.debug(
                    f"Quick classified {obs.get('data', {}).get('file', 'unknown')} "
                    f"as {quick_result.label} ({quick_result.confidence:.2f})"
                )
            else:
                # Uncertain - needs ML
                obs['quick_result'] = quick_result
                needs_ml.append(obs)
        
        # Phase 2: ML classification for uncertain cases
        if needs_ml:
            ml_results = await self._process_ml_batch(needs_ml)
            results.extend(ml_results)
        
        # Track timing
        elapsed_ms = (time.time() - start_time) * 1000
        self.stats['total_time_ms'] += elapsed_ms
        
        # Log statistics
        if len(observations) > 0:
            ml_percentage = (len(needs_ml) / len(observations)) * 100
            logger.info(
                f"Processed {len(observations)} observations: "
                f"{len(observations) - len(needs_ml)} quick filtered, "
                f"{len(needs_ml)} needed ML ({ml_percentage:.1f}%). "
                f"Time: {elapsed_ms:.1f}ms"
            )
        
        # Track ML usage for cost analysis
        if needs_ml:
            self._track_ml_usage(len(needs_ml), elapsed_ms)
        
        return results
    
    async def _process_ml_batch(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process observations through ML in batches.
        
        Args:
            observations: Observations needing ML classification
            
        Returns:
            Classified observations
        """
        # Add to pending batch
        async with self.batch_lock:
            self.pending_batch.extend(observations)
            
            # Process if batch is full
            if len(self.pending_batch) >= self.batch_size:
                return await self._run_ml_batch(self.pending_batch)
            
            # Otherwise, schedule batch processing
            if not self.batch_task or self.batch_task.done():
                self.batch_task = asyncio.create_task(self._batch_timeout())
        
        # For now, return observations with timeout processing
        # In production, would wait for batch completion
        return await self._wait_for_batch_results(observations)
    
    async def _batch_timeout(self):
        """Process batch after timeout."""
        await asyncio.sleep(self.batch_timeout)
        
        async with self.batch_lock:
            if self.pending_batch:
                await self._run_ml_batch(self.pending_batch)
    
    async def _run_ml_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run ML classification on a batch.
        
        Args:
            batch: Observations to classify
            
        Returns:
            Classified observations
        """
        # First, try pre-trained models if available
        if self.pretrained_adapter:
            for obs in batch:
                try:
                    # Get pre-trained analysis
                    code_content = obs.get('data', {}).get('content', '')
                    language = self._detect_language(obs.get('data', {}).get('file', ''))
                    
                    analysis = self.pretrained_adapter.analyze_code_privacy_safe(
                        code_content, 
                        language
                    )
                    
                    # Use pre-trained insights to enhance classification
                    if analysis.get('insights'):
                        quality_score = analysis['insights'].get('quality_score', 0.8)
                        pattern_matches = analysis.get('pattern_matches', [])
                        
                        # Enhance quick result with pre-trained knowledge
                        if pattern_matches:
                            # Find highest severity pattern
                            critical_patterns = [p for p in pattern_matches if p['severity'] in ['CRITICAL', 'HIGH']]
                            if critical_patterns:
                                obs['pretrained_severity'] = 'critical'
                                obs['pretrained_confidence'] = max(p['confidence'] for p in critical_patterns)
                except Exception as e:
                    logger.debug(f"Pre-trained analysis failed: {e}")
        if not batch:
            return []
        
        try:
            # Extract file paths and content
            items = []
            for obs in batch:
                data = obs.get('data', {})
                file_path = data.get('file', 'unknown')
                content = data.get('content', '')
                
                # For file changes without content, try to get from description
                if not content and 'description' in data:
                    content = data['description']
                    
                items.append((file_path, content))
            
            # Run ML classification in thread pool
            loop = asyncio.get_event_loop()
            
            # Try semantic analysis first if available
            if self.semantic_analyzer:
                ml_results = []
                for file_path, content in items:
                    try:
                        # Use semantic analyzer for intelligent classification
                        semantic_result = await loop.run_in_executor(
                            self.executor,
                            self.semantic_analyzer.analyze,
                            content,
                            {'file_path': file_path}
                        )
                        ml_results.append((semantic_result.category, semantic_result.confidence))
                    except Exception as e:
                        logger.debug(f"Semantic analysis failed, using fallback: {e}")
                        # Fallback to pattern-based classifier
                        result = self.ml_classifier.classify(file_path, content)
                        ml_results.append(result)
            else:
                # Use pattern-based classifier
                ml_results = await loop.run_in_executor(
                    self.executor,
                    self.ml_classifier.classify_batch,
                    items
                )
            
            # Update observations with ML results
            validated_results = []
            
            for obs, (label, confidence) in zip(batch, ml_results):
                logger.debug(f"ML result for {obs.get('type')}: {label} ({confidence})")
                obs['classification'] = label
                obs['confidence'] = confidence
                obs['ml_used'] = True
                
                # Combine with quick result reason if available
                quick_result = obs.pop('quick_result', None)
                if quick_result:
                    obs['classification_reason'] = f"ML confirmed: {quick_result.reason}"
                else:
                    obs['classification_reason'] = "ML classification"
                
                # Claude validation for critical findings
                if label == 'critical' and self.claude_analyzer.api_key:
                    validated_results.append((obs, (label, confidence)))
                else:
                    self.stats['ml_processed'] += 1
                
                logger.debug(
                    f"ML classified {obs.get('data', {}).get('file', 'unknown')} "
                    f"as {label} ({confidence:.2f})"
                )
            
            # Batch validate critical findings with Claude
            if validated_results:
                await self._validate_with_claude(validated_results)
            
            # Clear batch
            self.pending_batch = []
            
            return batch
            
        except Exception as e:
            logger.error(f"ML batch processing failed: {e}")
            
            # Fallback: use quick filter results
            for obs in batch:
                quick_result = obs.pop('quick_result', None)
                if quick_result:
                    obs['classification'] = quick_result.label
                    obs['confidence'] = quick_result.confidence
                else:
                    obs['classification'] = 'important'
                    obs['confidence'] = 0.5
                    
                obs['ml_used'] = False
                obs['classification_reason'] = f"ML failed, fallback: {e}"
            
            return batch
    
    async def _wait_for_batch_results(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Wait for batch processing to complete.
        
        Simplified for initial implementation - in production would properly
        track and wait for specific observations.
        """
        # For now, process immediately
        return await self._run_ml_batch(observations)
    
    def _track_ml_usage(self, batch_size: int, processing_time_ms: float):
        """Track ML usage for cost analysis.
        
        Args:
            batch_size: Number of items in batch
            processing_time_ms: Processing time in milliseconds
        """
        try:
            # Get cache statistics from classifier
            ml_stats = self.ml_classifier.get_stats()
            
            self.storage.track_ml_usage(
                batch_size=batch_size,
                model_version="codebert-small-quantized-v1",
                processing_time_ms=int(processing_time_ms),
                cache_hits=ml_stats.get('cache_hits', 0),
                cache_misses=batch_size  # Simplified
            )
            
        except Exception as e:
            logger.error(f"Failed to track ML usage: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = self.stats.copy()
        
        # Calculate rates
        if stats['total_processed'] > 0:
            stats['quick_filter_rate'] = stats['quick_filtered'] / stats['total_processed']
            stats['ml_rate'] = stats['ml_processed'] / stats['total_processed']
            stats['avg_time_ms'] = stats['total_time_ms'] / stats['total_processed']
        else:
            stats['quick_filter_rate'] = 0.0
            stats['ml_rate'] = 0.0
            stats['avg_time_ms'] = 0.0
        
        # Add component stats
        stats['quick_filter'] = self.quick_filter.get_stats()
        stats['ml_classifier'] = self.ml_classifier.get_stats()
        
        # Add pre-trained status
        if self.pretrained_adapter:
            stats['pretrained_status'] = self.pretrained_adapter.get_bootstrap_status()
        
        # Get ML usage from storage
        try:
            ml_usage = self.storage.get_ml_stats(since=datetime.utcnow().replace(hour=0, minute=0))
            stats['ml_usage_today'] = ml_usage
        except Exception as e:
            logger.error(f"Failed to get ML usage stats: {e}")
            stats['ml_usage_today'] = {}
        
        return stats
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path."""
        if not file_path:
            return 'unknown'
        
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        ext = Path(file_path).suffix.lower()
        return ext_to_lang.get(ext, 'unknown')
    
    async def _validate_with_claude(self, validated_results: List[Tuple[Dict, Tuple[str, float]]]):
        """Validate critical findings with Claude API.
        
        Args:
            validated_results: List of (observation, ml_result) tuples
        """
        logger.info(f"Validating {len(validated_results)} critical findings with Claude")
        
        for obs, ml_result in validated_results:
            try:
                # Get code content
                data = obs.get('data', {})
                content = data.get('content', data.get('snippet', ''))
                
                if not content:
                    continue
                
                # Validate with Claude
                validation = await self.claude_analyzer.validate_classification(
                    content, 
                    ml_result
                )
                
                if validation.get('validated'):
                    # Update classification based on Claude
                    obs['classification'] = validation['classification']
                    obs['confidence'] = validation['confidence']
                    obs['classification_reason'] = f"Claude validated: {validation['reason']}"
                    obs['claude_validated'] = True
                
                self.stats['ml_processed'] += 1
                
            except Exception as e:
                logger.error(f"Claude validation failed: {e}")
                self.stats['ml_processed'] += 1
    
    async def shutdown(self):
        """Clean shutdown of ML pipeline."""
        # Process any pending batches
        async with self.batch_lock:
            if self.pending_batch:
                await self._run_ml_batch(self.pending_batch)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Save ML classifier cache
        if self.ml_classifier.enabled:
            self.ml_classifier._save_cache()
        
        logger.info("ML pipeline shutdown complete")