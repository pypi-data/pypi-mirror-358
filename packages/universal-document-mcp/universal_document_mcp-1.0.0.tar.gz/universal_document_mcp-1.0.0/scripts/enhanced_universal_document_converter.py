#!/usr/bin/env python3
"""
Enhanced Universal Document Converter MCP Server
Features:
- Universal workspace compatibility
- NPX package distribution ready
- OpenRouter.AI integration for intelligent page layout
- Advanced API key management
- AI-powered layout optimization
"""

import sys
import os
import asyncio
import subprocess
import json
import re
import logging
import tempfile
import shutil
import requests
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class WorkspaceConfig:
    """Configuration for workspace detection and management"""
    root_path: Path
    relative_paths: bool = True
    backup_dir: str = "backups"
    output_dir: str = "output"
    temp_dir: Optional[str] = None

@dataclass
class AIConfig:
    """Configuration for AI-powered features"""
    enabled: bool = False
    provider: str = "openrouter"
    model: str = "anthropic/claude-3-haiku"
    api_keys: List[str] = None
    max_tokens: int = 4000
    temperature: float = 0.1
    chunk_size: int = 2000
    overlap_size: int = 200

@dataclass
class APIKeyStatus:
    """Status tracking for API keys"""
    key: str
    last_used: datetime
    request_count: int = 0
    rate_limited: bool = False
    rate_limit_reset: Optional[datetime] = None
    health_score: float = 1.0

