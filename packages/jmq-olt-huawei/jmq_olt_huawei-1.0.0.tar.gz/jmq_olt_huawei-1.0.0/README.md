# README - jmq_olt_huawei

**Paquete de integración con OLTs Huawei MA56XXT (como MA5603T) vía Telnet y SNMP asíncrono, diseñado para automatizar la recolección de información GPON desde Python.**

## 🛰️ ¿Qué hace este paquete?

Permite conectarse a una OLT Huawei MA56XXT y ejecutar operaciones como:

- Listar slots activos (`display board 0`)
- Consultar puertos GPON por slot
- Obtener ONTs conectadas a cada puerto, incluyendo:
  - Potencia TX (ptx) y RX (prx) vía SNMP asíncrono
- Realizar un escaneo completo (slots → puertos → ONTs)
- Manejar paginación, prompts dinámicos y errores comunes de sesión (bloqueo de usuario)

---

## 📦 Instalación

Requiere Python ≥ 3.7 y PySNMP ≥ 6.2 (para usar el HLAPI asíncrono).

```bash
pip install jmq_olt_huawei
````

o bien:

```bash
pip install git+https://github.com/juaquicar/jmq_olt_huawei.git
```

Para desarrollo en modo editable:

```bash
pip install -e .
```

---

## 📁 Estructura del paquete

```
jmq_olt_huawei/
│
├── ma56xxt.py          # Lógica principal de conexión Telnet y SNMP asíncrono
├── __init__.py         # Archivo de inicialización del paquete
├── Examples/           # Scripts de ejemplo (opcional)
├── tests/              # Pruebas automatizadas (pytest)
├── requirements.txt    # Dependencias de desarrollo / CI
├── pyproject.toml      # Configuración de build
├── LICENSE             # Licencia MIT
└── README.md           # Este archivo
```

---

## 🧪 Ejemplo de uso

A continuación se muestra un ejemplo mínimo de cómo usar `APIMA56XXT` con llamadas asíncronas para obtener la lista completa de ONTs y sus potencias SNMP.

```python
import asyncio
from jmq_olt_huawei.ma56xxt import APIMA56XXT, UserBusyError
from pprint import pprint

async def main():
    api = APIMA56XXT(
        host='192.168.88.25',
        user='root',
        password='admin',
        prompt='MA5603T',
        snmp_ip='192.168.88.25',
        snmp_port=161,
        snmp_community='public',
        debug=True
    )

    try:
        # Conexión Telnet (síncrona)
        api.connect()
        # Escaneo completo (async)
        full = await api.scan_all()
        pprint(full)
    except UserBusyError as e:
        print(f"ERROR: {e}")
    finally:
        api.close()  # Cierre de Telnet

if __name__ == '__main__':
    asyncio.run(main())
