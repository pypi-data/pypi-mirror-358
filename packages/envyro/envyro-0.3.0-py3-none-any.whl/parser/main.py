import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Literal, Any

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import tomli_w

    TOML_WRITE_AVAILABLE = True
except ImportError:
    TOML_WRITE_AVAILABLE = False


class EnvyroParser:
    ENV_SECTION = "envs"
    SECTION_PATTERN = re.compile(r"^\[(.+?)\]$")
    ENV_LINE_PATTERN = re.compile(r"\[([a-zA-Z0-9_*]+)\]:(\".*?\"|\S+)")

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.envs: List[str] = []
        self.default_env: Optional[str] = None
        self.structure: Dict[str, Dict[str, str]] = {}
        self._parse()

    def _parse(self):
        current_section = None
        try:
            self.file_path = self.file_path.resolve(strict=True)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{self.file_path}' not found.")
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                section_match = self.SECTION_PATTERN.match(line)
                if section_match:
                    current_section = section_match.group(1)
                    self.structure[current_section] = {}
                    continue

                if "=" in line and current_section:
                    key, raw_val = [x.strip() for x in line.split("=", 1)]
                    self.structure[current_section][key] = raw_val

        self._extract_envs()

    def _extract_envs(self):
        env_section = self.structure.get(self.ENV_SECTION, {})
        envs_str = env_section.get("environments", "")
        self.envs = [e.strip() for e in envs_str.split(",") if e.strip()]
        self.default_env = env_section.get(
            "default", self.envs[0] if self.envs else None
        )

    def _resolve_value(self, raw_val: str, env: str) -> str:
        matches = self.ENV_LINE_PATTERN.findall(raw_val)

        if not matches:
            return raw_val.strip().strip('"')

        for key, val in matches:
            if key == env:
                return val.strip().strip('"')

        for key, val in matches:
            if key == "*":
                return val.strip().strip('"')

        return ""

    def _flatten(self, data: Dict[str, Dict[str, str]], env: str) -> Dict[str, str]:
        result = {}
        for section, entries in data.items():
            if section == self.ENV_SECTION:
                continue

            for key, raw_val in entries.items():
                full_key = f"{section}.{key}" if section else key
                resolved = self._resolve_value(raw_val, env)
                if resolved != "":
                    result[full_key] = resolved

        return result

    def get_env_vars(self, env: Optional[str] = None) -> Dict[str, str]:
        env = env or self.default_env
        if env not in self.envs:
            raise ValueError(
                f"Environment '{env}' not declared in envs, available: {self.envs}"
            )

        return self._flatten(self.structure, env)

    def export_env_file(self, env: str, output_path: Optional[str] = None) -> None:
        env_vars = self.get_env_vars(env)
        output = Path(output_path) if output_path else Path(f".env.{env}")

        with output.open("w") as f:
            for key, val in env_vars.items():
                env_key = key.upper().replace(".", "_")
                f.write(f"{env_key}={val}\n")

    def export_json(self, env: str, output_path: Optional[str] = None) -> None:
        """Export environment variables to JSON format."""
        env_vars = self.get_env_vars(env)
        output = Path(output_path) if output_path else Path(f"config.{env}.json")

        nested_config = self._flatten_to_nested(env_vars)

        with output.open("w") as f:
            json.dump(nested_config, f, indent=2)

    def export_yaml(self, env: str, output_path: Optional[str] = None) -> None:
        """Export environment variables to YAML format."""
        if not YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required for YAML export. Install with: pip install PyYAML"
            )

        env_vars = self.get_env_vars(env)
        output = Path(output_path) if output_path else Path(f"config.{env}.yaml")

        nested_config = self._flatten_to_nested(env_vars)

        with output.open("w") as f:
            yaml.dump(nested_config, f, default_flow_style=False, sort_keys=False)

    def export_toml(self, env: str, output_path: Optional[str] = None) -> None:
        """Export environment variables to TOML format."""
        if not TOML_WRITE_AVAILABLE:
            raise ImportError(
                "tomli-w is required for TOML export. Install with: pip install tomli-w"
            )

        env_vars = self.get_env_vars(env)
        output = Path(output_path) if output_path else Path(f"config.{env}.toml")

        nested_config = self._flatten_to_nested(env_vars)

        # Use tomli-w to write TOML
        with output.open("wb") as f:
            tomli_w.dump(nested_config, f)

    def _flatten_to_nested(self, flat_config: Dict[str, str]) -> Dict[str, Any]:
        """Convert flat key-value pairs to nested structure."""
        nested = {}
        for key, value in flat_config.items():
            parts = key.split(".")
            current = nested
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        return nested

    def _write_toml(self, data: Dict[str, Any], file, prefix: str = "") -> None:
        """Write data to TOML format."""
        for key, value in data.items():
            if isinstance(value, dict):
                if prefix:
                    file.write(f"\n[{prefix}.{key}]\n")
                else:
                    file.write(f"\n[{key}]\n")
                self._write_toml(value, file, f"{prefix}.{key}" if prefix else key)
            else:
                if isinstance(value, str) and ('"' in value or "\n" in value):
                    value = f'"""\n{value}\n"""'
                elif isinstance(value, str):
                    value = f'"{value}"'
                file.write(f"{key} = {value}\n")

    def export_format(
        self,
        env: str,
        format_type: Literal["env", "json", "yaml", "toml"],
        output_path: Optional[str] = None,
    ) -> None:
        """Export environment variables to the specified format."""
        format_exporters = {
            "env": self.export_env_file,
            "json": self.export_json,
            "yaml": self.export_yaml,
            "toml": self.export_toml,
        }

        if format_type not in format_exporters:
            raise ValueError(
                f"Unsupported format: {format_type}. Supported formats: {list(format_exporters.keys())}"
            )

        format_exporters[format_type](env, output_path)

    def export_all(self) -> List[str]:
        exported_envs = []
        for env in self.envs:
            self.export_env_file(env)
            exported_envs.append(env)
        return exported_envs
