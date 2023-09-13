import argparse
from neo4j import GraphDatabase
import os

def executar_cypher_instrucao(cypher_instrucao, session):
    print(cypher_instrucao)
    session.run(cypher_instrucao)

def executar_arquivo_cypher(caminho_arquivo, session):
    with open(caminho_arquivo, "r") as arquivo:
        cypher_queries = arquivo.read().split(";")
        for cypher_query in cypher_queries:
            cypher_query = cypher_query.strip()
            if cypher_query:
                executar_cypher_instrucao(cypher_query, session)

def main():
    parser = argparse.ArgumentParser(description="Processa arquivos Cypher e executa-os no Neo4j")
    parser.add_argument("diretorio_cypher", help="Diretório contendo os arquivos Cypher")
    parser.add_argument("--host", default="localhost", help="Endereço do servidor Neo4j (padrão: localhost)")
    parser.add_argument("--port", default=7687, type=int, help="Porta do servidor Neo4j (padrão: 7687)")
    parser.add_argument("--user", default="neo4j", help="Nome de usuário do Neo4j (padrão: neo4j)")
    parser.add_argument("--password", default="your_password", help="Senha do usuário do Neo4j (padrão: your_password)")

    args = parser.parse_args()

    # Configuração da conexão com o Neo4j
    uri = f"bolt://{args.host}:{args.port}"
    driver = GraphDatabase.driver(uri, auth=(args.user, args.password))

    # Itera sobre todos os arquivos no diretório e executa os comandos Cypher
    with driver.session() as session:
        for arquivo in os.listdir(args.diretorio_cypher):
            if arquivo.endswith(".cypher"):
                caminho_arquivo = os.path.join(args.diretorio_cypher, arquivo)
                print(f"Executando arquivo Cypher: {caminho_arquivo}")
                executar_arquivo_cypher(caminho_arquivo, session)

    print("Processamento concluído.")

if __name__ == "__main__":
    main()