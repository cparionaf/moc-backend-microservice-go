from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import os
import requests
from botocore.config import Config

app = FastAPI(title="AWS Instance Info API")

# Modelo Pydantic para la respuesta
class ServerInfo(BaseModel):
    region: Optional[str] = None
    availability_zone: Optional[str] = None
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None
    timestamp: datetime

# Cliente para metadata de instancia EC2
METADATA_BASE_URL = "http://169.254.169.254/latest/meta-data"

def get_instance_metadata(path: str) -> Optional[str]:
    """
    Obtiene metadata de la instancia EC2 usando el servicio IMDS
    """
    try:
        response = requests.get(f"{METADATA_BASE_URL}/{path}", timeout=2)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        print(f"Error al obtener metadata {path}: {e}")
    return None

@app.get("/info", response_model=ServerInfo)
async def get_server_info():
    """
    Endpoint que retorna información detallada sobre la instancia EC2 y su región
    """
    try:
        # Inicializar boto3 con configuración por defecto
        session = boto3.Session()
        
        # Obtener información de la instancia usando IMDS
        instance_id = get_instance_metadata("instance-id")
        instance_type = get_instance_metadata("instance-type")
        availability_zone = get_instance_metadata("placement/availability-zone")
        
        # Determinar la región
        region = None
        if availability_zone:
            # La región es la AZ sin la última letra
            region = availability_zone[:-1]
        else:
            # Fallback a la región de la sesión
            region = session.region_name
        
        # Construir respuesta
        server_info = ServerInfo(
            region=region,
            availability_zone=availability_zone,
            instance_id=instance_id,
            instance_type=instance_type,
            timestamp=datetime.now()
        )
        
        return server_info
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener información del servidor: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)