```

### Flujo de ejemplo

1. `api.connect()` abre una sesión Telnet, hace login, entra en modo `enable` y `config`.
2. `await api.scan_all()` recorre:

   * `get_slots()` (síncrono, Telnet)
   * Para cada slot tipo `GPBD`: `get_ports(slot)` (síncrono)
   * Para cada puerto con `optical_state == 'Online'`: `await get_onts(slot, port_id)` (asíncrono)

     * Cada ONT “online” dispara consultas SNMP asíncronas a `await _snmp_potencia_tx(...)` y `await _snmp_potencia_rx(...)`.
3. Devuelve una lista jerárquica de slots → puertos → ONTs con campos SNMP (`ptx`, `prx`).

---

## 🔍 Manual de uso de los métodos de APIMA56XXT

### 1. `__init__(host, user, password, prompt, snmp_ip, snmp_port, snmp_community, timeout=2.0, debug=False)`

Inicializa la clase:

* `host` (str): IP o hostname de la OLT.
* `user` (str): Usuario Telnet.
* `password` (str): Contraseña Telnet.
* `prompt` (str): Prefijo del prompt (p.ej. `"MA5603T"`).
* `snmp_ip` (str): IP de la OLT para SNMP.
* `snmp_port` (int): Puerto SNMP (por defecto 161).
* `snmp_community` (str): Comunidad SNMP (p.ej. `"public"`).
* `timeout` (float): Segundos de espera en lecturas Telnet (por defecto 2.0).
* `debug` (bool): Si `True`, imprime logs de depuración.

```python
api = APIMA56XXT(
    host='192.168.88.25',
    user='root',
    password='admin',
    prompt='MA5603T',
    snmp_ip='192.168.88.25',
    snmp_port=161,
    snmp_community='public',
    timeout=2.0,
    debug=True
)
```

---

### 2. `connect()`

Abre sesión Telnet, hace login y entra en modo operativo:

```python
api.connect()
# Si debug=True:
# [DEBUG] Conectando a 192.168.88.25
# Conectado en modo config
```

* No devuelve valor.
* Lanza excepción (`EOFError`, `socket.error`) si la conexión falla.
* Después de llamar, se puede invocar `get_slots()`, `get_ports()`, etc.

---

### 3. `disconnect()`

Sale de los modos CLI (`config`, `enable`) y cierra la sesión Telnet:

```python
api.disconnect()
# Si debug=True imprime:
# [DEBUG] Desconectado
```

* Protege contra llamadas dobles (si `self.tn is None`, no hace nada).

---

### 4. `get_slots() → List[Tuple[str, str]]`

Obtiene los slots en la OLT con `display board 0`:

```python
slots = api.get_slots()
# Ejemplo:
# [('0', 'GPBD'), ('6', 'SCUN'), ('7', 'SCUN'), ('9', 'GICF')]
```

* Ejecuta internamente:

  1. `_send('display board 0')`
  2. `_read_until_prompt()`
  3. Parsea cada línea para extraer `(slot_id, tipo)`.
* Es método síncrono (no necesita `await`).

---

### 5. `get_ports(slot: str) → List[dict]`

Obtiene la lista de puertos GPON de un slot específico:

```python
ports = api.get_ports('0')
# Ejemplo de un diccionario en la lista:
# {
#   'id': 0,
#   'schema_fsp': '0/0/0',
#   'optical_state': 'Online',
#   'port_state': 'Offline',
#   'laser_state': 'Normal',
#   'bw': '1239040',
#   'temperature': '35',
#   'tx_bias': '12',
#   'voltage': '3.22',
#   'tx_power': '3.72',
#   'illegal_rogue_ont': 'Inexistent',
#   'max_distance': '40',
#   'wave_length': '1490',
#   'fiber_type': 'Single Mode',
#   'length': '-'
# }
```

* Paso a paso:

  1. `_send(f'interface gpon 0/{slot}')`
  2. `_read_until_prompt()`
  3. `_send('display port state all')`
  4. `_read_until_prompt()`
  5. Parsea bloques con `_parse_port_block`.
  6. `_send('quit')` + `_read_until_prompt()`
* Retorna lista de diccionarios, uno por puerto.
* Método síncrono (no usa `await`).

---

### 6. `async get_onts(slot: str, port_id: int) → List[dict]`

Devuelve la lista de ONTs conectadas a un puerto GPON:

```python
onts = await api.get_onts('0', 0)
# Ejemplo de un diccionario ONT:
# {
#   'id': 2,
#   'schema_fsp': '0/0/0',
#   'sn': '48575443E010C4AC',
#   'control_flag': 'active',
#   'run_state': 'online',
#   'config_state': 'normal',
#   'match_state': 'match',
#   'protect_side': 'no',
#   'description': 'Cliente01',
#   'ptx': 2.34,      # Potencia TX (mW), float o "" si no está disponible
#   'prx': -21.57     # Potencia RX (dBm), float o "" si no está disponible
# }
```

* Internamente:

  1. `_send(f'interface gpon 0/{slot}')` (Telnet) + `_read_until_prompt()`
  2. `_send(f'display ont info {port_id} all')` + `_read_until_prompt()`
  3. `_send('quit')` + `_read_until_prompt()`
  4. Parsea sección principal y descripción con `_parse_onts`.
  5. Para cada ONT con `run_state.lower() == 'online'`:

     * Llama a `await _snmp_potencia_tx(slot, port_id, ont_id)`
     * Llama a `await _snmp_potencia_rx(slot, port_id, ont_id)`
  6. Si SNMP falla, asigna `""` a `ptx` y `prx`.
* Debe invocarse con `await`.
* Retorna lista de diccionarios ONT, incluyendo campos SNMP (`ptx`, `prx`).

---

### 7. `async scan_all() → List[dict]`

Realiza un escaneo completo de la OLT:

1. Obtiene todos los slots vía `get_slots()` (síncrono).
2. Para cada slot de tipo `GPBD`:

   * Llama a `get_ports(slot)` (síncrono).
   * Para cada puerto donde `optical_state.lower() == 'online'`:

     * Llama a `await get_onts(slot, port_id)` (asíncrono).
   * Agrega un campo `'onts'` a cada puerto (lista vacía si está `offline`).
3. Devuelve lista de diccionarios, cada uno así:

```jsonc
{
  "id": "0",
  "tipo": "GPBD",
  "ports": [
    {
      "id": 0,
      "schema_fsp": "0/0/0",
      "optical_state": "Online",
      "port_state": "Online",
      "laser_state": "Normal",
      "bw": "1239040",
      "temperature": "35",
      "tx_bias": "12",
      "voltage": "3.22",
      "tx_power": "3.72",
      "illegal_rogue_ont": "Inexistent",
      "max_distance": "40",
      "wave_length": "1490",
      "fiber_type": "Single Mode",
      "length": "-",
      "onts": [
        {
          "id": 2,
          "schema_fsp": "0/0/0",
          "sn": "48575443E010C4AC",
          "control_flag": "active",
          "run_state": "online",
          "config_state": "normal",
          "match_state": "match",
          "protect_side": "no",
          "description": "Cliente01",
          "ptx": 2.34,
          "prx": -21.57
        }
      ]
    },
    {
      "id": 1,
      "schema_fsp": "0/0/1",
      "optical_state": "Offline",
      "port_state": "Offline",
      // …otros campos
      "onts": []
    }
    // … más puertos
  ]
}
```

* Debe invocarse con `await api.scan_all()`.
* Incluye SNMP asíncrono para ONTs “online”.

---

## 🛠️ Métodos y privados útiles

* **`_read_until_prompt()`**
  Lee líneas desde Telnet hasta detectar el prompt dinámico. Atiende paginación (`More`, `---- More`) y errores de login acumulado (`UserBusyError`).

* **`_parse_port_block(slot, bloque)` → `dict | None`**
  Dado un bloque de texto de `display port state all`, extrae campos como `id`, `optical_state`, `laser_state`, `bw`, etc.

* **`_parse_onts(raw, slot, port_id)` → `List[dict]`**
  Dada la salida de `display ont info {port_id} all`, extrae la tabla de ONTs y sus descripciones. Devuelve lista de dicts con `id`, `sn`, `run_state`, etc.

* **`_calcular_codigo(slot, pon)` → `str`**
  Calcula la parte numérica base del OID SNMP:

  ```
  base = 4194304000
  código = base + pon_int * 256 + slot_int * 8192
  devuelve "<código>."
  ```

* **“Helpers” SNMP asíncronos (`async def`)**

  * `_consultagetsnmp(codigo_oid: str) → int | None`
    Crea un `UdpTransportTarget` con `await UdpTransportTarget.create((ip, port), timeout=1, retries=0)`, luego hace `await get_cmd(...)`.
  * `_snmp_potencia_tx(slot, port, ont) → float | ""`
    Llama a `await _consultagetsnmp(...)` con OID para potencia TX y procesa la respuesta (mW).
  * `_snmp_potencia_rx(slot, port, ont) → float | ""`
    Similar para potencia RX (dBm).

---

## ✅ Tests

Para ejecutar pruebas unitarias:

```bash
pytest -s tests/test_ma56xxt.py
```

* Asegúrate de tener un entorno de testing adecuado o mocks para Telnet/SNMP.
* Los tests deben validar parsing de puertos, ONTs y comportamiento SNMP asíncrono.

---

## 🧩 Funcionalidades destacadas

* **Prompt dinámico configurable**
  Detecta automáticamente prompts como `MA5603T>`, `MA5603T(config)#`, etc.
