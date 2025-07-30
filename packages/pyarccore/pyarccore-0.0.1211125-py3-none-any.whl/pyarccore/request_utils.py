import re
from fastapi import Request, HTTPException, UploadFile
from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel
import json
from collections import defaultdict


class RequestData(BaseModel):
    queries: Dict[str, Any]
    params: Dict[str, Any]
    headers: Dict[str, Any]
    cookies: Dict[str, Any]
    session: Dict[str, Any]
    body: Optional[Union[Dict[str, Any], str]]
    form_data: Optional[Dict[str, Any]]

async def extract_all_request_data(request: Request) -> RequestData:
    try:
        # Extraction des données de base
        query_params = dict(request.query_params)
        path_params = dict(request.path_params)
        headers = dict(request.headers)
        cookies = dict(request.cookies)
        
        # Gestion du corps et form-data
        body = None
        form_data = None
        content_type = headers.get('content-type', '')

        if 'multipart/form-data' in content_type:
            form_data = await parse_form_data(request)
        elif 'application/x-www-form-urlencoded' in content_type:
            form_data = await parse_urlencoded_form(request)
        elif request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = await request.json()
            except json.JSONDecodeError:
                body = await request.body()
                try:
                    body = body.decode()
                except:
                    body = str(body)

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

async def parse_form_data(request: Request) -> Dict[str, Any]:
    form_data = {}
    form_items = await request.form()
    
    for key, value in form_items.items():
        if isinstance(value, UploadFile):
            continue  # Les fichiers sont gérés séparément
        
        # Conversion de la notation crochets en notation pointée
        normalized_key = key.replace('[', '.').replace(']', '')
        parts = normalized_key.split('.')
        current = form_data
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = _convert_value(value)
    
    # Traitement des fichiers
    files = await request.files()
    for key, file in files.items():
        normalized_key = key.replace('[', '.').replace(']', '')
        parts = normalized_key.split('.')
        current = form_data
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = file
    
    return form_data

async def parse_urlencoded_form(request: Request) -> Dict[str, Any]:
    body = await request.body()
    form_data = {}
    for item in body.decode().split('&'):
        key, value = item.split('=', 1)
        _process_form_field(form_data, key, value)
    return form_data

def _process_form_field(data: dict, key: str, value: Any):
    # Gestion des tableaux (champs comme 'imgs[]')
    if key.endswith('[]'):
        clean_key = key[:-2]
        if clean_key not in data:
            data[clean_key] = []
        data[clean_key].append(value)
        return

    # Gestion des structures imbriquées (other_info[data1])
    if '[' in key and ']' in key:
        parts = re.split(r'\[|\]', key)
        parts = [p for p in parts if p]  # Supprime les chaînes vides
        
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        last_part = parts[-1]
        current[last_part] = _convert_value(value)
    else:
        data[key] = _convert_value(value)

def _convert_value(value: Any) -> Any:
    if isinstance(value, UploadFile):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
    return value


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