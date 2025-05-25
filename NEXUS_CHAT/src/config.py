"""
Configuration management for NEXUS Multi-Agent Orchestrator
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class AgentConfig:
    role: str
    session_timeout: int = 3600
    max_retries: int = 3
    personality_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestratorConfig:
    task_timeout: int = 7200
    parallel_tasks: int = 4
    feedback_frequency: int = 30


@dataclass
class NEXUSConfig:
    workspace_path: str = "./workspace"
    session_storage_path: str = "sessions"
    log_level: str = "INFO"
    host: str = "localhost"
    port: int = 8000
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Agent configurations
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
    
    def __post_init__(self):
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


class ConfigManager:
    """
    Manages configuration loading and validation for NEXUS system
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        load_dotenv()
    
    def load_config(self) -> NEXUSConfig:
        """
        Load configuration from environment variables and config files
        """
        try:
            # Load base configuration from environment
            config = NEXUSConfig(
                workspace_path=os.getenv("NEXUS_WORKSPACE", "./workspace"),
                session_storage_path=os.getenv("NEXUS_SESSION_STORAGE", "sessions"),
                log_level=os.getenv("NEXUS_LOG_LEVEL", "INFO"),
                host=os.getenv("NEXUS_HOST", "localhost"),
                port=int(os.getenv("NEXUS_PORT", "8000")),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            
            # Load agent configurations
            agents_config_path = os.path.join(self.config_dir, "agents.json")
            if os.path.exists(agents_config_path):
                with open(agents_config_path, 'r') as f:
                    agents_data = json.load(f)
                
                # Parse agent configurations
                for agent_id, agent_data in agents_data.get("agents", {}).items():
                    config.agents[agent_id] = AgentConfig(
                        role=agent_data["role"],
                        session_timeout=agent_data.get("session_timeout", 3600),
                        max_retries=agent_data.get("max_retries", 3),
                        personality_config=agent_data.get("personality_config", {})
                    )
                
                # Parse orchestrator configuration
                orchestrator_data = agents_data.get("orchestrator", {})
                config.orchestrator = OrchestratorConfig(
                    task_timeout=orchestrator_data.get("task_timeout", 7200),
                    parallel_tasks=orchestrator_data.get("parallel_tasks", 4),
                    feedback_frequency=orchestrator_data.get("feedback_frequency", 30)
                )
            
            # Validate configuration
            self._validate_config(config)
            
            self.logger.info("Configuration loaded successfully")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _validate_config(self, config: NEXUSConfig):
        """
        Validate configuration values
        """
        # Check required API keys
        if not config.openai_api_key:
            self.logger.warning("OPENAI_API_KEY not configured")
        
        if not config.anthropic_api_key:
            self.logger.warning("ANTHROPIC_API_KEY not configured")
        
        # Validate workspace path
        if config.workspace_path:
            os.makedirs(config.workspace_path, exist_ok=True)
            os.makedirs(f"{config.workspace_path}/scratchpads", exist_ok=True)
            os.makedirs(f"{config.workspace_path}/sessions", exist_ok=True)
        
        # Validate port range
        if not (1024 <= config.port <= 65535):
            raise ValueError(f"Invalid port number: {config.port}")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {config.log_level}")
        
        # Validate agent configurations
        required_agents = ["aria", "code", "alpha", "beta"]
        for agent_id in required_agents:
            if agent_id not in config.agents:
                self.logger.warning(f"Missing configuration for agent: {agent_id}")
        
        self.logger.info("Configuration validation completed")
    
    def save_config(self, config: NEXUSConfig, config_file: str = "nexus_config.json"):
        """
        Save configuration to file
        """
        try:
            config_path = os.path.join(self.config_dir, config_file)
            
            config_data = {
                "workspace_path": config.workspace_path,
                "session_storage_path": config.session_storage_path,
                "log_level": config.log_level,
                "host": config.host,
                "port": config.port,
                "agents": {
                    agent_id: {
                        "role": agent_config.role,
                        "session_timeout": agent_config.session_timeout,
                        "max_retries": agent_config.max_retries,
                        "personality_config": agent_config.personality_config
                    }
                    for agent_id, agent_config in config.agents.items()
                },
                "orchestrator": {
                    "task_timeout": config.orchestrator.task_timeout,
                    "parallel_tasks": config.orchestrator.parallel_tasks,
                    "feedback_frequency": config.orchestrator.feedback_frequency
                }
            }
            
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
    
    def create_default_config(self) -> NEXUSConfig:
        """
        Create default configuration
        """
        config = NEXUSConfig()
        
        # Default agent configurations
        config.agents = {
            "aria": AgentConfig(
                role="coordinator",
                session_timeout=3600,
                max_retries=3,
                personality_config={
                    "detail_level": "high",
                    "analysis_depth": "comprehensive"
                }
            ),
            "code": AgentConfig(
                role="developer",
                session_timeout=3600,
                max_retries=3,
                personality_config={
                    "coding_style": "clean_code",
                    "optimization_focus": "performance"
                }
            ),
            "alpha": AgentConfig(
                role="test_creator",
                session_timeout=1800,
                max_retries=2,
                personality_config={
                    "coverage_target": 95,
                    "test_thoroughness": "comprehensive"
                }
            ),
            "beta": AgentConfig(
                role="test_validator",
                session_timeout=1800,
                max_retries=2,
                personality_config={
                    "validation_strictness": "high",
                    "performance_focus": "optimization"
                }
            )
        }
        
        return config


def get_config() -> NEXUSConfig:
    """
    Get the current NEXUS configuration
    """
    config_manager = ConfigManager()
    return config_manager.load_config()


def validate_environment() -> Dict[str, Any]:
    """
    Validate the environment for NEXUS system
    """
    validation_results = {
        "environment_valid": True,
        "warnings": [],
        "errors": [],
        "system_info": {}
    }
    
    # Check Python version
    import sys
    python_version = sys.version_info
    validation_results["system_info"]["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    
    if python_version < (3, 8):
        validation_results["errors"].append("Python 3.8+ required")
        validation_results["environment_valid"] = False
    
    # Check required environment variables
    required_env_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    for var in required_env_vars:
        if not os.getenv(var):
            validation_results["warnings"].append(f"Missing environment variable: {var}")
    
    # Check Claude CLI availability
    import shutil
    claude_cli = shutil.which("claude")
    validation_results["system_info"]["claude_cli_available"] = claude_cli is not None
    
    if not claude_cli:
        validation_results["errors"].append("Claude CLI not found in PATH")
        validation_results["environment_valid"] = False
    
    # Check disk space for workspace
    workspace_path = os.getenv("NEXUS_WORKSPACE", "./workspace")
    try:
        import shutil
        total, used, free = shutil.disk_usage(os.path.dirname(os.path.abspath(workspace_path)))
        validation_results["system_info"]["disk_space_gb"] = {
            "total": total // (1024**3),
            "used": used // (1024**3),
            "free": free // (1024**3)
        }
        
        # Warn if less than 1GB free
        if free < (1024**3):
            validation_results["warnings"].append("Low disk space (< 1GB free)")
            
    except Exception as e:
        validation_results["warnings"].append(f"Could not check disk space: {e}")
    
    return validation_results