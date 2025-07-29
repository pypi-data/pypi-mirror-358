"""
Semantic Code Analyzer - Real AI-powered code understanding

Uses embeddings and similarity search for intelligent classification.
"""
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    logger.warning("sentence-transformers not available - install with: pip install sentence-transformers")


@dataclass
class SemanticMatch:
    """Result from semantic analysis."""
    category: str
    confidence: float
    similar_to: str
    reasoning: str


class SemanticAnalyzer:
    """Real AI-powered semantic analysis using embeddings.
    
    This provides actual intelligence by:
    1. Understanding code semantics through embeddings
    2. Finding similar patterns in known examples
    3. Reasoning about code purpose and risk
    """
    
    def __init__(self, model_dir: Path):
        """Initialize semantic analyzer."""
        self.model_dir = Path(model_dir)
        self.model = None
        self.embeddings = {}
        self.examples = {}
        
        if HAS_EMBEDDINGS:
            self._initialize_model()
        else:
            logger.warning("Semantic analysis unavailable without sentence-transformers")
    
    def _initialize_model(self):
        """Initialize embedding model and load examples."""
        try:
            # Use a code-specific model if available
            model_name = 'all-MiniLM-L6-v2'  # Fast and efficient
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
            
            # Load or create embeddings
            self._load_embeddings()
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic model: {e}")
            self.model = None
    
    def _load_embeddings(self):
        """Load pre-computed embeddings and examples."""
        embeddings_path = self.model_dir / 'embeddings.npz'
        examples_path = self.model_dir / 'code_examples.json'
        
        # Load examples
        if examples_path.exists():
            with open(examples_path) as f:
                self.examples = json.load(f)
        else:
            # Use default examples
            self.examples = {
                "critical": [
                    {"code": "password = 'admin123'", "reason": "Hardcoded password"},
                    {"code": "eval(request.GET['cmd'])", "reason": "Remote code execution"},
                    {"code": "query = f'SELECT * FROM users WHERE id={user_id}'", "reason": "SQL injection"},
                    {"code": "os.system(user_input)", "reason": "Command injection"},
                    {"code": "pickle.loads(untrusted_data)", "reason": "Arbitrary code execution"},
                    {"code": "api_key = 'sk-1234567890abcdef'", "reason": "Exposed API key"}
                ],
                "important": [
                    {"code": "class UserAuthentication:", "reason": "Security-critical component"},
                    {"code": "def process_payment(amount, card):", "reason": "Financial transaction"},
                    {"code": "async def validate_permissions(user, resource):", "reason": "Access control"},
                    {"code": "def encrypt_data(plaintext, key):", "reason": "Cryptographic operation"},
                    {"code": "except Exception: pass", "reason": "Silent error handling"}
                ],
                "trivial": [
                    {"code": "import unittest", "reason": "Test framework import"},
                    {"code": "def test_addition():", "reason": "Unit test"},
                    {"code": "# TODO: refactor this later", "reason": "Comment"},
                    {"code": "logger.debug('Processing started')", "reason": "Debug logging"},
                    {"code": "if __name__ == '__main__':", "reason": "Script entry point"}
                ]
            }
            
            # Save examples
            examples_path.parent.mkdir(parents=True, exist_ok=True)
            with open(examples_path, 'w') as f:
                json.dump(self.examples, f, indent=2)
        
        # Load or compute embeddings
        if embeddings_path.exists():
            data = np.load(embeddings_path)
            self.embeddings = {k: data[k] for k in data.files}
            logger.info(f"Loaded embeddings from {embeddings_path}")
        else:
            self._compute_embeddings()
    
    def _compute_embeddings(self):
        """Compute embeddings for all examples."""
        if not self.model:
            return
        
        logger.info("Computing embeddings for code examples...")
        
        for category, examples in self.examples.items():
            codes = [ex['code'] for ex in examples]
            if codes:
                self.embeddings[category] = self.model.encode(codes)
        
        # Save embeddings
        embeddings_path = self.model_dir / 'embeddings.npz'
        np.savez_compressed(embeddings_path, **self.embeddings)
        logger.info(f"Saved embeddings to {embeddings_path}")
    
    def analyze(self, code: str, context: Dict[str, Any] = None) -> SemanticMatch:
        """Analyze code using semantic understanding.
        
        Args:
            code: Code snippet to analyze
            context: Additional context (file path, surrounding code, etc.)
            
        Returns:
            SemanticMatch with classification and reasoning
        """
        if not self.model or not self.embeddings:
            # Fallback to simple analysis
            return self._simple_analysis(code, context)
        
        # Encode the code
        code_embedding = self.model.encode([code])[0]
        
        # Find most similar examples
        best_match = None
        best_score = -1
        best_category = 'important'
        
        for category, embeddings in self.embeddings.items():
            # Compute cosine similarities
            similarities = self._cosine_similarity(code_embedding, embeddings)
            max_idx = np.argmax(similarities)
            max_score = similarities[max_idx]
            
            if max_score > best_score:
                best_score = max_score
                best_category = category
                best_match = self.examples[category][max_idx]
        
        # Determine confidence based on similarity
        if best_score > 0.8:
            confidence = 0.9
        elif best_score > 0.6:
            confidence = 0.7
        else:
            confidence = 0.5
        
        # Add context-based adjustments
        if context:
            confidence = self._adjust_confidence(code, context, confidence)
        
        return SemanticMatch(
            category=best_category,
            confidence=confidence,
            similar_to=best_match['code'] if best_match else '',
            reasoning=best_match['reason'] if best_match else 'No similar pattern found'
        )
    
    def _cosine_similarity(self, a: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between vector a and matrix B."""
        a_norm = a / np.linalg.norm(a)
        B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)
        return np.dot(B_norm, a_norm)
    
    def _adjust_confidence(self, code: str, context: Dict[str, Any], base_confidence: float) -> float:
        """Adjust confidence based on context."""
        file_path = context.get('file_path', '')
        
        # Boost confidence for known critical files
        if any(term in file_path.lower() for term in ['auth', 'security', 'crypto', 'payment']):
            return min(1.0, base_confidence * 1.2)
        
        # Lower confidence for test files
        if 'test' in file_path.lower():
            return base_confidence * 0.8
        
        return base_confidence
    
    def _simple_analysis(self, code: str, context: Dict[str, Any] = None) -> SemanticMatch:
        """Simple fallback analysis without ML."""
        # Look for obvious patterns
        if any(pattern in code.lower() for pattern in ['password =', 'api_key =', 'secret =']):
            return SemanticMatch('critical', 0.8, '', 'Hardcoded credential detected')
        elif 'eval(' in code or 'exec(' in code:
            return SemanticMatch('critical', 0.85, '', 'Dynamic code execution')
        elif any(pattern in code for pattern in ['TODO', 'FIXME', 'XXX']):
            return SemanticMatch('important', 0.6, '', 'Technical debt marker')
        else:
            return SemanticMatch('important', 0.5, '', 'Standard code')
    
    def explain_classification(self, code: str, result: SemanticMatch) -> str:
        """Provide detailed explanation of classification."""
        explanation = f"""
## Code Classification Result

**Category**: {result.category}
**Confidence**: {result.confidence:.0%}

### Reasoning
{result.reasoning}

### Similar Pattern
```
{result.similar_to}
```

### Recommendations
"""
        
        if result.category == 'critical':
            explanation += """
1. **Immediate Action Required**: This code contains a critical security issue
2. **Review**: Ensure this pattern is not used elsewhere in the codebase
3. **Fix**: Replace with secure alternative immediately
"""
        elif result.category == 'important':
            explanation += """
1. **Review Needed**: This code handles important functionality
2. **Testing**: Ensure comprehensive test coverage
3. **Documentation**: Add clear documentation of security considerations
"""
        else:
            explanation += """
1. **Low Risk**: This appears to be standard code
2. **Best Practice**: Follow coding standards
3. **Maintenance**: Keep code clean and well-documented
"""
        
        return explanation