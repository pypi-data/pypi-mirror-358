from typing import Any, Union, Dict
from fastapi import FastAPI, APIRouter
from pathlib import Path
from .internationalisation_manager import InternationalisationManager
from .config_manager import ConfigManager
from .router import ArcCmsRouter
from .feature_manager import FeatureManager
import logging

logger = logging.getLogger(__name__)

_intl = InternationalisationManager()
_config = ConfigManager()
_router = ArcCmsRouter()
_feature = FeatureManager()

def init_app(app_root: Union[Path, str] = None):
    """Initialise toutes les ressources"""
    if app_root is None:
        app_root = Path(__file__).parent.parent
    if isinstance(app_root, str):
        app_root = Path(app_root)
    
    _intl.set_project_root(app_root.resolve())
    _config.set_project_root(app_root.resolve())
    _feature.set_project_root(app_root)
    _intl.load_all()
    _config.load_all()
    
def execute_feature(
    feature_path: str,
    module: str,
    *args,
    **kwargs
) -> Any:
    """
    Exécute une fonctionnalité d'un module
    
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
    return _feature.execute(feature_path, module, *args, **kwargs)

def list_features(module: str) -> Dict[str, list]:
    """Liste toutes les fonctionnalités disponibles d'un module"""
    return _feature.list_features(module)

def t(key: str, locale: str = 'fr', module: str = "global", **kwargs) -> str:
    """Récupère une traduction"""
    value = _intl.get(module, key, locale) or key
    return value.format(**kwargs) if kwargs else value

def cfg(key: str, default: Any = None, module: str = "global") -> Any:
    """Récupère une configuration"""
    return _config.get(module, key, default)

def register_routes(router: APIRouter, base_path: Union[Path, str]):
    """Enregistre les routes"""
    if isinstance(base_path, str):
        base_path = Path(base_path)
    _router.register_routes(router, base_path.resolve())