class WorkspaceManager:
    """Manages workspace detection and path resolution"""
    
    def __init__(self, initial_path: Optional[str] = None):
        self.config = self._detect_workspace(initial_path)
        logger.info(f"Workspace detected: {self.config.root_path}")
    
    def _detect_workspace(self, initial_path: Optional[str] = None) -> WorkspaceConfig:
        """Dynamically detect workspace root and configuration"""
        if initial_path:
            root_path = Path(initial_path).resolve()
        else:
            # Try multiple detection methods
            root_path = self._find_workspace_root()
        
        # Ensure directories exist
        backup_dir = root_path / "backups"
        output_dir = root_path / "output"
        backup_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        
        return WorkspaceConfig(
            root_path=root_path,
            backup_dir=str(backup_dir.relative_to(root_path)),
            output_dir=str(output_dir.relative_to(root_path))
        )
    
    def _find_workspace_root(self) -> Path:
        """Find workspace root using multiple heuristics"""
        current = Path.cwd()
        
        # Method 1: Look for common workspace indicators
        workspace_indicators = [
            '.git', '.vscode', 'package.json', 'pyproject.toml', 
            'requirements.txt', 'Cargo.toml', '.project'
        ]
        
        path = current
        while path != path.parent:
            for indicator in workspace_indicators:
                if (path / indicator).exists():
                    logger.info(f"Workspace root found via {indicator}: {path}")
                    return path
            path = path.parent
        
        # Method 2: Check environment variables
        if 'WORKSPACE_ROOT' in os.environ:
            workspace_path = Path(os.environ['WORKSPACE_ROOT'])
            if workspace_path.exists():
                logger.info(f"Workspace root from environment: {workspace_path}")
                return workspace_path
        
        # Method 3: Use current directory as fallback
        logger.info(f"Using current directory as workspace root: {current}")
        return current
    
    def resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace root"""
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        return (self.config.root_path / path).resolve()
    
    def get_relative_path(self, path: str) -> str:
        """Get path relative to workspace root"""
        resolved = self.resolve_path(path)
        try:
            return str(resolved.relative_to(self.config.root_path))
        except ValueError:
            return str(resolved)

class APIKeyManager:
    """Advanced API key management with rotation and health monitoring"""
    
    def __init__(self, config_file: str = "api_keys.json"):
        self.config_file = config_file
        self.keys: List[APIKeyStatus] = []
        self.current_key_index = 0
        self.lock = threading.Lock()
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.keys = [
                        APIKeyStatus(
                            key=item['key'],
                            last_used=datetime.fromisoformat(item.get('last_used', datetime.now().isoformat())),
                            request_count=item.get('request_count', 0),
                            rate_limited=item.get('rate_limited', False),
                            rate_limit_reset=datetime.fromisoformat(item['rate_limit_reset']) if item.get('rate_limit_reset') else None,
                            health_score=item.get('health_score', 1.0)
                        )
                        for item in data.get('keys', [])
                    ]
                logger.info(f"Loaded {len(self.keys)} API keys")
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            self.keys = []
    
    def save_keys(self):
        """Save API keys to configuration file"""
        try:
            data = {
                'keys': [
                    {
                        'key': key.key,
                        'last_used': key.last_used.isoformat(),
                        'request_count': key.request_count,
                        'rate_limited': key.rate_limited,
                        'rate_limit_reset': key.rate_limit_reset.isoformat() if key.rate_limit_reset else None,
                        'health_score': key.health_score
                    }
                    for key in self.keys
                ]
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving API keys: {e}")
    
    def add_key(self, api_key: str) -> bool:
        """Add a new API key"""
        with self.lock:
            # Check if key already exists
            if any(key.key == api_key for key in self.keys):
                return False
            
            self.keys.append(APIKeyStatus(
                key=api_key,
                last_used=datetime.now()
            ))
            self.save_keys()
            logger.info(f"Added new API key (total: {len(self.keys)})")
            return True
    
    def bulk_import_keys(self, file_path: str) -> int:
        """Bulk import API keys from text file"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            added_count = 0
            for line in lines:
                key = line.strip()
                if key and not key.startswith('#'):  # Skip comments
                    if self.add_key(key):
                        added_count += 1
            
            logger.info(f"Bulk imported {added_count} new API keys")
            return added_count
        except Exception as e:
            logger.error(f"Error bulk importing keys: {e}")
            return 0
    
    def get_next_key(self) -> Optional[str]:
        """Get next available API key with load balancing"""
        with self.lock:
            if not self.keys:
                return None
            
            # Filter out rate-limited keys
            available_keys = [
                (i, key) for i, key in enumerate(self.keys)
                if not key.rate_limited or (
                    key.rate_limit_reset and 
                    datetime.now() > key.rate_limit_reset
                )
            ]
            
            if not available_keys:
                logger.warning("All API keys are rate limited")
                return None
            
            # Sort by health score and last used time
            available_keys.sort(key=lambda x: (x[1].health_score, -x[1].request_count))
            
            # Select the best key
            best_index, best_key = available_keys[0]
            self.current_key_index = best_index
            
            # Update usage statistics
            best_key.last_used = datetime.now()
            best_key.request_count += 1
            
            # Reset rate limit if time has passed
            if best_key.rate_limited and best_key.rate_limit_reset and datetime.now() > best_key.rate_limit_reset:
                best_key.rate_limited = False
                best_key.rate_limit_reset = None
                best_key.health_score = min(1.0, best_key.health_score + 0.1)
            
            self.save_keys()
            return best_key.key
    
    def mark_rate_limited(self, api_key: str, reset_time: Optional[datetime] = None):
        """Mark an API key as rate limited"""
        with self.lock:
            for key in self.keys:
                if key.key == api_key:
                    key.rate_limited = True
                    key.rate_limit_reset = reset_time or (datetime.now() + timedelta(hours=1))
                    key.health_score = max(0.1, key.health_score - 0.2)
                    logger.warning(f"API key marked as rate limited until {key.rate_limit_reset}")
                    break
            self.save_keys()
    
    def validate_key(self, api_key: str) -> bool:
        """Validate an API key by making a test request"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Test with a minimal request
            response = requests.get(
                'https://openrouter.ai/api/v1/models',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all API keys"""
        with self.lock:
            total_keys = len(self.keys)
            available_keys = sum(1 for key in self.keys if not key.rate_limited)
            avg_health = sum(key.health_score for key in self.keys) / total_keys if total_keys > 0 else 0
            
            return {
                'total_keys': total_keys,
                'available_keys': available_keys,
                'rate_limited_keys': total_keys - available_keys,
                'average_health_score': round(avg_health, 2),
                'keys_status': [
                    {
                        'key_hash': hashlib.md5(key.key.encode()).hexdigest()[:8],
                        'health_score': key.health_score,
                        'request_count': key.request_count,
                        'rate_limited': key.rate_limited,
                        'last_used': key.last_used.isoformat()
                    }
                    for key in self.keys
                ]
            }

