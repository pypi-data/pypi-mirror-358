from fastapi import Request, HTTPException, UploadFile
from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel
import json
import urllib.parse

class FormDataItem(BaseModel):
    data: Union[str, bytes]
    filename: Optional[str]
    content_type: Optional[str]

class RequestData(BaseModel):
    queries: Dict[str, Any]
    params: Dict[str, Any]
    headers: Dict[str, Any]
    cookies: Dict[str, Any]
    session: Dict[str, Any]
    body: Optional[Union[Dict[str, Any], str]]
    form_data: Optional[Dict[str, Union[str, FormDataItem]]]

async def extract_all_request_data(request: Request) -> RequestData:
    """
    Extrait toutes les données de la requête y compris le form-data
    """
    try:
        # Extraction des données de base
        query_params = dict(request.query_params)
        path_params = request.path_params
        headers = dict(request.headers)
        cookies = request.cookies
        
        # Initialisation des variables
        body = None
        form_data = None
        
        # Vérification du content-type
        content_type = headers.get('content-type', '')
        
        if 'multipart/form-data' in content_type:
            form_data = await _extract_form_data(request)
        elif 'application/x-www-form-urlencoded' in content_type:
            form_data = await _extract_urlencoded_form(request)
        elif request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = await request.json()
            except json.JSONDecodeError:
                body = await request.body()
                try:
                    body = body.decode()
                except:
                    body = str(body)
        
        # Extraction de la session
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

async def _extract_form_data(request: Request) -> Dict[str, Union[str, FormDataItem]]:
    """Extrait les données d'un formulaire multipart"""
    form_data = {}
    
    try:
        form_items = await request.form()
        for key, value in form_items.items():
            if isinstance(value, UploadFile):
                form_data[key] = FormDataItem(
                    data=await value.read(),
                    filename=value.filename,
                    content_type=value.content_type
                )
                await value.seek(0)  # Rewind the file for potential future reads
            else:
                form_data[key] = value
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid form data: {str(e)}"
        )
    
    return form_data

async def _extract_urlencoded_form(request: Request) -> Dict[str, str]:
    """Extrait les données d'un formulaire urlencoded"""
    try:
        body = await request.body()
        return urllib.parse.parse_qs(body.decode())
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid urlencoded form data: {str(e)}"
        )

def get_specific_data(
    request_data: RequestData,
    data_type: str,
    key: Optional[str] = None,
    default: Any = None
) -> Any:
    """
    Récupère une donnée spécifique de la requête
    
    Ajout du support pour 'form_data' comme type de données
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
        if data_type == 'form_data' and key in data and isinstance(data[key], FormDataItem):
            return data[key].data  # Retourne directement les données binaires/textuelles
        return data.get(key, default)
    return data