import socket
import json
import sys

'''Função para verificar o status da porta TCP'''
def verificarTCP(host, porta):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketObj:
            socketObj.settimeout(1)
            resultado = socketObj.connect_ex((host, porta))
            return "OK" if resultado == 0 else f"Erro {resultado}"
    except Exception as e:
        print(f"Erro ao verificar TCP na porta {porta}: {str(e)}")
        return f"Erro: {str(e)}"

'''Função para verificar o status da porta UDP'''
def verificarUDP(host, porta):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketObj:
            socketObj.settimeout(1)
            socketObj.sendto(b'', (host, porta))
            socketObj.recvfrom(1024)
            return "OK"
    except socket.timeout:
        return "Erro: Timeout"
    except Exception as e:
        print(f"Erro ao verificar UDP na porta {porta}: {str(e)}")
        return f"Erro: {str(e)}"

'''Função principal'''
def verificarPortas(host):
    portas = [
        # Protocolos TCP
        {'porta': 21, 'protocolo': 'TCP – FTP', 'descricao': 'File Transfer Protocol'},
        {'porta': 22, 'protocolo': 'TCP – SSH', 'descricao': 'Secure Shell'},
        {'porta': 23, 'protocolo': 'TCP – Telnet', 'descricao': 'Telnet protocol'},
        {'porta': 25, 'protocolo': 'TCP – SMTP', 'descricao': 'Simple Mail Transfer Protocol'},
        {'porta': 53, 'protocolo': 'TCP – DNS', 'descricao': 'Domain Name System'},
        {'porta': 80, 'protocolo': 'TCP – HTTP', 'descricao': 'Hypertext Transfer Protocol'},
        {'porta': 110, 'protocolo': 'TCP – POP3', 'descricao': 'Post Office Protocol v3'},
        {'porta': 143, 'protocolo': 'TCP – IMAP', 'descricao': 'Internet Message Access Protocol'},
        {'porta': 443, 'protocolo': 'TCP – HTTPS', 'descricao': 'HTTP Secure'},
        {'porta': 3389, 'protocolo': 'TCP – RDP', 'descricao': 'Remote Desktop Protocol'},
        {'porta': 8080, 'protocolo': 'TCP – HTTP-Alt', 'descricao': 'HTTP alternative port'},
        
        # Protocolos UDP
        {'porta': 53, 'protocolo': 'UDP – DNS', 'descricao': 'Domain Name System'},
        {'porta': 67, 'protocolo': 'UDP – DHCP', 'descricao': 'Dynamic Host Configuration Protocol'},
        {'porta': 123, 'protocolo': 'UDP – NTP', 'descricao': 'Network Time Protocol'},
        {'porta': 161, 'protocolo': 'UDP – SNMP', 'descricao': 'Simple Network Management Protocol'},
        {'porta': 162, 'protocolo': 'UDP – SNMPTRAP', 'descricao': 'SNMP Trap'},
        {'porta': 514, 'protocolo': 'UDP – Syslog', 'descricao': 'System Log Protocol'},
        {'porta': 161, 'protocolo': 'UDP – SNMP', 'descricao': 'Simple Network Management Protocol'},
        {'porta': 5060, 'protocolo': 'UDP – SIP', 'descricao': 'Session Initiation Protocol'},
        {'porta': 1812, 'protocolo': 'UDP – RADIUS', 'descricao': 'Remote Authentication Dial-In User Service'},
        {'porta': 69, 'protocolo': 'UDP – TFTP', 'descricao': 'Trivial File Transfer Protocol'}
    ]
    
    result = []

    for portaInfo in portas:
        protocolo, descricao = portaInfo['protocolo'].split(' – ')
        
        statusTCP = "Desconhecido"
        statusUDP = "Desconhecido"

        try:
            statusTCP = verificarTCP(host, portaInfo['porta'])
        except Exception as e:
            print(f"Erro: {str(e)}, ao verificar TCP na porta {portaInfo['porta']}")
        
        try:
            statusUDP = verificarUDP(host, portaInfo['porta'])
        except Exception as e:
            print(f"Erro: {str(e)}, ao verificar UDP na porta {portaInfo['porta']}")

        result.append({
            portaInfo['porta']: {
                'porta': portaInfo['porta'],
                'protocolo': f"{protocolo} – {descricao}",
                'status': statusTCP if statusTCP != "Desconhecido" else statusUDP
            }
        })

    try:
        with open("testePorta.json", "w") as outputFile:
            json.dump(result, outputFile, indent=4)
    except Exception as e:
        print(f"Erro: {str(e)}, ao salvar o arquivo JSON")
        sys.exit(1)

    print("Verificacao concluida, arquivo 'testePorta.json' salvo.")