import os
from funcoes import (
    extrair_exif,
    obter_informacoes_basicas,
    obter_latitude_longitude,
    geocodificar
)
from collections import Counter
import json

def processar_imagens(diretorio):
    if not os.path.isdir(diretorio):
        print("Caminho invalido.")
        return

    resumo_cidades = Counter()
    resultados = []

    for arquivo in os.listdir(diretorio):
        caminho_arquivo = os.path.join(diretorio, arquivo)

        if not os.path.isfile(caminho_arquivo):
            continue

        print(f"Processando: {arquivo}")
        dados_exif = extrair_exif(caminho_arquivo)

        if dados_exif is None:
            print(f"Arquivo ignorado (nao possui EXIF valido): {arquivo}")
            continue

        informacoes_basicas = obter_informacoes_basicas(dados_exif)
        coordenadas = obter_latitude_longitude(dados_exif)
        cidade = "Sem localizacao"

        if coordenadas:
            lat, lon = coordenadas
            cidade = geocodificar(lat, lon)

        resultado = {
            "arquivo": arquivo,
            "largura": informacoes_basicas.get('largura', 'Desconhecida'),
            "altura": informacoes_basicas.get('altura', 'Desconhecida'),
            "fabricante": informacoes_basicas.get('fabricante', 'Desconhecido'),
            "modelo": informacoes_basicas.get('modelo', 'Desconhecido'),
            "data_hora": informacoes_basicas.get('data_hora', 'Desconhecida'),
            "latitude_longitude": coordenadas if coordenadas else 'Desconhecida',
            "cidade": cidade
        }

        resultados.append(resultado)

        if cidade != "Sem localizacao":
            resumo_cidades[cidade] += 1

    salvar_resultados_json(resultados)
    exibir_resumo_cidades(resumo_cidades)

def salvar_resultados_json(resultados):
    with open("resultados.json", "w", encoding="utf-8") as arquivo_json:
        json.dump(resultados, arquivo_json, ensure_ascii=False, indent=4)
    print("Resultados salvos em resultados.json")

def exibir_resumo_cidades(resumo_cidades):
    print("\nResumo das cidades:")
    for cidade, quantidade in resumo_cidades.items():
        print(f"{cidade}: {quantidade} fotos")

diretorio_imagens = input("Digite o caminho do diretorio com as imagens: ")
processar_imagens(diretorio_imagens)