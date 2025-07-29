"""
Output Generator for Copper Alloy Brass

Generates JSON output files for Claude Code to read.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from coppersun_brass.core.storage import BrassStorage
from coppersun_brass.config import BrassConfig

logger = logging.getLogger(__name__)


class OutputGenerator:
    """Generates structured output files for AI consumption."""
    
    def __init__(self, config: BrassConfig, storage: BrassStorage):
        """
        Initialize output generator.
        
        Args:
            config: Copper Alloy Brass configuration
            storage: Storage instance
        """
        self.config = config
        self.storage = storage
        self.output_dir = config.output_dir
        
    def generate_analysis_report(self) -> Path:
        """
        Generate comprehensive analysis report.
        
        Returns:
            Path to generated report file
        """
        # Get all observations
        observations = self.storage.get_all_observations()
        
        # Group by type
        grouped = {}
        for obs in observations:
            obs_type = obs['type']
            if obs_type not in grouped:
                grouped[obs_type] = []
            grouped[obs_type].append(obs)
        
        # Create report structure
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'project_path': str(self.config.project_root),
                'total_observations': len(observations),
                'brass_version': '1.0.0'
            },
            'summary': {
                'total_todos': len(grouped.get('todo', [])),
                'total_files_analyzed': len(grouped.get('scout_analysis_summary', [])),
                'critical_issues': self._count_critical_issues(observations),
                'by_type': {k: len(v) for k, v in grouped.items()}
            },
            'todos': self._format_todos(grouped.get('todo', [])),
            'issues': self._format_issues(observations),
            'file_summaries': self._format_file_summaries(grouped.get('scout_analysis_summary', []))
        }
        
        # Write report
        report_path = self.output_dir / 'analysis_report.json'
        report_path.write_text(json.dumps(report, indent=2))
        logger.info(f"Generated analysis report: {report_path}")
        
        return report_path
    
    def generate_todo_list(self) -> Path:
        """
        Generate a focused TODO list.
        
        Returns:
            Path to generated TODO file
        """
        # Get only recent TODOs from the last 24 hours to avoid duplicates
        # from multiple runs
        since = datetime.now() - timedelta(hours=24)
        todos = self.storage.get_observations(obs_type='todo', since=since)
        
        # Deduplicate TODOs by file+line+content
        seen = set()
        unique_todos = []
        for todo in todos:
            data = todo.get('data', {})
            key = (data.get('file', ''), data.get('line', 0), data.get('content', ''))
            if key not in seen:
                seen.add(key)
                unique_todos.append(todo)
        
        # Sort by priority
        unique_todos.sort(key=lambda x: x.get('priority', 50), reverse=True)
        
        todo_list = {
            'generated_at': datetime.now().isoformat(),
            'total_todos': len(unique_todos),
            'todos': [
                {
                    'file': todo.get('data', {}).get('file', 'unknown'),
                    'line': todo.get('data', {}).get('line', 0),
                    'content': todo.get('data', {}).get('content', ''),
                    'priority': todo.get('priority', 50),
                    'classification': todo.get('data', {}).get('classification', 'unclassified')
                }
                for todo in unique_todos
            ]
        }
        
        # Write TODO list
        todo_path = self.output_dir / 'todos.json'
        todo_path.write_text(json.dumps(todo_list, indent=2))
        logger.info(f"Generated TODO list: {todo_path}")
        
        return todo_path
    
    def generate_project_context(self) -> Path:
        """
        Generate project context information.
        
        Returns:
            Path to generated context file
        """
        # Get statistics
        stats = self.storage.get_activity_stats()
        
        context = {
            'project': {
                'path': str(self.config.project_root),
                'name': self.config.project_root.name,
                'analyzed_at': datetime.now().isoformat()
            },
            'statistics': {
                'files_analyzed': stats.get('files_analyzed', 0),
                'total_observations': stats.get('total_observations', 0),
                'critical_issues': stats.get('critical_count', 0),
                'important_issues': stats.get('important_count', 0)
            },
            'recent_activity': {
                'last_24h': stats
            }
        }
        
        # Write context
        context_path = self.output_dir / 'project_context.json'
        context_path.write_text(json.dumps(context, indent=2))
        logger.info(f"Generated project context: {context_path}")
        
        return context_path
    
    def _count_critical_issues(self, observations: List[Dict]) -> int:
        """Count critical issues from observations."""
        return sum(
            1 for obs in observations
            if obs.get('data', {}).get('classification') == 'critical'
        )
    
    def _format_todos(self, todos: List[Dict]) -> List[Dict]:
        """Format TODO observations for report."""
        formatted = []
        for todo in todos:
            data = todo.get('data', {})
            formatted.append({
                'file': data.get('file', 'unknown'),
                'line': data.get('line', 0),
                'content': data.get('content', ''),
                'priority': todo.get('priority', 50),
                'classification': data.get('classification', 'unclassified'),
                'ml_confidence': data.get('ml_confidence', 0.0)
            })
        return sorted(formatted, key=lambda x: x['priority'], reverse=True)
    
    def _format_issues(self, observations: List[Dict]) -> List[Dict]:
        """Format critical and important issues."""
        issues = []
        for obs in observations:
            data = obs.get('data', {})
            classification = data.get('classification', '')
            
            if classification in ['critical', 'important']:
                issues.append({
                    'type': obs.get('type'),
                    'severity': classification,
                    'file': data.get('file', 'unknown'),
                    'description': data.get('content', data.get('summary', '')),
                    'confidence': data.get('ml_confidence', 0.0)
                })
        
        return sorted(issues, key=lambda x: (
            0 if x['severity'] == 'critical' else 1,
            -x['confidence']
        ))
    
    def _format_file_summaries(self, summaries: List[Dict]) -> List[Dict]:
        """Format file analysis summaries."""
        formatted = []
        for summary in summaries:
            data = summary.get('data', {})
            formatted.append({
                'file': data.get('file_path', 'unknown'),
                'analyzed_at': summary.get('created_at', ''),
                'summary': data.get('summary', {}),
                'has_issues': data.get('total_issues', 0) > 0
            })
        return formatted
    
    def generate_all_outputs(self) -> Dict[str, Path]:
        """
        Generate all output files.
        
        Returns:
            Dictionary mapping output type to file path
        """
        outputs = {}
        
        try:
            outputs['analysis_report'] = self.generate_analysis_report()
            outputs['todo_list'] = self.generate_todo_list()
            outputs['project_context'] = self.generate_project_context()
            
            logger.info(f"Generated {len(outputs)} output files in {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to generate outputs: {e}")
        
        return outputs