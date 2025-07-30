"""
Claude API Integration - Real AI-powered code analysis

Uses Claude for deep semantic understanding and validation.
"""
import os
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import hashlib

logger = logging.getLogger(__name__)

# Try to import dotenv for better .env handling
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    logger.debug("python-dotenv not installed - using manual .env parsing")

try:
    from anthropic import Anthropic, AsyncAnthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logger.warning("anthropic not installed - Claude API unavailable")


class ClaudeAnalyzer:
    """Real Claude API integration for intelligent code analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude analyzer.
        
        Args:
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)
        """
        # Try to load from .env if not provided
        if not api_key and not os.getenv('ANTHROPIC_API_KEY'):
            self._load_from_env()
        
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        self.async_client = None
        self.cache_dir = Path.home() / '.brass' / 'claude_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load config
        ml_config_path = Path.home() / '.brass' / 'ml_config.json'
        if ml_config_path.exists():
            with open(ml_config_path) as f:
                config = json.load(f)
                self.config = config.get('claude_api', {})
                # Ensure required fields have defaults
                self.config.setdefault('model', 'claude-3-haiku-20240307')
                self.config.setdefault('max_tokens', 1000)
                self.config.setdefault('temperature', 0.3)
        else:
            self.config = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 1000,
                'temperature': 0.3
            }
        
        if self.api_key and HAS_ANTHROPIC:
            # Basic validation - Anthropic keys start with sk-ant-
            if self.api_key.startswith('sk-ant-') and len(self.api_key) > 40:
                self._initialize_client()
            else:
                logger.warning("Invalid Claude API key format")
                self.api_key = None
        else:
            logger.warning("Claude API not configured")
    
    def _load_from_env(self):
        """Load API key from .env file."""
        if HAS_DOTENV:
            # Use python-dotenv for proper parsing
            env_files = [
                Path.cwd() / '.env',
                Path.cwd().parent / '.env',  # Check parent directory
                Path.home() / '.brass' / '.env'
            ]
            
            for env_path in env_files:
                if env_path.exists():
                    logger.debug(f"Checking .env file: {env_path}")
                    load_dotenv(env_path, override=True)
                    if os.getenv('ANTHROPIC_API_KEY'):
                        logger.info(f"Loaded API key from {env_path}")
                        return
        else:
            # Fallback to manual parsing
            env_files = [
                Path.cwd() / '.env',
                Path.cwd().parent / '.env',  # Check parent directory
                Path.home() / '.brass' / '.env'
            ]
            
            for env_path in env_files:
                if env_path.exists():
                    logger.debug(f"Manually parsing .env file: {env_path}")
                    with open(env_path) as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('ANTHROPIC_API_KEY='):
                                key_value = line.split('=', 1)[1]
                                api_key = key_value.strip('"\'')
                                os.environ['ANTHROPIC_API_KEY'] = api_key
                                logger.info(f"Loaded API key from {env_path}")
                                return
        
        logger.debug("No .env file found with ANTHROPIC_API_KEY")
    
    def _initialize_client(self):
        """Initialize Claude client."""
        try:
            self.client = Anthropic(api_key=self.api_key)
            self.async_client = AsyncAnthropic(api_key=self.api_key)
            logger.info("Claude API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude API: {e}")
    
    async def analyze_code(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code using Claude for deep understanding.
        
        Args:
            code: Code snippet to analyze
            context: Additional context (file path, surrounding code, etc.)
            
        Returns:
            Analysis results with classification and insights
        """
        if not self.async_client:
            return self._fallback_analysis(code, context)
        
        # Check cache first
        cache_key = self._get_cache_key(code, context)
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Prepare prompt
            prompt = self._create_analysis_prompt(code, context)
            
            # Call Claude API
            response = await self.async_client.messages.create(
                model=self.config['model'],
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature'],
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            result = self._parse_claude_response(response.content[0].text)
            
            # Add metadata
            result['api_model'] = self.config['model']
            result['timestamp'] = datetime.utcnow().isoformat()
            result['confidence'] = self._calculate_confidence(result)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            return self._fallback_analysis(code, context)
    
    async def validate_classification(self, code: str, ml_result: Tuple[str, float]) -> Dict[str, Any]:
        """Use Claude to validate ML classification for critical findings.
        
        Args:
            code: Code that was classified
            ml_result: (category, confidence) from ML
            
        Returns:
            Validation result with confirmed classification
        """
        if not self.async_client:
            return {
                'validated': False,
                'original': ml_result,
                'reason': 'Claude API not available'
            }
        
        category, confidence = ml_result
        
        # Only validate critical findings or low confidence
        if category != 'critical' and confidence > 0.8:
            return {
                'validated': True,
                'classification': category,
                'confidence': confidence,
                'reason': 'High confidence non-critical'
            }
        
        try:
            prompt = f"""
Please validate this code classification:

Code:
```
{code[:500]}  # Truncate for token limits
```

ML Classification: {category} (confidence: {confidence:.2%})

Is this classification correct? If not, what should it be?
Respond with JSON: {{"correct": bool, "category": "critical/important/trivial", "reason": "explanation"}}
"""
            
            response = await self.async_client.messages.create(
                model=self.config['model'],
                max_tokens=200,
                temperature=0.1,  # Low temp for consistency
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            try:
                validation = json.loads(response.content[0].text)
                return {
                    'validated': True,
                    'classification': validation.get('category', category),
                    'confidence': 0.95 if validation.get('correct') else confidence,
                    'reason': validation.get('reason', 'Claude validated'),
                    'original': ml_result
                }
            except:
                # Fallback if JSON parsing fails
                return {
                    'validated': True,
                    'classification': category,
                    'confidence': confidence,
                    'reason': 'Claude response parsing failed'
                }
                
        except Exception as e:
            logger.error(f"Claude validation failed: {e}")
            return {
                'validated': False,
                'original': ml_result,
                'reason': str(e)
            }
    
    def _create_analysis_prompt(self, code: str, context: Dict[str, Any]) -> str:
        """Create detailed prompt for Claude analysis."""
        file_path = context.get('file_path', 'unknown')
        
        prompt = f"""Analyze this code for security issues, code quality, and importance.

File: {file_path}
Code:
```
{code}
```

Please analyze and respond with:
1. Classification: Is this code critical (security/payment/auth), important (core logic), or trivial (tests/docs)?
2. Security Issues: Any vulnerabilities or risks?
3. Code Quality: Any anti-patterns or improvements needed?
4. Recommendations: Specific fixes if issues found

Format your response as:
CLASSIFICATION: [critical/important/trivial]
SECURITY: [list any security issues]
QUALITY: [list any quality issues]
RECOMMENDATIONS: [specific actionable fixes]
REASONING: [explain your classification]"""
        
        return prompt
    
    def _parse_claude_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response into structured data."""
        result = {
            'classification': 'important',  # default
            'security_issues': [],
            'quality_issues': [],
            'recommendations': [],
            'reasoning': ''
        }
        
        # Log the raw response for debugging
        logger.debug(f"Claude raw response:\n{response[:500]}...")
        
        # Simple parsing - handles various formats Claude might use
        lines = response.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if line.upper().startswith('CLASSIFICATION:'):
                # Save previous section if any
                if current_section and section_content:
                    self._save_section_content(result, current_section, section_content)
                    section_content = []
                
                # Extract classification
                classification = line.split(':', 1)[1].strip().lower()
                if classification in ['critical', 'important', 'trivial']:
                    result['classification'] = classification
                current_section = None
                
            elif line.upper().startswith('SECURITY:'):
                if current_section and section_content:
                    self._save_section_content(result, current_section, section_content)
                    section_content = []
                current_section = 'security'
                # Check if content is on same line
                content = line.split(':', 1)[1].strip()
                if content and content != '[]':
                    section_content.append(content)
                    
            elif line.upper().startswith('QUALITY:'):
                if current_section and section_content:
                    self._save_section_content(result, current_section, section_content)
                    section_content = []
                current_section = 'quality'
                content = line.split(':', 1)[1].strip()
                if content and content != '[]':
                    section_content.append(content)
                    
            elif line.upper().startswith('RECOMMENDATIONS:'):
                if current_section and section_content:
                    self._save_section_content(result, current_section, section_content)
                    section_content = []
                current_section = 'recommendations'
                content = line.split(':', 1)[1].strip()
                if content and content != '[]':
                    section_content.append(content)
                    
            elif line.upper().startswith('REASONING:'):
                if current_section and section_content:
                    self._save_section_content(result, current_section, section_content)
                    section_content = []
                current_section = 'reasoning'
                content = line.split(':', 1)[1].strip()
                if content:
                    result['reasoning'] = content
                    
            elif line and current_section:
                # Add content to current section
                section_content.append(line)
        
        # Save any remaining section content
        if current_section and section_content:
            self._save_section_content(result, current_section, section_content)
        
        # Log parsed result for debugging
        logger.debug(f"Parsed result: {result}")
        
        return result
    
    def _save_section_content(self, result: Dict[str, Any], section: str, content: List[str]):
        """Save section content to result, handling various formats."""
        if section == 'reasoning':
            result['reasoning'] = ' '.join(content)
        else:
            # Process list items
            items = []
            for line in content:
                # Handle bullet points, numbers, or plain text
                if line.startswith(('-', '*', '•', '·')):
                    items.append(line[1:].strip())
                elif line and line[0].isdigit() and ('.' in line[:3] or ')' in line[:3]):
                    # Numbered list
                    items.append(line.split('.', 1)[1].strip() if '.' in line[:3] else line.split(')', 1)[1].strip())
                elif line:
                    # Plain text - might be a single item or continuation
                    items.append(line)
            
            if section == 'security':
                result['security_issues'] = items
            elif section == 'quality':
                result['quality_issues'] = items
            elif section == 'recommendations':
                result['recommendations'] = items
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence based on Claude's analysis."""
        # High confidence if Claude found specific issues
        if result.get('security_issues'):
            return 0.95
        elif result.get('quality_issues'):
            return 0.85
        elif result.get('reasoning'):
            return 0.80
        else:
            return 0.70
    
    def _get_cache_key(self, code: str, context: Dict[str, Any]) -> str:
        """Generate cache key for code + context."""
        content = f"{context.get('file_path', '')}:{code[:200]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Check if we have cached analysis."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    # Check if cache is recent (24 hours)
                    cached_time = datetime.fromisoformat(data['timestamp'])
                    if (datetime.utcnow() - cached_time).total_seconds() < 86400:
                        data['from_cache'] = True
                        return data
            except:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """Save analysis result to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except Exception as e:
            logger.debug(f"Cache save failed: {e}")
    
    def _fallback_analysis(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when Claude not available."""
        # Use simple heuristics
        classification = 'important'
        security_issues = []
        
        code_lower = code.lower()
        if any(risk in code_lower for risk in ['password', 'secret', 'api_key']):
            classification = 'critical'
            security_issues.append('Possible hardcoded credential')
        elif 'eval(' in code or 'exec(' in code:
            classification = 'critical'
            security_issues.append('Dynamic code execution')
        
        return {
            'classification': classification,
            'security_issues': security_issues,
            'quality_issues': [],
            'recommendations': [],
            'reasoning': 'Analyzed using fallback heuristics',
            'confidence': 0.6,
            'fallback': True
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics from cache."""
        stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'classifications': {'critical': 0, 'important': 0, 'trivial': 0}
        }
        
        # Count cache files
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    stats['total_calls'] += 1
                    if data.get('from_cache'):
                        stats['cache_hits'] += 1
                    classification = data.get('classification', 'unknown')
                    if classification in stats['classifications']:
                        stats['classifications'][classification] += 1
            except:
                pass
        
        return stats