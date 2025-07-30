import builtins
import base64
import openai
import os


def print(*args, **kwargs):
    """
    Reemplaza print para detectar hojas/frutos enfermos
    y añadir diagnóstico de plaga si se detecta 'enferma' en la clase.
    """
    for arg in args:
        if isinstance(arg, list):
            for item in arg:
                if isinstance(item, dict) and "clase" in item and "enferma" in item["clase"].lower():
                    image_bytes = kwargs.get("image_bytes")
                    if image_bytes:
                        try:
                            item["plaga"] = _analizar_con_openai(image_bytes)
                        except Exception as e:
                            item["plaga"] = "error"
                            builtins.print("Error al analizar imagen con OpenAI:", e)

    builtins.print(*args)


def _analizar_con_openai(image_bytes: bytes) -> str:
    """
    Analiza una imagen de granadilla para detectar si está afectada
    por trips o araña roja, según patrones visuales definidos.
    """
    api_key = "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"
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY no está definido en el entorno")

    openai.api_key = api_key
    imagen_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "Esta imagen muestra una hoja o fruto de granadilla enfermo. "
        "Analiza cuidadosamente los patrones visuales y determina si el daño se debe a trips o a araña roja.\n\n"
        "🔍 *Síntomas de trips*: manchas plateadas o bronceadas, deformaciones en hojas jóvenes, cicatrices, puntos negros.\n"
        "🕷️ *Síntomas de araña roja*: punteado clorótico (puntos amarillos), telarañas finas, decoloración progresiva, necrosis.\n\n"
        "Responde únicamente con una palabra en minúsculas: `trips` o `araña`."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}}
                ]
            }
        ],
        max_tokens=10,
    )

    return response["choices"][0]["message"]["content"].strip().lower()
