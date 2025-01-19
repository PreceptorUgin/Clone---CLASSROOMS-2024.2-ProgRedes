from fun_tcpdump import *
import json

def main():
    """Função principal para execução do programa."""
    data = getFile()

    if not data:
        return

    print(f"{'-'*12} Analisando pacotes {'-'*12}")
    results = parse_packet_headers(data)

    # Exibir resultados no console
    print(f"Tamanho máximo de pacote TCP: {results['Tamanho máximo do pacote TCP']}")
    print(f"Tamanho médio de pacotes UDP: {results['Tamanho médio dos pacotes UDP']}")
    print(f"Interações entre IPs: {results['Interações entre IPs']}")
    print(f"Par de IPs com maior tráfego: {results['Par de IPs com maior tráfego']}")

    # Salvar resultados em JSON
    save_results(results)

main()
