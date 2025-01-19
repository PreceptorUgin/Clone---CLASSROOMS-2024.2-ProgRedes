import struct
import json

def getFile():
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
    """Analisa os cabeçalhos de pacotes no arquivo PCAP."""
    offset = 24  # Pular o cabeçalho PCAP
    PACKET_HEADER_SIZE = 16
    packets = []
    ip_interactions = {}
    largest_tcp_packet = 0
    udp_packet_sizes = []
    ip_traffic = {}

    while offset + PACKET_HEADER_SIZE <= len(data):
        # Lê o cabeçalho do pacote
        packet_header = data[offset:offset + PACKET_HEADER_SIZE]

        if len(packet_header) < PACKET_HEADER_SIZE:
            print("Pacote corrompido ou incompleto.")
            break

        # Interpreta o cabeçalho
        timestamp_sec, timestamp_usec, cap_len, orig_len = struct.unpack("<IIII", packet_header)
        packet_data = data[offset + PACKET_HEADER_SIZE:offset + PACKET_HEADER_SIZE + cap_len]

        # Garantir que temos dados suficientes para processar (cabeçalho IP)
        if len(packet_data) < 20:  # Cabeçalho IP tem 20 bytes no mínimo
            print(f"Erro ao processar um pacote: Dados do pacote muito curtos para cabeçalho IP.")
            offset += PACKET_HEADER_SIZE + cap_len
            continue

        # Analisar cabeçalho IP
        ip_header = packet_data[:20]  # Cabeçalho IP (20 bytes)
        try:
            ip_version, ip_header_length, ttl, protocol, checksum, src_ip, dest_ip = struct.unpack(
                "!BBHHHII", ip_header
            )
        except struct.error:
            print(f"Erro ao processar um pacote: erro ao desempacotar o cabeçalho IP.")
            offset += PACKET_HEADER_SIZE + cap_len
            continue

        # Converter os endereços IP para formato legível
        src_ip = ".".join(str((src_ip >> (i << 3)) & 0xFF) for i in range(4)[::-1])
        dest_ip = ".".join(str((dest_ip >> (i << 3)) & 0xFF) for i in range(4)[::-1])

        # Aumenta o contador de interações entre IPs
        ip_interactions[src_ip] = ip_interactions.get(src_ip, 0) + 1
        ip_interactions[dest_ip] = ip_interactions.get(dest_ip, 0) + 1

        # Se o protocolo for TCP ou UDP
        if protocol == 6:  # TCP
            tcp_header = packet_data[20:40]  # Cabeçalho TCP
            if len(tcp_header) >= 20:  # Verificar se o cabeçalho TCP é completo
                src_port, dest_port, sequence, ack, offset_reserved_flags = struct.unpack("!HHLLH", tcp_header[:14])
                # Calcular o tamanho do maior pacote TCP
                largest_tcp_packet = max(largest_tcp_packet, cap_len)

        elif protocol == 17:  # UDP
            udp_header = packet_data[20:28]  # Cabeçalho UDP
            if len(udp_header) >= 8:  # Verificar se o cabeçalho UDP é completo
                src_port, dest_port, length, checksum = struct.unpack("!HHHH", udp_header)
                udp_packet_sizes.append(cap_len)  # Adicionar o tamanho do pacote UDP

        offset += PACKET_HEADER_SIZE + cap_len

    # Calcular o tamanho médio dos pacotes UDP
    avg_udp_size = sum(udp_packet_sizes) / len(udp_packet_sizes) if udp_packet_sizes else 0

    # Encontrar o par de IPs com maior tráfego
    max_traffic_ips = max(ip_traffic.items(), key=lambda x: x[1], default=(None, 0))

    return {
        "Tamanho máximo do pacote TCP": largest_tcp_packet,
        "Tamanho médio dos pacotes UDP": avg_udp_size,
        "Interações entre IPs": ip_interactions,
        "Par de IPs com maior tráfego": max_traffic_ips,
    }


def save_results(results):
    """Salva os resultados em um arquivo JSON."""
    with open("results.json", "w") as json_file:
        json.dump(results, json_file, indent=4)
