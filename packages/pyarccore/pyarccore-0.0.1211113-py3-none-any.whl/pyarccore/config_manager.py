import xml.etree.ElementTree as ET
from pathlib import Path
import threading
import hashlib
from functools import lru_cache
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self._configs = {}
        self._lock = threading.RLock()
        self._project_root = None
        self._file_hashes = {}

    def set_project_root(self, path: Path):
        """Définit la racine du projet"""
        with self._lock:
            self._project_root = path.resolve()

    def load_all(self):
        """Charge toutes les configurations"""
        if self._project_root is None:
            logger.error("Project root not set, call set_project_root() first")
            return

        # Global
        global_config = self._project_root / 'config.xml'
        if global_config.exists():
            self._load_config('global', global_config)

        # Modules
        modules_dir = self._project_root / 'modules'
        if modules_dir.exists():
            for module_path in modules_dir.iterdir():
                if module_path.is_dir():
                    config_file = module_path / 'config.xml'
                    if config_file.exists():
                        self._load_config(module_path.name, config_file)

    def _load_config(self, name: str, path: Path):
        """Charge une configuration XML"""
        path = path.resolve()
        file_hash = self._file_hash(path)
        try:
            tree = ET.parse(path)
            config = self._xml_to_dict(tree.getroot())
            config['_hash'] = file_hash

            with self._lock:
                self._configs[name] = config

        except ET.ParseError as e:
            logger.error(f"XML parsing error in config {path}: {e}")
        except Exception as e:
            logger.error(f"Failed to load config {path}: {e}")

    def _file_hash(self, path: Path) -> str:
        """Calcule le hash d'un fichier"""
        path = path.resolve()
        if path not in self._file_hashes:
            try:
                with open(path, 'rb') as f:
                    self._file_hashes[path] = hashlib.md5(f.read()).hexdigest()
            except IOError as e:
                logger.error(f"Could not read file {path}: {e}")
                return ""
        return self._file_hashes[path]

    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convertit XML en dict"""
        result = {**element.attrib}
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = [result[child.tag], child_data]
            else:
                result[child.tag] = child_data or child.text
        return result

    @lru_cache(maxsize=1024)
    def get(self, module: str, key: str, default: Any = None) -> Any:
        """Récupère une valeur avec cache"""
        with self._lock:
            keys = key.split('.')
            try:
                value = self._configs.get(module, {})
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default