class EnhancedUniversalDocumentConverter:
    """Enhanced document converter with AI-powered features"""
    
    def __init__(self, workspace_path: Optional[str] = None, ai_config: Optional[AIConfig] = None):
        self.workspace = WorkspaceManager(workspace_path)
        self.ai_config = ai_config or AIConfig()
        self.api_key_manager = APIKeyManager()
        
        # Supported trigger keywords
        self.supported_triggers = [
            "convert: md -> html -> pdf",
            "markdown to pdf",
            "document conversion",
            "md to pdf",
            "convert markdown",
            "generate pdf",
            "mermaid pdf",
            "export pdf",
            "create pdf from markdown",
            "markdown document conversion",
            "universal doc converter",
            "npx universal-doc-converter"
        ]
        
        logger.info("Enhanced Universal Document Converter initialized")
        logger.info(f"AI features: {'enabled' if self.ai_config.enabled else 'disabled'}")
        logger.info(f"API keys available: {len(self.api_key_manager.keys)}")
    
    def detect_trigger(self, user_input: str) -> bool:
        """Detect if user input contains conversion trigger keywords"""
        user_input_lower = user_input.lower()
        return any(trigger in user_input_lower for trigger in self.supported_triggers)

    async def analyze_document_with_ai(self, content: str, existing_diagrams: List[str]) -> Dict[str, Any]:
        """Use AI to analyze document structure and suggest optimal page breaks"""
        if not self.ai_config.enabled:
            return {"ai_analysis": False, "chunks": [], "page_breaks": []}

        api_key = self.api_key_manager.get_next_key()
        if not api_key:
            logger.warning("No available API keys for AI analysis")
            return {"ai_analysis": False, "chunks": [], "page_breaks": []}

        try:
            # Create AI prompt for document analysis
            prompt = self._create_layout_analysis_prompt(content, existing_diagrams)

            # Make API request to OpenRouter
            response = await self._make_ai_request(api_key, prompt)

            if response:
                return self._parse_ai_response(response)
            else:
                return {"ai_analysis": False, "chunks": [], "page_breaks": []}

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"ai_analysis": False, "chunks": [], "page_breaks": []}

    def _create_layout_analysis_prompt(self, content: str, diagrams: List[str]) -> str:
        """Create specialized AI prompt for document layout analysis"""
        return f"""You are a professional document layout specialist with expertise in both logical content flow and visual aesthetics. Analyze this markdown document and provide optimal page break recommendations.

DOCUMENT CONTENT:
{content[:self.ai_config.chunk_size]}

EXISTING MERMAID DIAGRAMS:
{len(diagrams)} diagrams detected

ANALYSIS REQUIREMENTS:
1. **Logical Flow Analysis**: Identify natural content boundaries that preserve reading flow
2. **Visual Layout Optimization**: Ensure diagrams and related text stay together
3. **Professional Standards**: Apply standard document formatting principles
4. **Page Break Strategy**: Suggest optimal break points that avoid:
   - Orphaned headings (heading at bottom of page)
   - Split diagrams across pages
   - Broken code blocks or tables
   - Awkward content separation

RESPONSE FORMAT (JSON):
{{
  "analysis_summary": "Brief overview of document structure",
  "optimal_chunks": [
    {{
      "chunk_id": 1,
      "start_line": 1,
      "end_line": 25,
      "content_type": "introduction",
      "contains_diagram": false,
      "break_reason": "Natural section boundary"
    }}
  ],
  "page_break_recommendations": [
    {{
      "position": "after_line_25",
      "confidence": 0.9,
      "reason": "Section boundary with diagram following"
    }}
  ],
  "layout_optimizations": [
    "Keep Figure 1 with its description",
    "Ensure conclusion doesn't start on new page alone"
  ]
}}

Analyze the document structure and provide your recommendations:"""

    async def _make_ai_request(self, api_key: str, prompt: str) -> Optional[Dict]:
        """Make request to OpenRouter AI API"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://universal-doc-converter.com',
                'X-Title': 'Universal Document Converter'
            }

            payload = {
                'model': self.ai_config.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': self.ai_config.max_tokens,
                'temperature': self.ai_config.temperature,
                'response_format': {'type': 'json_object'}
            }

            async with asyncio.timeout(30):  # 30 second timeout
                response = requests.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content')
            elif response.status_code == 429:
                # Rate limited
                self.api_key_manager.mark_rate_limited(api_key)
                logger.warning("API key rate limited, trying next key")
                return None
            else:
                logger.error(f"AI API request failed: {response.status_code} - {response.text}")
                return None

        except asyncio.TimeoutError:
            logger.error("AI API request timed out")
            return None
        except Exception as e:
            logger.error(f"AI API request error: {e}")
            return None

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract layout recommendations"""
        try:
            data = json.loads(response)
            return {
                "ai_analysis": True,
                "summary": data.get("analysis_summary", ""),
                "chunks": data.get("optimal_chunks", []),
                "page_breaks": data.get("page_break_recommendations", []),
                "optimizations": data.get("layout_optimizations", [])
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return {"ai_analysis": False, "chunks": [], "page_breaks": []}

    def install_dependencies(self) -> bool:
        """Install required dependencies for conversion"""
        try:
            import playwright
            import markdown
            logger.info("Dependencies already installed")
            return True
        except ImportError:
            logger.info("Installing required packages...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "markdown", "requests"])
                subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
                logger.info("Dependencies installed successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to install dependencies: {e}")
                return False

    def analyze_document(self, md_file: str) -> Dict:
        """Analyze markdown document for optimization opportunities"""
        try:
            resolved_path = self.workspace.resolve_path(md_file)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Detect existing Mermaid diagrams
            mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', content, re.DOTALL)

            # Detect figure placeholders
            figure_placeholders = re.findall(r'\[.*?Figure.*?\]', content)

            # Detect document type based on content
            doc_type = "technical" if any(word in content.lower() for word in
                                       ["architecture", "algorithm", "framework", "system"]) else "general"

            analysis = {
                "file_path": str(resolved_path),
                "relative_path": self.workspace.get_relative_path(md_file),
                "file_size": len(content),
                "line_count": len(content.split('\n')),
                "existing_mermaid_diagrams": len(mermaid_blocks),
                "figure_placeholders": len(figure_placeholders),
                "document_type": doc_type,
                "needs_optimization": len(mermaid_blocks) > 0,
                "complexity": "high" if len(content) > 20000 else "medium" if len(content) > 10000 else "low",
                "workspace_root": str(self.workspace.config.root_path)
            }

            logger.info(f"Document analysis: {analysis}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return {"error": str(e)}

    def optimize_mermaid_diagrams(self, content: str) -> str:
        """Optimize Mermaid diagrams for better PDF rendering"""

        # Patterns for common optimizations
        optimizations = [
            # Shorten common long labels
            (r'"([^"]{30,})"', lambda m: f'"{self.shorten_label(m.group(1))}"'),
            # Convert TB to TD for better spacing
            (r'flowchart TB', 'flowchart TD'),
            # Optimize class definitions for smaller stroke width
            (r'stroke-width:2px', 'stroke-width:1px'),
            (r'stroke-width:3px', 'stroke-width:2px'),
        ]

        optimized_content = content
        for pattern, replacement in optimizations:
            if callable(replacement):
                optimized_content = re.sub(pattern, replacement, optimized_content)
            else:
                optimized_content = re.sub(pattern, replacement, optimized_content)

        return optimized_content

    def shorten_label(self, label: str) -> str:
        """Intelligently shorten long labels while preserving meaning"""
        # Common abbreviations for technical terms
        abbreviations = {
            "Architecture": "Arch",
            "Cognitive": "Cog",
            "Differentiable": "Diff",
            "Optimization": "Opt",
            "Processing": "Process",
            "Framework": "FW",
            "Algorithm": "Algo",
            "Implementation": "Impl",
            "Configuration": "Config",
            "Management": "Mgmt",
            "Development": "Dev",
            "Application": "App",
            "Interface": "IF",
            "Component": "Comp"
        }

        shortened = label
        for full, abbrev in abbreviations.items():
            shortened = shortened.replace(full, abbrev)

        # If still too long, truncate intelligently
        if len(shortened) > 25:
            words = shortened.split()
            if len(words) > 2:
                shortened = f"{words[0]} {words[1]}..."
            elif len(shortened) > 30:
                shortened = shortened[:27] + "..."

        return shortened

    def create_backup(self, file_path: str) -> str:
        """Create timestamped backup of original file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        resolved_path = self.workspace.resolve_path(file_path)
        backup_dir = self.workspace.config.root_path / self.workspace.config.backup_dir
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / f"{resolved_path.stem}_backup_{timestamp}{resolved_path.suffix}"

        try:
            shutil.copy2(resolved_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path.relative_to(self.workspace.config.root_path))
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""
