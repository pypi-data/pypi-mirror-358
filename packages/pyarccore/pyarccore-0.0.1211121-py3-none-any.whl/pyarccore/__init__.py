from typing import Any, Union, Dict, List, Optional
from fastapi import FastAPI, APIRouter, Request
from pathlib import Path
from .internationalisation_manager import InternationalisationManager
from .config_manager import ConfigManager
from .router import ArcCmsRouter
from .feature_manager import FeatureManager
from .request_utils import RequestData, extract_all_request_data, get_specific_data
import logging
import asyncio

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
    module: Optional[str] = None,
    *args,
    **kwargs
) -> Any:
    """
    Exécute une fonctionnalité globale ou d'un module
    
    Args:
        feature_path: "auth.createData" (module) ou "utils.cleanData" (global)
        module: Optionnel - nom du module ("module2")
        *args: Arguments positionnels
        **kwargs: Arguments nommés
        
    Returns:
        Résultat de la fonctionnalité
    """
    return _feature.execute(feature_path, module, *args, **kwargs)

async def execute_features(
    features: List[Dict[str, Any]],
    fail_fast: bool = False
) -> Dict[str, Any]:
    """
    Exécute plusieurs fonctionnalités en parallèle
    
    Args:
        features: Liste de dictionnaires contenant:
            - feature_path: chemin de la feature
            - module: nom du module (optionnel)
            - args: arguments positionnels (optionnel)
            - kwargs: arguments nommés (optionnel)
        fail_fast: Si True, s'arrête au premier échec
    
    Returns:
        Dictionnaire avec:
            - results: résultats des features réussies
            - errors: erreurs des features échouées
    """
    return await _feature.execute_many(features, fail_fast)

def execute_features_sync(
    features: List[Dict[str, Any]],
    fail_fast: bool = False
) -> Dict[str, Any]:
    """
    Version synchrone de execute_features
    
    Args: voir execute_features
    Returns: voir execute_features
    """
    return asyncio.run(_feature.execute_many_sync(features, fail_fast))

def list_features(module: str = None) -> Dict[str, list]:
    """Liste toutes les fonctionnalités disponibles d'un module"""
    return _feature.list_features(module)

def list_all_features() -> Dict[str, Dict[str, List[str]]]:
    """Liste toutes les fonctionnalités disponibles (globales et modules)"""
    return _feature.list_all_features()

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


async def all_requests(request: Request) -> RequestData:
    return await extract_all_request_data(request = request)

def specific_request(
    request_data: RequestData,
    data_type: str,
    key: Optional[str] = None,
    default: Any = None
) -> Any:
    return get_specific_data(
        request_data = request_data,
        data_type = data_type,
        key = key,
        default = default,
    )