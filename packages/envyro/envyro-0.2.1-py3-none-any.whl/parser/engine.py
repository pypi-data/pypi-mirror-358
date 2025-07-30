import re
from pathlib import Path
from typing import Dict, List


class EnvyroLexer:
    SECTION_PATTERN = re.compile(r'^\[(.+?)\]$')
    ASSIGN_PATTERN = re.compile(r'([^=]+)=(.+)')
    COMMENT_PATTERN = re.compile(r'^#')

    def tokenize(self, lines: List[str]) -> List[Dict]:
        tokens = []
        for line in lines:
            line = line.strip()
            if not line or self.COMMENT_PATTERN.match(line):
                continue
            if self.SECTION_PATTERN.match(line):
                tokens.append(
                    {"type": "SECTION", "value": self.SECTION_PATTERN.match(line).group(1)})
            elif self.ASSIGN_PATTERN.match(line):
                key, val = self.ASSIGN_PATTERN.match(line).groups()
                tokens.append(
                    {"type": "ASSIGN", "key": key.strip(), "value": val.strip()})
            else:
                raise SyntaxError(f"Unrecognized line: {line}")
        return tokens


class EnvyroParser:
    def parse(self, tokens: List[Dict]) -> Dict[str, Dict[str, str]]:
        structure = {}
        current_section = None
        for token in tokens:
            if token["type"] == "SECTION":
                current_section = token["value"]
                structure[current_section] = {}
            elif token["type"] == "ASSIGN":
                if not current_section:
                    raise ValueError("Assignment outside of a section")
                structure[current_section][token["key"]] = token["value"]
        return structure


class EnvyroSemanticAnalyzer:
    def analyze(self, structure: Dict[str, Dict[str, str]]) -> Dict:
        if "envs" not in structure or "environments" not in structure["envs"]:
            raise ValueError("Missing [envs] or 'environments' key")
        return structure


class EnvyroTransformer:
    ENV_LINE_PATTERN = re.compile(r'\[([a-zA-Z0-9_*]+)\]:(\".*?\"|\S+)')

    def resolve(self, structure: Dict[str, Dict[str, str]], env: str) -> Dict[str, str]:
        output = {}
        for section, entries in structure.items():
            if section == "envs":
                continue
            for key, raw_val in entries.items():
                full_key = f"{section}.{key}"
                val = self._resolve_value(raw_val, env)
                if val != "":
                    output[full_key] = val
        return output

    def _resolve_value(self, raw_val: str, env: str) -> str:
        matches = self.ENV_LINE_PATTERN.findall(raw_val)
        if not matches:
            return raw_val.strip().strip('"')
        for key, val in matches:
            if key == env:
                return val.strip().strip('"')
        for key, val in matches:
            if key == '*':
                return val.strip().strip('"')
        return ""


class EnvyroCodeGenerator:
    def generate_env_file(self, env_vars: Dict[str, str], output_path: Path):
        with output_path.open("w") as f:
            for k, v in env_vars.items():
                f.write(f"{k.upper().replace('.', '_')}={v}\n")


class EnvyroCompiler:
    def __init__(self, file_path: str, env: str):
        self.file_path = Path(file_path)
        self.env = env

    def compile(self):
        # 1. Read Source
        lines = self.file_path.read_text(encoding="utf-8").splitlines()

        # 2. Lexical Analysis
        lexer = EnvyroLexer()
        tokens = lexer.tokenize(lines)

        # 3. Parsing
        parser = EnvyroParser()
        structure = parser.parse(tokens)

        # 4. Semantic Analysis
        analyzer = EnvyroSemanticAnalyzer()
        validated = analyzer.analyze(structure)

        # 5. Transform
        transformer = EnvyroTransformer()
        resolved = transformer.resolve(validated, self.env)

        # 6. Code Generation
        generator = EnvyroCodeGenerator()
        generator.generate_env_file(resolved, Path(f".env.{self.env}"))
