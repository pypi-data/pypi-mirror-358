from fastapi import Request, HTTPException, UploadFile
from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel
import json

class FormDataItem(BaseModel):
    value: Union[str, bytes, UploadFile]
    type: str  # 'text', 'binary', or 'file'

class RequestData(BaseModel):
    queries: Dict[str, Any]
    params: Dict[str, Any]
    headers: Dict[str, Any]
    cookies: Dict[str, Any]
    session: Dict[str, Any]
    body: Optional[Union[Dict[str, Any], str]]
    form_data: Optional[Dict[str, FormDataItem]]

async def extract_all_request_data(request: Request) -> RequestData:
    """
    Extrait toutes les données brutes de la requête sans aucun traitement
    """
    try:
        # Extraction des données de base
        query_params = dict(request.query_params)
        path_params = request.path_params
        headers = dict(request.headers)
        cookies = request.cookies
        
        # Variables pour body et form_data
        body = None
        form_data = None
        
        # Détection du type de contenu
        content_type = headers.get('content-type', '')
        
        if 'multipart/form-data' in content_type:
            form_data = await _extract_raw_form_data(request)
        elif 'application/x-www-form-urlencoded' in content_type:
            form_data = await _extract_raw_urlencoded(request)
        elif request.method in ['POST', 'PUT', 'PATCH']:
            body = await _extract_raw_body(request)
        
        # Session data
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
            body=body,
            form_data=form_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract request data: {str(e)}"
        )

async def _extract_raw_form_data(request: Request) -> Dict[str, FormDataItem]:
    """Extrait les données brutes du formulaire multipart"""
    form_data = {}
    
    try:
        form_items = await request.form()
        for key, value in form_items.items():
            if isinstance(value, UploadFile):
                form_data[key] = FormDataItem(
                    value=value,  # Conserve l'objet UploadFile original
                    type='file'
                )
            else:
                form_data[key] = FormDataItem(
                    value=value,
                    type='binary' if isinstance(value, bytes) else 'text'
                )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid form data: {str(e)}"
        )
    
    return form_data

async def _extract_raw_urlencoded(request: Request) -> Dict[str, FormDataItem]:
    """Extrait les données brutes du formulaire urlencoded"""
    try:
        body = await request.body()
        form_data = {}
        for key, value in body.decode().split('&'):
            key_val = value.split('=')
            if len(key_val) == 2:
                form_data[key_val[0]] = FormDataItem(
                    value=key_val[1],
                    type='text'
                )
        return form_data
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid urlencoded form data: {str(e)}"
        )

async def _extract_raw_body(request: Request) -> Union[Dict[str, Any], str, bytes]:
    """Extrait le corps brut de la requête"""
    try:
        return await request.json()
    except json.JSONDecodeError:
        body = await request.body()
        try:
            return body.decode()
        except:
            return body

def get_specific_data(
    request_data: RequestData,
    data_type: str,
    key: Optional[str] = None,
    default: Any = None
) -> Any:
    """
    Récupère une donnée spécifique brute sans traitement
    """
    data_map = {
        'queries': request_data.queries,
        'params': request_data.params,
        'headers': request_data.headers,
        'cookies': request_data.cookies,
        'session': request_data.session,
        'body': request_data.body,
        'form_data': request_data.form_data or {}
    }
    
    if data_type not in data_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data type. Must be one of: {', '.join(data_map.keys())}"
        )
    
    data = data_map[data_type]
    
    if key is not None:
        if data_type == 'form_data' and key in data:
            return data[key].value  # Retourne la valeur brute
        return data.get(key, default)
    return data