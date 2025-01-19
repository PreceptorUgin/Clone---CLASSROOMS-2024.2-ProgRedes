from fun_tcpdump import *
import json
import sys

data = get_file()
if not data:
    sys.exit()

print(f"{'-'*12} Analisando pacotes {'-'*12}")
results = parse_packet_headers(data)

print(f"Tamanho máximo de pacote TCP: {results['Tamanho máximo do pacote TCP']}")
print(f"Tamanho médio de pacotes UDP: {results['Tamanho médio dos pacotes UDP']}")
print(f"Pacotes incompletos: {results['Pacotes incompletos']}")
print(f"Interações entre IPs: {results['Interações entre IPs']}")
print(f"Par de IPs com maior tráfego: {results['Par de IPs com maior tráfego']}")

save_results(results)