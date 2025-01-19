import sys
import scan

host = input("Digite o IP ou o hostname do servidor a ser testado: ")
try:
    scan.verificarPortas(host)
except Exception as e:
    print(f"Erro fatal: {str(e)}")
    sys.exit(1)