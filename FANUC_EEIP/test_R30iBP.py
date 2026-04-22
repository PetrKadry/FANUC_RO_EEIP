"""
Testování komunikace s robotem FANUC R30iB Plus pomocí EEIPClient z knihovny eeip.py.
https://github.com/rossmann-engineering/eeip.py.git

Základní funkce pro čtení a zápis dat z/do registrů R[] a PR[] 
pomocí EEIPClient a pro práci s pozicemi jako POSREGC.
Používá se pro testování komunikace a základních operací s robotem přes Ethernet/IP. 
Pro komplexnější aplikace lze tento modul rozšířit o další funkce pro práci 
s různými datovými typy a registry robota.
"""

# EEIPClient pro komunikaci s robotem pomocí Ethernet/IP
#   git clone https://github.com/rossmann-engineering/eeip.py.git
#   cd eeip.py
#   python setup.py install
# nebo ve .venv:
#   cd /cesta/k/muj-gitovy-projekt
#   python -m venv .venv
#   git clone https://github.com/rossmann-engineering/eeip.py.git
#   .venv\Scripts\activate   # nebo .venv\Scripts\activate na Windows
#   eeip nemá setup.py -> vytvořit
#           from setuptools import setup, find_packages
#           setup(
#               name="eeip",
#               version="0.1",
#               packages=["eeip"],
#               package_dir={"eeip": "eeip"},  # pokud máš /eeip/eeip/*.py
#           )
#   cd eeip.py
#   pip install -e .   # nainstaluje eeip jako lokální balíček
#   deaktivovat virtuální prostředí: deactivate

from eeip import EEIPClient
from fanuc.posreg import POSREGC, POSREGJ, pack_posregc, unpack_posregc
import struct

ROBOT_IP = "10.209.26.201"

def set_int_to_r(eeip: EEIPClient, r_index: int, value: int):
    """Zápis celočíselné hodnoty do registru R[] jako INT (4 bajty)"""

    eeip.set_attribute_single(0x6B, 1, r_index, list(struct.pack("<i", value)))


def set_real_to_r(eeip: EEIPClient, r_index: int, value: float):
    """Zápis reálné hodnoty do registru R[] jako REAL (4 bajty)"""

    eeip.set_attribute_single(0x6C, 1, r_index, list(struct.pack("<f", value)))


def set_posc_to_pr(eeip: EEIPClient, pr_index: int, pos_data: list, validate=False):
    """Zápis pozice do registru PR[] jako POGREGC"""

    eeip.set_attribute_single(0x7B, 1, pr_index, pos_data)
    if validate:
        response = eeip.get_attribute_single(0x7B, 1, pr_index)
        if response != pos_data:
            return 1
        else:
            return 0
    else:
        return 0


def get_int_from_r(eeip: EEIPClient, r_index: int):
    """Čtení celočíselné hodnoty z registru R[] jako INT (4 bajty)"""

    response = eeip.get_attribute_single(0x6B, 1, r_index)
    return struct.unpack("<i", bytes(response[:4]))[0]


def get_real_from_r(eeip: EEIPClient, r_index: int):
    """Čtení reálné hodnoty z registru R[] jako REAL (4 bajty)"""

    response = eeip.get_attribute_single(0x6C, 1, r_index)
    return struct.unpack("<f", bytes(response[:4]))[0]


def get_curposc(eeip: EEIPClient):
    """Čtení aktuální pozice CURPOS jako POGREGC"""

    response = eeip.get_attribute_single(0x7D, 1, 1)
    return unpack_posregc(response)


def get_pr_posc(eeip: EEIPClient, pr_index: int):
    """Čtení pozice z registru PR[] jako POGREGC"""

    response = eeip.get_attribute_single(0x7B, 1, pr_index)
    return unpack_posregc(response)


def test_communication():
    print("Test komunikace s robotem FANUC R30iB Plus pomocí EEIPClient...")

    # REAL z R[5]
    # response = eeip.get_attribute_single(0x6C, 1, 5)
    response = get_int_from_r(eeip, 5)
    print(f"R[5] (float)= {response}")

    # REAL do R[4]
    R_VALUE = 42.444
    # eeip.set_attribute_single(0x6C, 1, 4,list(struct.pack("<f", R_VALUE)))
    set_int_to_r(eeip, 4, int(R_VALUE))  # pro porovnání zápisu jako Int
    print(f"Hodnota {R_VALUE} (float) zapsána do R[4]")

    # INT z R[2]
    # response = eeip.get_attribute_single(0x6B, 1, 2)
    response = get_int_from_r(eeip, 2)
    print(f"R[2] (int) = {response}")

    # INT do R[3]
    int_value = 1112111
    # eeip.set_attribute_single(0x6B, 1, 3,list(struct.pack("<i", int_value)))
    set_int_to_r(eeip, 3, int_value)  # pro porovnání zápisu jako Int
    print(f"{int_value} (int) zapsán do R[3]\n")

    # CURPOS jako POSREGC
    # response = eeip.get_attribute_single(0x7D, 1, 1)
    response = get_curposc(eeip)
    print(f"načteno z PR[1]: {response}\n")

    # pos_data =pack_posregc(
    #     uf=255, ut=255,
    #     x=1, y=2, z=3,
    #     w=4, p=5, r=6,
    #     turn1=1, turn2=2, turn3=3,
    #     front=1, up=1, left=0, flip=0,
    #     ext1=0, ext2=0, ext3=0
    # )
    # data pro pozici lze zjednodušit vynecháním argumentů pro výchozí hodnoty pro UF, UT, turny a flags
    # POZOR! PR při zápisu kartézských dat nesmí být v jointech!
    # UF a UT do PR vždy 255 (default hodnota) - neaktivní
    pos_data = pack_posregc(
        x=1.111,
        y=2.222,
        z=3.333,
        w=4.444,
        p=5.555,
        r=6.666,
    )

    # Explicitní zápis dat do PR[3] jako POGREGC (Class 0x7B, Instance 1, Attribute 3)
    # eeip.set_attribute_single(0x7B, 1, 3, pos_data)
    # set_posc_to_pr(eeip, 3, pos_data) == 0
    if set_posc_to_pr(eeip, 3, pos_data, validate=True) == 0:
        print(f"do PR[3] úspěšně zapsáno: {unpack_posregc(pos_data)}\n")
    else:
        print("Zápis do PR[3] se nezdařil - hodnoty se neshodují po ověření.\n")


if __name__ == "__main__":
    eeip = EEIPClient()
    print(f"Registrace session s Fanucem... ({ROBOT_IP})\n")
    eeip.register_session(ROBOT_IP)

    try:
        test_communication()

    finally:
        eeip.unregister_session()
        print(f"Session s {ROBOT_IP} uzavřena.")
