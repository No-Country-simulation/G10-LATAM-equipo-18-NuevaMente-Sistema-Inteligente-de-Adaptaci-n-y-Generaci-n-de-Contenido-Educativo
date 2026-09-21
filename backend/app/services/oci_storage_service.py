import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("OCIStorageService")

class OCIStorageService:
    def __init__(self):
        self.config_path = os.path.expanduser("~/.oci/config")
        self.is_connected = False
        self.client = None
        self.namespace = "mock-oci-namespace"
        
        if os.path.exists(self.config_path):
            try:
                import oci
                self.config = oci.config.from_file(self.config_path)
                self.client = oci.object_storage.ObjectStorageClient(self.config)
                self.namespace = self.client.get_namespace().data
                self.is_connected = True
                logger.info("Conexión con Oracle Cloud OCI Object Storage establecida.")
            except Exception as e:
                logger.warning(f"No se pudo conectar a OCI Object Storage via SDK: {e}. Usando fallback local.")
        else:
            logger.info("Archivo ~/.oci/config no encontrado. OCI Storage operará en modo Local Mock (Always Free Compatible).")

    def upload_json_artifact(self, bucket_name: str, object_name: str, json_data: dict) -> Dict[str, Any]:
        """
        Guarda el objeto JSON en el bucket de OCI Object Storage.
        Si la conexión OCI no está activa, persiste en storage_mock/ local.
        """
        if self.is_connected and self.client:
            try:
                body = json.dumps(json_data, ensure_ascii=False, indent=2).encode('utf-8')
                self.client.put_object(self.namespace, bucket_name, object_name, body)
                return {
                    "bucket": bucket_name,
                    "objeto_id": object_name,
                    "status_upload": "completado"
                }
            except Exception as e:
                logger.error(f"Error subiendo objeto a OCI: {e}")

        # Fallback local mock
        base_dir = os.path.join(os.getcwd(), "storage_mock", bucket_name)
        os.makedirs(base_dir, exist_ok=True)
        file_path = os.path.join(base_dir, object_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            
        return {
            "bucket": bucket_name,
            "objeto_id": object_name,
            "status_upload": "completado"
        }
