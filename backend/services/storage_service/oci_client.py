import oci
import os

def obtener_oci():
    valores = {
        "user": os.getenv("OCI_USER_OCID"),
        "tenancy": os.getenv("OCI_TENANCY_OCID"),
        "fingerprint": os.getenv("OCI_FINGERPRINT"),
        "region": os.getenv("OCI_REGION"),
        "key_content": os.getenv("OCI_PRIVATE_KEY"),
    }
    namespace = os.getenv("OCI_NAMESPACE")
    bucket = os.getenv("OCI_BUCKET")

    if not all(valores.values()) or not namespace or not bucket:
        return None, None, None

    config = {
        "user": valores["user"],
        "tenancy": valores["tenancy"],
        "fingerprint": valores["fingerprint"],
        "region": valores["region"],
        "key_content": valores["key_content"],
    }
    try:
        oci.config.validate_config(config)
        return oci.object_storage.ObjectStorageClient(config), namespace, bucket
    except Exception as e:
        print(f"Error validating OCI config: {e}")
        return None, None, None

def subir_bytes_oci(nombre_objeto: str, contenido: bytes):
    cliente, namespace, bucket = obtener_oci()
    if cliente is None:
        return {
            "configurado": False,
            "status": "OCI no configurado o faltan variables de entorno",
            "objeto": None
        }

    try:
        cliente.put_object(namespace, bucket, nombre_objeto, contenido)
        return {
            "configurado": True,
            "status": "completado",
            "bucket": bucket,
            "objeto": nombre_objeto
        }
    except Exception as e:
        return {
            "configurado": True,
            "status": f"error: {str(e)}",
            "objeto": nombre_objeto
        }
