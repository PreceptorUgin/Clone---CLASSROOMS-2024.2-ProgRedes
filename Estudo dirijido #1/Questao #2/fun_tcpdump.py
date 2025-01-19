import struct
import json
import os

def get_file():
    """Lê o arquivo PCAP informado pelo usuário."""
    try:
        user_input = input("Insira o arquivo ou o caminho absoluto: ")
        with open(user_input, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print("Arquivo não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")
        return None

def parse_packet_headers(data):
    """Analisa os cabeçalhos de pacotes no arquivo PCAP e retorna as estatísticas necessárias."""
    offset = 24
    PACKET_HEADER_SIZE = 16
    packets = []
    ip_interactions = {}
    largest_tcp_packet = 0
    udp_packet_sizes = []
    ip_traffic = {}
    incomplete_packets = 0

    while offset + PACKET_HEADER_SIZE <= len(data):
        packet_header = data[offset:offset + PACKET_HEADER_SIZE]
        if len(packet_header) < PACKET_HEADER_SIZE:
            print("Pacote corrompido ou incompleto.")
            break

        timestamp_sec, timestamp_usec, cap_len, orig_len = struct.unpack("<IIII", packet_header)
        packet_data = data[offset + PACKET_HEADER_SIZE:offset + PACKET_HEADER_SIZE + cap_len]

        if len(packet_data) < 20:
            print(f"Erro ao processar um pacote: Dados do pacote muito curtos para cabeçalho IP.")
            incomplete_packets += 1
            offset += PACKET_HEADER_SIZE + cap_len
            continue

        ip_header = packet_data[:20]
        try:
            ip_version, ip_header_length, ttl, protocol, checksum, src_ip, dest_ip = struct.unpack(
                "!BBHHHII", ip_header
            )
        except struct.error:
            print(f"Erro ao processar um pacote: erro ao desempacotar o cabeçalho IP.")
            offset += PACKET_HEADER_SIZE + cap_len
            continue

        src_ip = ".".join(str((src_ip >> (i << 3)) & 0xFF) for i in range(4)[::-1])
        dest_ip = ".".join(str((dest_ip >> (i << 3)) & 0xFF) for i in range(4)[::-1])

        ip_interactions[src_ip] = ip_interactions.get(src_ip, 0) + 1
        ip_interactions[dest_ip] = ip_interactions.get(dest_ip, 0) + 1

        if protocol == 6:
            tcp_header = packet_data[20:40]
            if len(tcp_header) >= 20:
                src_port, dest_port, sequence, ack, offset_reserved_flags = struct.unpack("!HHLLH", tcp_header[:14])
                largest_tcp_packet = max(largest_tcp_packet, cap_len)

        elif protocol == 17:
            udp_header = packet_data[20:28]
            if len(udp_header) >= 8:
                src_port, dest_port, length, checksum = struct.unpack("!HHHH", udp_header)
                udp_packet_sizes.append(cap_len)

        offset += PACKET_HEADER_SIZE + cap_len

    avg_udp_size = sum(udp_packet_sizes) / len(udp_packet_sizes) if udp_packet_sizes else 0

    max_traffic_ips = max(ip_interactions.items(), key=lambda x: x[1], default=(None, 0))

    return {
        "Tamanho máximo do pacote TCP": largest_tcp_packet,
        "Tamanho médio dos pacotes UDP": avg_udp_size,
        "Pacotes incompletos": incomplete_packets,
        "Interações entre IPs": ip_interactions,
        "Par de IPs com maior tráfego": max_traffic_ips,
    }

def save_results(results):
    """Salva os resultados em um arquivo JSON."""
    with open("results.json", "w") as json_file:
        json.dump(results, json_file, indent=4)

