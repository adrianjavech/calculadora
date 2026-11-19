# -*- coding: utf-8 -*-
"""
Registro (LOG) de uso del Sistema de Recomendación / Calculadora de Tarifas.

Cada evento se guarda como una fila en 'registro_uso.csv' (mismo folder que la app).
El CSV se abre bien en Excel (UTF-8 con BOM).
"""
import csv
import os
import threading
from datetime import datetime

ARCHIVO_LOG = "registro_uso.csv"

COLUMNAS = [
    "fecha_hora",
    "sesion_id",
    "evento",
    "plan",
    "continuidad",
    "num_asegurados",
    "edades",
    "prima_total",
    "num_cuotas",
    "financiamiento",
    "cuota_mensual",
    "detalle",
]

# Evita que dos usuarios escriban al mismo tiempo y se mezclen las filas
_lock = threading.Lock()


def registrar_evento(evento, sesion_id="", **datos):
    """
    Agrega una fila al log. Devuelve True si se guardó, False si hubo error
    (un fallo en el log nunca debe romper la app).

    Ejemplo:
        registrar_evento("Cotización calculada", sesion_id, plan="MNAC", prima_total=1200.5)
    """
    fila = {c: "" for c in COLUMNAS}
    fila.update({k: v for k, v in datos.items() if k in COLUMNAS})
    fila["fecha_hora"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fila["sesion_id"] = sesion_id
    fila["evento"] = evento

    try:
        with _lock:
            es_nuevo = not os.path.exists(ARCHIVO_LOG) or os.path.getsize(ARCHIVO_LOG) == 0
            with open(ARCHIVO_LOG, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNAS)
                if es_nuevo:
                    writer.writeheader()
                writer.writerow(fila)
        return True
    except Exception:
        return False


def leer_log():
    """Devuelve el log como DataFrame (vacío si aún no existe)."""
    import pandas as pd

    if not os.path.exists(ARCHIVO_LOG):
        return pd.DataFrame(columns=COLUMNAS)
    try:
        return pd.read_csv(ARCHIVO_LOG, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame(columns=COLUMNAS)
