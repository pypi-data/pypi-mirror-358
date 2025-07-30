import telnetlib
import re
import asyncio

from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    CommunityData,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    UdpTransportTarget,
)

from pprint import pprint


class UserBusyError(Exception):
    """Raised when la OLT indica que los intentos de login están bloqueados."""
    pass


class APIMA56XXT:
    """
    Clase optimizada para conectarse a una OLT vía Telnet y consultar:
      - Slots PON
      - Puertos GPON
      - ONTs y, si están Online, sus potencias TX/RX vía SNMP

    Ahora precompila expresiones regulares y OID bases en el init para mejorar rendimiento,
    y usa patrones en bytes para telnetlib.expect.
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        prompt: str,
        snmp_ip: str,
        snmp_port: int,
        snmp_community: str,
        timeout: float = 1,
        debug: bool = False,
    ):
        # Parámetros Telnet
        self.host = host
        self.user = user
        self.password = password
        self.timeout = timeout
        self.debug = debug
        self.tn = None

        # Regex precompiladas sobre strings
        prompt_pattern = rf"^{re.escape(prompt)}(?:\([^)]+\))?[>#]"
        self.ansi_re = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

        # Regex precompiladas sobre bytes para telnetlib.expect
        self.error_re = re.compile(br"^%.*")
        self.more_re = re.compile(br"More|Press 'Q'|---- More")
        self.prompt_re = re.compile(prompt_pattern.encode())

        # Patrón para parsing de 'display board 0'
        self.slot_pattern = re.compile(r"^\s*(\d+)\s+H\d+([A-Z]+)")
        # Patrón para parsing de bloques de puerto GPON (F/S/P header)
        self.block_header_re = re.compile(r"^0/(\d+)/(\d+)")

        # Parámetros SNMP
        self.snmp_ip = snmp_ip
        self.snmp_port = snmp_port or 161
        self.snmp_community = snmp_community
        # OID base para TX y RX
        self.oid_tx_prefix = ".1.3.6.1.4.1.2011.6.128.1.1.2.51.1.6."
        self.oid_rx_prefix = ".1.3.6.1.4.1.2011.6.128.1.1.2.51.1.4."

    def _log(self, *args):
        if self.debug:
            print("[DEBUG]", *args)

    def _read_line(self) -> str:
        raw = self.tn.read_until(b"\n", timeout=self.timeout)
        text = raw.decode("utf-8", errors="ignore")
        return self.ansi_re.sub("", text).rstrip()

    def _read_until_prompt(self) -> str:
        # Usamos patrones en bytes para expect
        patterns = [self.error_re, self.more_re, self.prompt_re]
        idx, match, chunk = self.tn.expect(patterns, timeout=self.timeout)
        text = self.ansi_re.sub('', chunk.decode('utf-8', 'ignore')).rstrip()

        if idx == 1:
            # Paginación
            self._log("Paginación detectada, ENTER")
            self.tn.write(b"\n")
            return text + "\n" + self._read_until_prompt()

        return text

    def connect(self):
        """Conecta por Telnet, hace login y entra en modo config."""
        self._log("Conectando a", self.host)
        self.tn = telnetlib.Telnet(self.host)

        # Login
        self.tn.read_until(b"User name:", timeout=self.timeout)
        self.tn.write(self.user.encode() + b"\n")
        self.tn.read_until(b"User password:", timeout=self.timeout)
        self.tn.write(self.password.encode() + b"\n")

        self._read_until_prompt()

        # Enable + config
        for cmd in ('enable', 'config'):
            self._send(cmd)
            self._read_until_prompt()

        print("Conectado en modo config")

    def close(self):
        """Cierra la conexión Telnet directamente."""
        if self.tn:
            self.tn.close()
        self.tn = None
        self._log("Desconectado")

    def disconnect(self):
        """Sale de config/enable y cierra Telnet con confirmación."""
        if not self.tn:
            return
        for _ in range(2):
            self._send('quit')
            self._read_until_prompt()
        # Confirm quit enable
        self._send('quit')
        try:
            confirm = self.tn.read_until(b"(y/n)", timeout=self.timeout).decode()
            self._log(f"Confirm prompt: {confirm.strip()}")
            self.tn.write(b"y\n")
        except Exception:
            pass
        self.tn.close()
        self.tn = None
        self._log("Desconectado")

    def _send(self, cmd: str):
        self._log(f"Enviando comando: {cmd}")
        self.tn.write(cmd.encode() + b"\n")

    def get_slots(self) -> list[tuple[str, str]]:
        self._send('display board 0')
        raw = self._read_until_prompt()
        slots = []
        for line in raw.splitlines():
            m = self.slot_pattern.match(line)
            if m:
                slots.append((m.group(1), m.group(2)))
        return slots

    def get_ports(self, slot: str) -> list[dict]:
        self._send(f'interface gpon 0/{slot}')
        self._read_until_prompt()
        self._send('display port state all')
        raw = self._read_until_prompt()

        ports = []
        for bloque in raw.split('F/S/P')[1:]:
            info = self._parse_port_block(slot, bloque)
            if info:
                ports.append(info)

        self._send('quit')
        self._read_until_prompt()
        return ports

    async def get_onts(self, slot: str, port_id: int) -> list[dict]:
        self._send(f'interface gpon 0/{slot}')
        self._read_until_prompt()
        self._send(f'display ont info {port_id} all')
        raw = self._read_until_prompt()
        self._send('quit')
        self._read_until_prompt()

        onts = self._parse_onts(raw, slot, port_id)
        for ont in onts:
            if ont.get('run_state', '').lower() == 'online':
                try:
                    ptx = await self._snmp_potencia_tx(slot, port_id, ont['id'])
                    prx = await self._snmp_potencia_rx(slot, port_id, ont['id'])
                    ont['ptx'] = ptx
                    ont['prx'] = prx
                except Exception as e:
                    self._log(f"Error SNMP ONT {slot}/{port_id}/{ont['id']}: {e}")
                    ont['ptx'] = ''
                    ont['prx'] = ''
            else:
                ont['ptx'] = ''
                ont['prx'] = ''
        return onts

    async def scan_all(self) -> list[dict]:
        result = []
        for slot, tipo in self.get_slots():
            entry = {'id': slot, 'tipo': tipo, 'ports': []}
            if tipo == 'GPBD':
                for port in self.get_ports(slot):
                    if port.get('optical_state', '').lower() == 'online':
                        port['onts'] = await self.get_onts(slot, port['id'])
                    else:
                        port['onts'] = []
                    entry['ports'].append(port)
            result.append(entry)
        return result

    def _parse_port_block(self, slot: str, bloque: str) -> dict | None:
        lines = bloque.strip().splitlines()
        m = self.block_header_re.match(lines[0].strip())
        if not m or m.group(1) != slot:
            return None
        pid = int(m.group(2))
        data = {key: None for key in [
            'id', 'schema_fsp', 'optical_state', 'port_state', 'laser_state',
            'bw', 'temperature', 'tx_bias', 'voltage', 'tx_power',
            'illegal_rogue_ont', 'max_distance', 'wave_length', 'fiber_type', 'length'
        ]}
        data.update({'id': pid, 'schema_fsp': f"0/{slot}/{pid}"})
        for l in lines:
            parts = l.split()
            if 'Optical Module status' in l:
                data['optical_state'] = parts[-1]
            elif 'Port state' in l:
                data['port_state'] = parts[-1]
            elif 'Laser state' in l:
                data['laser_state'] = parts[-1]
            elif 'Available bandwidth' in l:
                data['bw'] = parts[-1]
            elif 'Temperature' in l:
                data['temperature'] = parts[-1]
            elif 'TX Bias' in l:
                data['tx_bias'] = parts[-1]
            elif 'Supply Voltage' in l:
                data['voltage'] = parts[-1]
            elif 'TX power' in l:
                data['tx_power'] = parts[-1]
            elif 'Illegal rogue ONT' in l:
                data['illegal_rogue_ont'] = parts[-1]
            elif 'Max Distance' in l:
                data['max_distance'] = parts[-1]
            elif 'Wave length' in l:
                data['wave_length'] = parts[-1]
            elif 'Fiber type' in l:
                data['fiber_type'] = parts[-1]
            elif 'Length' in l:
                data['length'] = parts[-1]
        return data

    def _parse_onts(self, raw: str, slot: str, port_id: int) -> list[dict]:
        onts, in_main, in_desc = [], False, False
        lines = raw.splitlines()
        base_fsp = f"0/{slot}/{port_id}"
        for ln in lines:
            if ln.startswith('  F/S/P') and 'ONT' in ln and 'SN' in ln:
                in_main = True
                continue
            if in_main and ln.strip():
                parts = ln.split()
                if len(parts) >= 9 and parts[1].startswith(f"{slot}/"):
                    try:
                        oid = int(parts[2])
                    except ValueError:
                        continue
                    entry = {
                        'id': oid,
                        'schema_fsp': base_fsp,
                        'sn': parts[3],
                        'control_flag': parts[4],
                        'run_state': parts[5],
                        'config_state': parts[6],
                        'match_state': parts[7],
                        'protect_side': parts[8],
                        'description': None
                    }
                    onts.append(entry)
                    continue
            if ln.startswith('  F/S/P') and 'Description' in ln:
                in_desc, in_main = True, False
                continue
            if in_desc and ln.strip():
                parts = ln.split(maxsplit=3)
                if len(parts) == 4 and parts[0].startswith('0/'):
                    try:
                        oid = int(parts[2])
                    except ValueError:
                        continue
                    for o in onts:
                        if o['id'] == oid:
                            o['description'] = parts[3]
                            break
        return onts

    async def _consultagetsnmp(self, codigo_oid: str):
        transport = await UdpTransportTarget.create(
            (self.snmp_ip, self.snmp_port),
            timeout=1,
            retries=0
        )
        iterator = get_cmd(
            SnmpEngine(),
            CommunityData(self.snmp_community),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(codigo_oid))
        )
        error_indication, error_status, error_index, var_binds = await iterator
        if error_indication or error_status:
            return None
        for var_bind in var_binds:
            return var_bind[1]
        return None

    async def _snmp_potencia_tx(self, slot: int | str, port: int, ont: int) -> float | str:
        cod_full = self.oid_tx_prefix + self._calcular_codigo(slot, port) + str(ont)
        valor = await self._consultagetsnmp(cod_full)
        if valor is None:
            return ""
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            return ""
        poten = round(int(valor) / 1000, 2)
        return "" if val_int == 2147483647 or poten == -0.0 else poten

    async def _snmp_potencia_rx(self, slot: int | str, port: int, ont: int) -> float | str:
        cod_full = self.oid_rx_prefix + self._calcular_codigo(slot, port) + str(ont)
        valor = await self._consultagetsnmp(cod_full)
        if valor is None:
            return ""
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            return ""
        poten = round(int(valor) / 100, 2)
        return "" if val_int == 2147483647 or poten == -0.01 else poten

    def _calcular_codigo(self, slot: int | str, pon: int | str) -> str:
        num = 4194304000
        return f"{num + int(pon) * 256 + int(slot) * 8192}."


if __name__ == '__main__':
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

    async def main():
        try:
            api.connect()
            full = await api.scan_all()
            pprint(full)
        except UserBusyError as e:
            print(f"ERROR: {e}")
        finally:
            api.close()

    asyncio.run(main())