* **Manejo de paginación**
  Envía `\n` si detecta líneas con `More`, `---- More` o `Press 'Q'`.
* **Bloqueo de usuario**
  Si la OLT informa “Reenter times have reached the upper limit”, lanza `UserBusyError`.
* **SNMP asíncrono (PySNMP ≥ 6.2)**
  Obtiene potencias TX/RX de cada ONT “online” de forma concurrente sin bloquear la lectura Telnet.
* **Escaneo jerárquico (slots → puertos → ONTs)**
  Permite obtener toda la información en una sola llamada a `await scan_all()`.

---

## 📢 Contribuyendo

1. Haz un fork del repositorio.
2. Crea una rama:

   ```bash
   git checkout -b feature/nombre-de-funcionalidad
   ```
3. Realiza tus cambios, añade tests y actualiza este README si es necesario.
4. Haz commit y push a tu rama.
5. Abre un Pull Request describiendo los cambios propuestos.

---

## ⚖️ Licencia

MIT © [Juanma Quijada](mailto:quijada.jm@gmail.com)

---

## 🔗 Enlaces

* **Homepage / GitHub**:
  [https://github.com/juaquicar/jmq\_olt\_huawei](https://github.com/juaquicar/jmq_olt_huawei)
* **PyPI**:
  [https://pypi.org/project/jmq-olt-huawei/](https://pypi.org/project/jmq-olt-huawei/)


