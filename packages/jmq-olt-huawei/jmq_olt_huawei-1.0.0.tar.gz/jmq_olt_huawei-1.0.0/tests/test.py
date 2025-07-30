import time
from jmq_olt_huawei.ma56xxt import APIMA56XXT, UserBusyError
import asyncio
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
        api.connect()
        # Empieza cronómetro
        t0 = time.perf_counter()
        full = await api.scan_all()
        # full = await api.get_onts("0", 0)
        # Para cronómetro
        t1 = time.perf_counter()
        pprint(full)
        print(f"\nTiempo de scan_all(): {t1 - t0:.3f} segundos")
    except UserBusyError as e:
        print(f"ERROR: {e}")
    finally:
        api.close()

if __name__ == '__main__':
    asyncio.run(main())
