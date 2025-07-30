from fastapi import Request, HTTPException
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel
import json

class RequestData(BaseModel):
    queries: Dict[str, Any]
    params: Dict[str, Any]
    headers: Dict[str, Any]
    cookies: Dict[str, Any]
    session: Dict[str, Any]
    body: Optional[Union[Dict[str, Any], str]]

async def extract_all_request_data(request: Request) -> RequestData:
    """
    Extrait toutes les données de la requête dans un dictionnaire structuré
    
    Args:
        request: Objet Request de FastAPI
        
    Returns:
        RequestData: Objet contenant toutes les données de la requête
    """
    try:
        # Extraction des données de base
        query_params = dict(request.query_params)
        path_params = request.path_params
        headers = dict(request.headers)
        cookies = request.cookies
        
        # Extraction du corps (pour les méthodes POST, PUT, etc.)
        body = {}
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = await request.json()
            except json.JSONDecodeError:
                body = await request.body()
                try:
                    body = body.decode()
                except:
                    body = str(body)
        
        # Extraction de la session (nécessite un middleware de session configuré)
        session = {}
        if hasattr(request.state, 'session'):
            session = request.state.session
        elif 'session' in request.scope:
            session = request.scope['session']
        
        return RequestData(
            queries=query_params,
            params=path_params,
            headers=headers,
            cookies=cookies,
            session=session,
            body=body
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract request data: {str(e)}"
        )

def get_specific_data(
    request_data: RequestData,
    data_type: str,
    key: Optional[str] = None,
    default: Any = None
) -> Any:
    """
    Récupère une donnée spécifique de la requête
    
    Args:
        request_data: Objet RequestData contenant les données
        data_type: Type de données ('queries', 'params', 'headers', 'cookies', 'session', 'body')
        key: Clé spécifique à récupérer (optionnel)
        default: Valeur par défaut si la clé n'existe pas
        
    Returns:
        La valeur demandée ou le dictionnaire complet si aucune clé n'est spécifiée
        
    Raises:
        HTTPException: Si le type de données est invalide
    """
    data_map = {
        'queries': request_data.queries,
        'params': request_data.params,
        'headers': request_data.headers,
        'cookies': request_data.cookies,
        'session': request_data.session,
        'body': request_data.body
    }
    
    if data_type not in data_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data type. Must be one of: {', '.join(data_map.keys())}"
        )
    
    data = data_map[data_type]
    
    if key is not None:
        return data.get(key, default)
    return data