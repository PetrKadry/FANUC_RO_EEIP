"""
struktury pro práci s pozicemi robota FANUC ve formátu POSREGC (kartézské) a POSREGJ (kloubové).
Zahrnuje také funkce pro balení a rozbalování těchto struktur do binárné podoby pro komunikaci
s robotem pomocí Ethernet/IP.
Tyto struktury a funkce jsou navrženy tak, aby odpovídaly formátu používanému roboty FANUC,
což umožňuje snadnou integraci do projektů, které potřebují pracovat s pozicemi jako POSREGC.
"""

# =========================
# fanuc/posreg.py
# =========================
from .serializer import StructSerializer, Field

# POSREGC (Cartesian - Fanuc compatible layout)
POSREGC = StructSerializer(
    [
        Field("UF", "H"),
        Field("UT", "H"),
        Field("XYZWPR", "f", 6),
        Field("TURN", "b", 3),
        Field("FLAGS", "B"),  # packed bitfield
        Field("EXT", "f", 3),
    ]
)

# POSREGJ (Joint)
POSREGJ = StructSerializer(
    [
        Field("UF", "H"),
        Field("UT", "H"),
        Field("JNT", "f", 9),
    ]
)


# Funkce pro balení a rozbalování POSREGC dat do binární podoby pro komunikaci s robotem
def _pack_flags(front, up, left, flip):
    flags = 0
    flags |= (front & 1) << 4
    flags |= (up & 1) << 5
    flags |= (left & 1) << 6
    flags |= (flip & 1) << 7
    return flags


# Funkce pro rozbalování bitového pole FLAGS do jednotlivých komponent Front, Up, Left, Flip
def _unpack_flags(flags):
    return {
        "Front": (flags >> 4) & 1,
        "Up": (flags >> 5) & 1,
        "Left": (flags >> 6) & 1,
        "Flip": (flags >> 7) & 1,
    }


# Funkce pro balení dat do formátu POSREGC pro zápis do PR[] nebo odeslání robotu
def pack_posregc(
    uf=255, ut=255,
    x=0, y=0, z=0,
    w=0, p=0, r=0, 
    turn1=0, turn2=0, turn3=0,
    front=1, up=1, left=0, flip=0,
    ext1=0, ext2=0, ext3=0,
):

    return POSREGC.pack(
        UF=uf,
        UT=ut,
        XYZWPR=(x, y, z, w, p, r),
        TURN=(turn1, turn2, turn3),
        FLAGS=_pack_flags(front, up, left, flip),
        EXT=(ext1, ext2, ext3),
    )


# Funkce pro rozbalování dat z formátu POSREGC načtených z PR[] nebo od robota
def unpack_posregc(data):
    raw = POSREGC.unpack(data)

    flags = _unpack_flags(raw["FLAGS"])

    return {
        "UF": raw["UF"],
        "UT": raw["UT"],
        "X": raw["XYZWPR"][0],
        "Y": raw["XYZWPR"][1],
        "Z": raw["XYZWPR"][2],
        "W": raw["XYZWPR"][3],
        "P": raw["XYZWPR"][4],
        "R": raw["XYZWPR"][5],
        "Turn1": raw["TURN"][0],
        "Turn2": raw["TURN"][1],
        "Turn3": raw["TURN"][2],
        **flags,
        "EXT": raw["EXT"],
    }
