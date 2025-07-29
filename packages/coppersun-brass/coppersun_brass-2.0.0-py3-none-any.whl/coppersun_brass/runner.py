"""
Copper Alloy Brass Runner - Async orchestration without subprocess overhead

Key improvements:
- Direct imports instead of subprocess
- Async execution for better performance
- Graceful error handling
- Resource management
"""
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import importlib.util

from .config import BrassConfig
from .core.storage import BrassStorage
from .core.dcp_adapter import DCPAdapter
from .ml.ml_pipeline import MLPipeline

# Import agents directly - no subprocess!
from .agents.scout.scout_agent import ScoutAgent
from .agents.watch.watch_agent import WatchAgent
from .agents.strategist.strategist_agent import StrategistAgent
from .agents.planner.task_generator import TaskGenerator

# Import learning system
from .core.learning.training_coordinator import TrainingCoordinator
from .core.learning.project_learner import ProjectLearner
from .core.output_generator import OutputGenerator

logger = logging.getLogger(__name__)


class BrassRunner:
    """Efficient async runner for Copper Alloy Brass agents.
    
    Replaces subprocess-based execution with direct imports:
    - 10x faster startup
    - Shared memory/cache
    - Better error handling
    - No serialization overhead
    """
    
    def __init__(self, config: BrassConfig):
        """Initialize runner with configuration.
        
        Args:
            config: Copper Alloy Brass configuration
        """
        self.config = config
        self.project_root = config.project_root
        
        # Initialize storage
        self.storage = BrassStorage(config.data_dir / "coppersun_brass.db")
        
        # Initialize DCP adapter for agents
        self.dcp = DCPAdapter(self.storage, self.project_root)
        
        # Initialize ML pipeline
        self.ml_pipeline = MLPipeline(
            config.data_dir / 'models',
            self.storage
        )
        
        # Initialize training coordinator
        self.training_coordinator = TrainingCoordinator(
            dcp_path=str(self.project_root / '.brass'),
            config=config,
            team_id=None  # Can be configured later
        )
        self.last_training_check = datetime.now()
        self.training_check_interval = timedelta(hours=1)
        
        # Initialize project learner for first-run training
        self.project_learner = ProjectLearner(
            dcp_path=str(self.project_root / '.brass')
        )
        
        # Agent instances (lazy loaded)
        self.agents: Dict[str, Any] = {}
        self.running_agents: Set[asyncio.Task] = set()
        
        # Shutdown handling
        self.shutdown_event = asyncio.Event()
        self._setup_signal_handlers()
        
        # Performance tracking
        self.stats = {
            'runs': 0,
            'errors': 0,
            'total_observations': 0,
            'avg_run_time_ms': 0,
            'training_runs': 0
        }
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, initiating shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize_agents(self):
        """Initialize agent instances."""
        logger.info("Initializing agents...")
        
        try:
            # Scout agent - code analysis
            self.agents['scout'] = ScoutAgent(
                dcp_path=str(self.project_root / '.brass'),
                project_root=self.project_root
            )
            
            # Watch agent - file monitoring
            self.agents['watch'] = WatchAgent({
                'project_path': str(self.project_root),
                'dcp_path': str(self.project_root / '.brass'),
                'analysis_interval': 300  # 5 minutes
            })
            
            # Strategist agent - orchestration and prioritization
            self.agents['strategist'] = StrategistAgent(
                project_path=str(self.project_root),
                dcp_path=str(self.project_root / '.brass'),
                config={}
            )
            
            # Planner agent - task generation and planning
            self.agents['planner'] = TaskGenerator(
                dcp_manager=self.dcp
            )
            
            logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def run_scout_analysis(self) -> List[Dict[str, Any]]:
        """Run Scout agent analysis.
        
        Returns:
            List of observations from Scout
        """
        start_time = asyncio.get_event_loop().time()
        observations = []
        
        try:
            scout = self.agents.get('scout')
            if not scout:
                logger.warning("Scout agent not initialized")
                return []
            
            logger.info("Running Scout analysis...")
            
            # Get files to analyze
            files_to_analyze = await self._get_changed_files()
            
            logger.info(f"Scout will analyze {len(files_to_analyze)} files")
            
            if not files_to_analyze:
                logger.info("No files to analyze")
                return []
            
            # Run analysis
            for file_path in files_to_analyze:
                try:
                    # Scout's analyze method
                    result = await asyncio.to_thread(
                        scout.analyze,
                        str(file_path),
                        deep_analysis=False  # Just TODO analysis for now
                    )
                    
                    if result:
                        # Debug logging
                        logger.info(f"Scout analyzed {file_path}: {len(result.todo_findings)} TODOs found")
                        
                        # Convert ScoutAnalysisResult to observations
                        obs = result.to_dcp_observations()
                        observations.extend(obs)
                        
                        # Convert TODO findings to observations with proper data structure
                        for finding in result.todo_findings:
                            observations.append({
                                'type': 'todo',
                                'data': {
                                    'file': finding.file_path,
                                    'line': finding.line_number,
                                    'content': finding.content,
                                },
                                'summary': f"TODO in {Path(finding.file_path).name}: {finding.content[:50]}...",
                                'priority': finding.priority_score
                            })
                        
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {e}")
                    self.stats['errors'] += 1
            
            # Process through ML pipeline
            if observations:
                logger.info(f"Sending {len(observations)} observations to ML pipeline")
                processed_observations = await self.ml_pipeline.process_observations(observations)
                logger.info(f"ML pipeline returned {len(processed_observations)} observations")
                observations = processed_observations
            
            # Check if this is first run and trigger project learning
            is_first_run = self.storage.get_last_analysis_time() is None
            if is_first_run and observations:
                logger.info("First run detected - project learning temporarily disabled")
                # TODO: Fix project learner DCP integration
                # await self.project_learner.learn_from_initial_analysis(observations)
            
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.info(
                f"Scout analysis complete: {len(observations)} observations "
                f"in {elapsed_ms:.1f}ms"
            )
            
            # Update stats
            self.stats['runs'] += 1
            self.stats['total_observations'] += len(observations)
            self._update_avg_time(elapsed_ms)
            
            logger.info(f"Returning {len(observations)} observations from Scout")
            return observations
            
        except Exception as e:
            logger.error(f"Scout analysis failed: {e}", exc_info=True)
            self.stats['errors'] += 1
            return []
    
    async def run_watch_monitoring(self):
        """Run Watch agent for continuous monitoring."""
        try:
            watch = self.agents.get('watch')
            if not watch:
                logger.warning("Watch agent not initialized")
                return
            
            logger.info("Starting Watch monitoring...")
            
            # Create watch task
            watch_task = asyncio.create_task(
                self._run_watch_loop(watch)
            )
            self.running_agents.add(watch_task)
            
            # Remove from set when done
            watch_task.add_done_callback(self.running_agents.discard)
            
        except Exception as e:
            logger.error(f"Failed to start Watch monitoring: {e}")
            self.stats['errors'] += 1
    
    async def _run_watch_loop(self, watch_agent):
        """Run watch agent monitoring loop."""
        while not self.shutdown_event.is_set():
            try:
                # Check for file changes
                changes = await asyncio.to_thread(
                    watch_agent.check_changes
                )
                
                if changes:
                    # Process through ML pipeline
                    processed = await self.ml_pipeline.process_observations(changes)
                    
                    # Store high-priority observations
                    for obs in processed:
                        if obs.get('classification') in ['critical', 'important']:
                            self.storage.add_observation(
                                obs_type='file_change',
                                data=obs['data'],
                                source_agent='watch',
                                priority=obs.get('priority', 50),
                                metadata={
                                    'classification': obs['classification'],
                                    'confidence': obs['confidence']
                                }
                            )
                    
                    self.stats['total_observations'] += len(changes)
                
                # Wait before next check
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
                self.stats['errors'] += 1
                await asyncio.sleep(10.0)  # Back off on error
    
    async def _get_changed_files(self) -> List[Path]:
        """Get list of files that need analysis.
        
        Returns:
            List of file paths to analyze
        """
        try:
            # Get files modified since last run
            last_run = self.storage.get_last_analysis_time()
            
            if not last_run:
                logger.info(f"First run - analyzing all files in {self.project_root}")
                # First run - analyze all Python files
                files = list(self.project_root.rglob("*.py"))
                # Add other important file types
                files.extend(self.project_root.rglob("*.js"))
                files.extend(self.project_root.rglob("*.ts"))
                logger.info(f"Found {len(files)} files before filtering")
            else:
                # Check all files but only analyze those that changed
                logger.info(f"Incremental run - checking for modified files in {self.project_root}")
                all_files = list(self.project_root.rglob("*.py"))
                all_files.extend(self.project_root.rglob("*.js"))
                all_files.extend(self.project_root.rglob("*.ts"))
                
                # Filter to only changed files
                files = []
                for f in all_files:
                    if not self._should_ignore(f) and self.storage.should_analyze_file(f):
                        files.append(f)
                
                logger.info(f"Found {len(files)} modified files out of {len(all_files)} total")
            
            # Filter out ignored paths
            files = [f for f in files if not self._should_ignore(f)]
            logger.info(f"After filtering: {len(files)} files to analyze")
            
            # Limit batch size for memory
            max_batch = 20  # Reasonable batch size
            if len(files) > max_batch:
                logger.warning(f"Limiting analysis to {max_batch} files (found {len(files)})")
                files = files[:max_batch]
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            return []
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        path_str = str(path)
        
        # Check against config ignore patterns
        for pattern in self.config.ignored_dirs:
            if pattern in path_str:
                return True
        
        # Check file patterns
        for pattern in self.config.ignored_files:
            if path.name == pattern or path.match(pattern):
                return True
        
        # Check common ignore patterns
        ignore_dirs = {
            '__pycache__', '.git', 'node_modules', 
            '.pytest_cache', '.mypy_cache', 'venv',
            'dist', 'build', '.egg-info'
        }
        
        parts = path.parts
        return any(part in ignore_dirs for part in parts)
    
    def _update_avg_time(self, time_ms: float):
        """Update average run time."""
        current_avg = self.stats['avg_run_time_ms']
        runs = self.stats['runs']
        
        # Weighted average
        self.stats['avg_run_time_ms'] = (
            (current_avg * (runs - 1) + time_ms) / runs
        )
    
    async def run_once(self):
        """Run all agents once (for scheduled execution)."""
        logger.info("Starting Copper Alloy Brass analysis run...")
        
        try:
            # Initialize agents if needed
            if not self.agents:
                await self.initialize_agents()
            
            # Run Scout analysis
            observations = await self.run_scout_analysis()
            
            # Pass observations through Strategist for prioritization
            if 'strategist' in self.agents and observations:
                try:
                    logger.info(f"Sending {len(observations)} observations to Strategist")
                    strategist = self.agents['strategist']
                    # Prioritize observations through Strategist
                    prioritized = await asyncio.to_thread(
                        strategist.prioritize_observations,
                        observations
                    )
                    
                    # Update observations with priority scores
                    if prioritized:
                        observations = prioritized
                        logger.info(f"Strategist prioritized {len(observations)} observations")
                    else:
                        logger.warning(f"Strategist returned no prioritized observations")
                except Exception as e:
                    logger.error(f"Strategist orchestration failed: {e}")
            
            # Generate tasks through Planner
            if 'planner' in self.agents and observations:
                try:
                    planner = self.agents['planner']
                    # Convert observations to tasks
                    tasks = await asyncio.to_thread(
                        planner.generate_tasks_from_observations,
                        observations
                    )
                    
                    if tasks:
                        logger.info(f"Planner generated {len(tasks)} tasks")
                        # Store tasks in DCP for future use
                        # TODO: Implement task storage
                except Exception as e:
                    logger.error(f"Planner task generation failed: {e}")
            
            # Store observations
            logger.info(f"About to store {len(observations)} observations")
            stored_count = 0
            for obs in observations:
                try:
                    # Extract observation data
                    obs_type = obs.get('type', 'unknown')
                    obs_data = obs.get('data', obs)  # Use whole obs if no data field
                    priority = obs.get('priority', 50)
                    
                    # Store in database
                    obs_id = self.storage.add_observation(
                        obs_type=obs_type,
                        data={
                            **obs_data,
                            'classification': obs.get('classification', 'unclassified'),
                            'ml_confidence': obs.get('confidence', 0.0)
                        },
                        source_agent='scout',
                        priority=priority
                    )
                    
                    if obs_id:
                        stored_count += 1
                    
                    # Log critical/important findings
                    if obs.get('classification') in ['critical', 'important']:
                        logger.info(
                            f"Found {obs['classification']} issue in "
                            f"{obs.get('file', 'unknown')}: "
                            f"{obs.get('content', obs.get('classification_reason', 'No details'))}"
                        )
                except Exception as e:
                    logger.error(f"Failed to store observation: {e}")
            
            logger.info(f"Stored {stored_count} of {len(observations)} observations")
            
            # Update last run time
            self.storage.update_last_analysis_time()
            
            # Generate output files for Claude Code
            if stored_count > 0:
                try:
                    output_gen = OutputGenerator(self.config, self.storage)
                    outputs = output_gen.generate_all_outputs()
                    logger.info(f"Generated {len(outputs)} output files in {self.config.output_dir}")
                except Exception as e:
                    logger.error(f"Failed to generate output files: {e}")
            
            # Generate summary
            summary = self._generate_summary(observations)
            if summary:
                logger.info(f"Run summary: {summary}")
            
            # Check if training is needed
            await self._check_and_train()
            
        except Exception as e:
            logger.error(f"Run failed: {e}")
            self.stats['errors'] += 1
    
    async def run_continuous(self):
        """Run agents continuously with Watch monitoring."""
        logger.info("Starting continuous Copper Alloy Brass monitoring...")
        
        try:
            # Initialize agents
            if not self.agents:
                await self.initialize_agents()
            
            # Start Watch monitoring
            await self.run_watch_monitoring()
            
            # Run Scout periodically
            while not self.shutdown_event.is_set():
                await self.run_once()
                
                # Wait for next run (configurable)
                wait_time = self.config.get('run_interval', 300)  # Default 5 minutes
                await asyncio.sleep(wait_time)
            
        except Exception as e:
            logger.error(f"Continuous run failed: {e}")
        finally:
            await self.shutdown()
    
    async def _check_and_train(self):
        """Check if training is needed and run if so."""
        # Only check periodically
        now = datetime.now()
        if now - self.last_training_check < self.training_check_interval:
            return
        
        self.last_training_check = now
        
        try:
            # Check and train if needed
            result = await self.training_coordinator.check_and_train()
            
            if result:
                self.stats['training_runs'] += 1
                logger.info(f"Training completed: {result.get('phases', {}).get('model_training', {}).get('models_trained', [])}")
        except Exception as e:
            logger.error(f"Training check failed: {e}")
    
    def _generate_summary(self, observations: List[Dict[str, Any]]) -> str:
        """Generate run summary for logging."""
        if not observations:
            return ""
        
        # Count by classification
        counts = {'critical': 0, 'important': 0, 'trivial': 0}
        for obs in observations:
            classification = obs.get('classification', 'unknown')
            if classification in counts:
                counts[classification] += 1
        
        # Build summary
        parts = []
        if counts['critical'] > 0:
            parts.append(f"{counts['critical']} critical")
        if counts['important'] > 0:
            parts.append(f"{counts['important']} important")
        if counts['trivial'] > 0:
            parts.append(f"{counts['trivial']} trivial")
        
        return f"Found {', '.join(parts)} observations"
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down Copper Alloy Brass runner...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Cancel running tasks
        for task in self.running_agents:
            task.cancel()
        
        # Wait for tasks to complete
        if self.running_agents:
            await asyncio.gather(*self.running_agents, return_exceptions=True)
        
        # Shutdown ML pipeline
        await self.ml_pipeline.shutdown()
        
        # Log final stats
        logger.info(f"Final stats: {self.stats}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get runner statistics."""
        stats = self.stats.copy()
        
        # Add component stats
        stats['ml_pipeline'] = self.ml_pipeline.get_stats()
        stats['storage'] = {
            'total_observations': self.storage.get_observation_count()
        }
        
        # Add training stats
        stats['training'] = self.training_coordinator.get_training_status()
        
        return stats