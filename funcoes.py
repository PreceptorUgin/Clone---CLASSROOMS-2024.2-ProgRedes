import os
import struct
import requests
from collections import Counter

def extrair_exif(caminho_arquivo):
    try:
        with open(caminho_arquivo, "rb") as arquivo:
            dados = arquivo.read()

            if not dados.startswith(b'\xFF\xD8'):
                return None

            offset = 2
            while offset < len(dados):
                marcador, comprimento = struct.unpack(">HH", dados[offset:offset + 4])
                if marcador == 0xFFE1:
                    if b"Exif\x00\x00" in dados[offset + 4:offset + 10]:
                        return dados[offset + 10:offset + 4 + comprimento]
                offset += 2 + comprimento

            return None
    except Exception as e:
        print(f"Erro ao ler EXIF: {e}")
        return None

def obter_informacoes_basicas(dados_exif):
    try:
        cabecalho_tiff_offset = 0
        if dados_exif[:4] == b"II*\x00":
            endian = "<"
            cabecalho_tiff_offset = struct.unpack("<I", dados_exif[4:8])[0]
        elif dados_exif[:4] == b"MM\x00*":
            endian = ">"
            cabecalho_tiff_offset = struct.unpack(">I", dados_exif[4:8])[0]
        else:
            return {}

        num_entradas = struct.unpack(f"{endian}H", dados_exif[cabecalho_tiff_offset:cabecalho_tiff_offset + 2])[0]
        informacoes = {}
        for i in range(num_entradas):
            entrada_offset = cabecalho_tiff_offset + 2 + (i * 12)
            tag, tipo_campo, contador, valor_offset = struct.unpack(f"{endian}HHII", dados_exif[entrada_offset:entrada_offset + 12])

            if tag == 0x0100:
                informacoes['largura'] = valor_offset
            elif tag == 0x0101:
                informacoes['altura'] = valor_offset
            elif tag == 0x010F:
                informacoes['fabricante'] = ler_string(dados_exif, valor_offset, endian)
            elif tag == 0x0110:
                informacoes['modelo'] = ler_string(dados_exif, valor_offset, endian)
            elif tag == 0x9003:
                informacoes['data_hora'] = ler_string(dados_exif, valor_offset, endian)

        return informacoes
    except Exception as e:
        print(f"Erro ao obter informações básicas: {e}")
        return {}

def ler_string(dados, offset, endian):
    if offset >= len(dados):
        return None
    final = dados.find(b'\x00', offset)
    return dados[offset:final].decode(errors='ignore') if final != -1 else None

def obter_latitude_longitude(dados_exif):
    try:
        cabecalho_tiff_offset = 0
        if dados_exif[:4] == b"II*\x00":
            endian = "<"
            cabecalho_tiff_offset = struct.unpack("<I", dados_exif[4:8])[0]
        elif dados_exif[:4] == b"MM\x00*":
            endian = ">"
            cabecalho_tiff_offset = struct.unpack(">I", dados_exif[4:8])[0]
        else:
            return None

        gps_ifd_offset = None
        num_entradas = struct.unpack(f"{endian}H", dados_exif[cabecalho_tiff_offset:cabecalho_tiff_offset + 2])[0]
        for i in range(num_entradas):
            entrada_offset = cabecalho_tiff_offset + 2 + (i * 12)
            tag, tipo_campo, contador, valor_offset = struct.unpack(f"{endian}HHII", dados_exif[entrada_offset:entrada_offset + 12])
            if tag == 0x8825:
                gps_ifd_offset = valor_offset
                break

        if gps_ifd_offset is None:
            return None

        gps_offset_dados = gps_ifd_offset
        gps_num_entradas = struct.unpack(f"{endian}H", dados_exif[gps_offset_dados:gps_offset_dados + 2])[0]

        latitude = longitude = None
        lat_ref = lon_ref = None

        for i in range(gps_num_entradas):
            entrada_offset = gps_offset_dados + 2 + (i * 12)
            tag, tipo_campo, contador, valor_offset = struct.unpack(f"{endian}HHII", dados_exif[entrada_offset:entrada_offset + 12])

            if valor_offset >= len(dados_exif):
                continue

            if tag == 0x0001:
                lat_ref = dados_exif[valor_offset:valor_offset + 1].decode(errors="ignore")
            elif tag == 0x0002:
                latitude = converter_coordenadas(dados_exif[valor_offset:valor_offset + 24], endian)
            elif tag == 0x0003:
                lon_ref = dados_exif[valor_offset:valor_offset + 1].decode(errors="ignore")
            elif tag == 0x0004:
                longitude = converter_coordenadas(dados_exif[valor_offset:valor_offset + 24], endian)

        if latitude and longitude:
            if lat_ref == "S":
                latitude = -latitude
            if lon_ref == "W":
                longitude = -longitude
            return latitude, longitude
        return None
    except Exception as e:
        print(f"Erro ao processar coordenadas GPS: {e}")
        return None

def converter_coordenadas(dados, endian):
    graus = struct.unpack(f"{endian}I", dados[0:4])[0] / struct.unpack(f"{endian}I", dados[4:8])[0]
    minutos = struct.unpack(f"{endian}I", dados[8:12])[0] / struct.unpack(f"{endian}I", dados[12:16])[0]
    segundos = struct.unpack(f"{endian}I", dados[16:20])[0] / struct.unpack(f"{endian}I", dados[20:24])[0]
    return graus + (minutos / 60.0) + (segundos / 3600.0)

def geocodificar(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
        resposta = requests.get(url, headers={"User-Agent": "ExifReader/1.0"})
        if resposta.status_code == 200:
            dados = resposta.json()
            endereco = dados.get("address", {})
            return endereco.get("city") or endereco.get("town") or endereco.get("village") or "Local desconhecido"
    except Exception as e:
        print(f"Erro ao geocodificar coordenadas: {e}")
    return "Local desconhecido"