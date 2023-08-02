# Threat Copilot
Possui o objetivo facilitar a adoção da modelagem de ameaças por times ágeis de desenvolvimento em organizações. Para isso, a ferramenta armazena e in tegra os modelos de ameaças com os repositórios de produtos, de ativos e com as bases dedados de conhecimento sobre fraquezas (CWE), ataques (CAPEC) e ameaças (Mobile Threat Catalog).

# Instalação

Para executar a aplicação no seu ambiente siga os passos:

1. Inicie o Neo4J via docker (Pasta /docker) (Comando: docker compose up)
2. Crie um ambiente usando o módulo venv do python (python3 -m venv venv)
3. Habilite o ambiente (Comando: source /venv/bin/activate)
4. Instale as dependencias via PIP (Comando: pip install -r requirements.txt)
5. Inicie a aplicação (Comando: gunicorn --config ./gunicorn-cfg.py --reload run:app)

Para preparar para o uso é necessário realizar uma carga inicial ETL via Cypher:

1. Abra o console de admin do NEO4J (http://localhost:7474)
2. Execute os scripts cypher da pasta (/etl_scripts)
3. Entre na aplicação (http://localhost:5005/) Threat Copilot
4. Realize a carga do vocabulário (/kbdata/vocabulary.yml)

# Dúvidas e Sugestões
negocio.yuri@academico.ifpb.edu.br
