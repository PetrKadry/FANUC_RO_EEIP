# =========================
# fanuc/serializer.py
# =========================
import struct
from dataclasses import dataclass

# Tento modul obsahuje základní třídy a funkce pro serializaci 
# a deserializaci datových struktur používaných v komunikaci s roboty FANUC.
# Obsahuje třídu Field pro definici jednotlivých polí a třídu StructSerializer 
# pro balení a rozbalování dat podle definovaných struktur.
# Tyto třídy umožňují snadné definování komplexních datových struktur, 
# které odpovídají formátu používanému roboty FANUC 
# a jejich převod do binární podoby pro komunikaci pomocí Ethernet/IP.
@dataclass
class Field:
    name: str
    fmt: str
    count: int = 1

# Třída pro serializaci a deserializaci datových struktur
class StructSerializer:
    def __init__(self, fields):
        self.fields = fields

        self.format = "<" + "".join(
            f"{f.count}{f.fmt}" if f.count > 1 else f.fmt
            for f in fields
        )

        self.size = struct.calcsize(self.format)

    # Funkce pro balení dat do binární podoby podle definovaných polí
    def pack(self, **kwargs):
        values = []

        for f in self.fields:
            v = kwargs[f.name]

            if f.count > 1:
                if len(v) != f.count:
                    raise ValueError(f"{f.name} must have {f.count} elements")
                values.extend(v)
            else:
                values.append(v)

        return list(struct.pack(self.format, *values))

    # Funkce pro rozbalování dat z binární podoby do slovníku podle definovaných polí
    def unpack(self, data):
        raw = struct.unpack(self.format, bytes(data))

        out = {}
        i = 0

        for f in self.fields:
            if f.count > 1:
                out[f.name] = raw[i:i+f.count]
                i += f.count
            else:
                out[f.name] = raw[i]
                i += 1

        return out