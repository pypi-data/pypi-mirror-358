import json
import threading
from pathlib import Path
from functools import lru_cache
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class InternationalisationManager:
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
        self._translations = {}
        self._lock = threading.RLock()
        self._project_root = None

    def set_project_root(self, path: Path):
        """Définit la racine du projet"""
        with self._lock:
            self._project_root = path.resolve()

    def load_all(self):
        """Charge toutes les traductions"""
        if self._project_root is None:
            logger.error("Project root not set, call set_project_root() first")
            return

        # Global
        global_locale = self._project_root / 'locales'
        if global_locale.exists():
            self._load_translations('global', global_locale)

        # Modules
        modules_dir = self._project_root / 'modules'
        if modules_dir.exists():
            for module_path in modules_dir.iterdir():
                if module_path.is_dir():
                    locale_dir = module_path / 'locales'
                    if locale_dir.exists():
                        self._load_translations(module_path.name, locale_dir)

    def _load_translations(self, module_name: str, locale_dir: Path):
        """Charge les traductions pour un module"""
        locale_dir = locale_dir.resolve()
        translations = {}
        
        for locale_file in locale_dir.glob('*.json'):
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning(f"Empty translation file: {locale_file}")
                        continue
                    translations[locale_file.stem] = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {locale_file}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error loading {locale_file}: {e}")
                continue
        
        if translations:
            with self._lock:
                self._translations[module_name] = translations

    @lru_cache(maxsize=2048)
    def get(self, module: str, key: str, locale: str = 'fr') -> Optional[str]:
        """Récupère une traduction avec cache"""
        with self._lock:
            keys = key.split('.')
            try:
                value = self._translations.get(module, {}).get(locale, {})
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return None