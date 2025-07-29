import importlib
import inspect
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union
import logging
import asyncio
import threading

logger = logging.getLogger(__name__)

class FeatureManager:
    _instance = None
    _lock = threading.Lock()
    _features_cache: Dict[str, Dict[str, Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self._project_root = None

    def set_project_root(self, path: Union[str, Path]):
        """Définit la racine du projet"""
        self._project_root = Path(path).resolve()

    async def execute(
        self,
        feature_path: str,
        module: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Exécute une fonctionnalité de manière asynchrone ou synchrone
        
        Args:
            feature_path: "auth_features.createData"
            module: "module2"
            *args: Arguments positionnels
            **kwargs: Arguments nommés
            
        Returns:
            Résultat de la fonctionnalité
            
        Raises:
            FeatureNotFound: Si la fonctionnalité n'existe pas
            FeatureError: Si une erreur survient lors de l'exécution
        """
        try:
            feature = self._get_feature(feature_path, module)
            
            if asyncio.iscoroutinefunction(feature):
                return await feature(*args, **kwargs)
            return feature(*args, **kwargs)
            
        except ImportError as e:
            logger.error(f"Feature import error: {e}")
            raise FeatureNotFound(f"Feature '{feature_path}' not found in module '{module}'") from e
        except Exception as e:
            logger.error(f"Feature execution error: {e}")
            raise FeatureError(f"Error executing feature '{feature_path}': {str(e)}") from e

    def _get_feature(self, feature_path: str, module: str) -> Callable:
        """Récupère une fonctionnalité depuis le cache ou la charge"""
        cache_key = f"{module}.{feature_path}"
        
        if cache_key in self._features_cache:
            return self._features_cache[cache_key]
        
        # Format: "auth_features.createData"
        parts = feature_path.split('.')
        if len(parts) != 2:
            raise FeatureNotFound(f"Invalid feature path format: {feature_path}")
        
        filename, func_name = parts
        
        # Chemin vers le fichier de feature
        feature_file = self._project_root / "modules" / module / "features" / f"{filename}.py"
        if not feature_file.exists():
            raise FeatureNotFound(f"Feature file not found: {feature_file}")
        
        # Import dynamique
        module_path = f"modules.{module}.features.{filename}"
        try:
            feature_module = importlib.import_module(module_path)
            
            # Vérifie que la fonction existe
            if not hasattr(feature_module, func_name):
                raise FeatureNotFound(f"Function '{func_name}' not found in {module_path}")
                
            feature = getattr(feature_module, func_name)
            
            # Cache la fonctionnalité
            self._features_cache[cache_key] = feature
            return feature
            
        except ImportError as e:
            logger.error(f"Failed to import feature module {module_path}: {e}")
            raise

    def list_features(self, module: str) -> Dict[str, list]:
        """Liste toutes les fonctionnalités disponibles d'un module"""
        features_dir = self._project_root / "modules" / module / "features"
        if not features_dir.exists():
            return {}
            
        features = {}
        for feature_file in features_dir.glob('*.py'):
            if feature_file.name.startswith('_'):
                continue
                
            module_name = feature_file.stem
            module_path = f"modules.{module}.features.{module_name}"
            
            try:
                feature_module = importlib.import_module(module_path)
                module_features = [
                    name for name, obj in inspect.getmembers(feature_module)
                    if inspect.isfunction(obj) or inspect.iscoroutinefunction(obj)
                ]
                features[module_name] = module_features
            except ImportError:
                continue
                
        return features

class FeatureNotFound(Exception):
    """Exception levée quand une fonctionnalité n'est pas trouvée"""
    pass

class FeatureError(Exception):
    """Exception levée quand une erreur survient lors de l'exécution"""
    pass