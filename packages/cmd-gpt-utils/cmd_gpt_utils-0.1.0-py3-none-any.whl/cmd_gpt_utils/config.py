import os
import yaml
from dataclasses import dataclass, field
from dotenv import load_dotenv
from typing import Optional, List

from .exceptions import ConfigError

@dataclass
class Model:
    id: int
    openai_api_key: str
    api_base_url: str
    model_tag: str
    model_name: Optional[str] = None
    enable_sse: bool = True
    enable_cot: bool = False
    cot_tag: Optional[str] = None
    temperature: float = -1.0

    def __post_init__(self):
        if self.model_name is None:
            self.model_name = self.model_tag

@dataclass
class Config:
    model_yaml_path: Optional[str] = None
    system_prompt: Optional[str] = None
    enable_cot: Optional[bool] = None
    cot_tag: Optional[str] = None
    enable_sse: Optional[bool] = None
    prompt_before: Optional[str] = None
    prompt_after: Optional[str] = None
    prompt_concat_nl: bool = True
    prompt_concat_sp: bool = True
    stop_at_newline: bool = False
    models: List[Model] = field(default_factory=list)

class ConfigLoader:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = os.path.expanduser(
            config_dir or os.getenv("CMDGPT_CONFIG_PATH", "~/.config/cmd_gpt")
        )
        os.makedirs(self.config_dir, exist_ok=True)

    def initialize_default_configs(self):
        conf_path = os.path.join(self.config_dir, "default.conf")
        if not os.path.exists(conf_path):
            conf_template = """# This is the default configuration file for cmd_gpt_utils.
# You can copy this file to 'default.local' to override settings safely.

# --- File Paths ---
# MODEL_YAML: Path to the model configuration file.
# It can be an absolute path or a path relative to the config directory.
# Default: models.yaml
# MODEL_YAML=models.yaml

# --- Prompting ---
# SYSTEM_PROMPT: A default system prompt to be used for all conversations.
# SYSTEM_PROMPT=You are a helpful AI assistant.

# PROMPT_BEFORE: Text to prepend to every prompt.
# PROMPT_BEFORE=

# PROMPT_AFTER: Text to append to every prompt.
# PROMPT_AFTER=

# PROMPT_CONCAT_NL: Whether to join prompt parts (-B, main, -A) with a newline.
# Default: true
# PROMPT_CONCAT_NL=true

# PROMPT_CONCAT_SP: Whether to join positional prompt arguments with a space.
# Default: true
# PROMPT_CONCAT_SP=true

# STOP_AT_NEWLINE: Stop reading from stdin at the first newline.
# Default: false
# STOP_AT_NEWLINE=false

# --- Chain-of-Thought (CoT) ---
# ENABLE_COT: Default setting for CoT filtering (true, false, default).
# 'default' uses the model's own setting.
# ENABLE_COT=default

# COT_TAG: Default tag for CoT filtering if ENABLE_COT is true.
# COT_TAG=

# --- Streaming (SSE) ---
# ENABLE_SSE: Default setting for streaming (true, false, default).
# 'default' uses the model's own setting.
# ENABLE_SSE=default
"""
            with open(conf_path, 'w') as f:
                f.write(conf_template)

        yaml_path = os.path.join(self.config_dir, "models.yaml")
        if not os.path.exists(yaml_path):
            yaml_template = """# This file configures the models available to cmd_gpt_utils.
# You can define multiple model profiles here.

models:
    - 
        id: 1
        # Your OpenAI API key. This is required.
        openai_api_key: "sk-YOUR_API_KEY_HERE"
        
        # The base URL for the API.
        api_base_url: "https://api.openai.com/v1/chat/completions"
        
        # The model identifier used in the API call (e.g., gpt-4-turbo).
        model_tag: "gpt-4-turbo"
        
        # A friendly name for command-line selection (e.g., -m gpt4-turbo).
        model_name: "gpt4-turbo"
        
        # Optional settings for this specific model.
        # enable_sse: true
        # enable_cot: false
        # cot_tag: "thinking"
        # temperature: 1.0
    - 
        id: 2
        # It's recommended to use a different key for different providers or models.
        openai_api_key: "sk-ANOTHER_API_KEY"
        
        # Example for a different provider.
        api_base_url: "https://api.deepseek.com/chat/completions"
        
        model_tag: "deepseek-chat"
        
        model_name: "deepseek"
        
        # This model will have streaming disabled by default.
        enable_sse: false
"""
            with open(yaml_path, 'w') as f:
                f.write(yaml_template)

    def _find_valid_path(self, path: str) -> str:
        if os.path.isabs(path):
            if os.path.exists(path):
                return path
        else:
            search_paths = [
                os.path.join(os.getcwd(), path),
                os.path.join(os.getcwd(), f"{path}.local"),
                os.path.join(self.config_dir, path),
                os.path.join(self.config_dir, f"{path}.local"),
            ]
            for p in search_paths:
                if os.path.exists(p):
                    return p
        raise ConfigError(f"Configuration file not found for path: {path}")

    def load(self, conf_files: Optional[List[str]] = None) -> Config:
        # 1. Load default .conf file
        default_local_path = os.path.join(self.config_dir, "default.local")
        if os.path.exists(default_local_path):
            load_dotenv(default_local_path)
        else:
            default_path = os.path.join(self.config_dir, "default.conf")
            if os.path.exists(default_path):
                load_dotenv(default_path)
        
        # 2. Load user-specified .conf files, overriding previous ones
        if conf_files:
            for conf_file in conf_files:
                found_path = self._find_valid_path(conf_file)
                load_dotenv(found_path, override=True)

        # 3. Resolve MODEL_YAML path
        model_yaml_path_str = os.getenv("MODEL_YAML", "models.yaml")
        model_yaml_path = self._find_valid_path(model_yaml_path_str)

        with open(model_yaml_path, 'r') as f:
            models_data = yaml.safe_load(f)

        if not models_data or 'models' not in models_data:
            raise ConfigError(f"No 'models' section found in {model_yaml_path}")
            
        models = [Model(**m) for m in models_data['models']]
        models.sort(key=lambda m: m.id)

        # 4. Populate Config object from environment
        enable_cot_str = os.getenv("ENABLE_COT", "default").lower()
        enable_cot = None
        if enable_cot_str == 'true':
            enable_cot = True
        elif enable_cot_str == 'false':
            enable_cot = False

        enable_sse_str = os.getenv("ENABLE_SSE", "default").lower()
        enable_sse = None
        if enable_sse_str == 'true':
            enable_sse = True
        elif enable_sse_str == 'false':
            enable_sse = False
            
        prompt_concat_nl = os.getenv("PROMPT_CONCAT_NL", "true").lower() == 'true'
        prompt_concat_sp = os.getenv("PROMPT_CONCAT_SP", "true").lower() == 'true'
        stop_at_newline = os.getenv("STOP_AT_NEWLINE", "false").lower() == 'true'

        return Config(
            model_yaml_path=model_yaml_path,
            system_prompt=os.getenv("SYSTEM_PROMPT"),
            enable_cot=enable_cot,
            cot_tag=os.getenv("COT_TAG"),
            enable_sse=enable_sse,
            prompt_before=os.getenv("PROMPT_BEFORE"),
            prompt_after=os.getenv("PROMPT_AFTER"),
            prompt_concat_nl=prompt_concat_nl,
            prompt_concat_sp=prompt_concat_sp,
            stop_at_newline=stop_at_newline,
            models=models,
        )
