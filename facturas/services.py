import uuid
import time
import logging

logger = logging.getLogger(__name__)

#esto se usa para simular el envio de la factura a la empresa intermediaria como prueba , 
def enviar_a_intermediario(factura):
    """
    Simula el envío a una empresa intermediaria .
    Retorna un 'CUFE' simulado.
    """
    # Simular retardo
    time.sleep(1)
    cufe = str(uuid.uuid4())

    #  Usamos el ID real de la factura
    factura_id = getattr(factura, "id", None) or getattr(factura, "id_factura", None)
    logger.info(f"Intermediario simul: factura {factura_id} -> cufe {cufe}")

    return cufe