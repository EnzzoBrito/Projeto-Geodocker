# 🌍 GeoDocker Challenge — Mapa Colaborativo de Ocorrências Urbanas

> **Atividade Prática de DevOps**  
> **Equipe:**  
> - 👨‍💻 **Hermes da Rocha Martins STupinambá**  
> - 👨‍💻 **Carlos Garcia**  
> - 👨‍💻 **Enzo Brito**  
> 
---

## 📌 1. Visão Geral do Projeto

O **GeoDocker Challenge** é uma plataforma web completa para mapeamento colaborativo e gestão de problemas urbanos em cidades (como buracos em vias públicas, alagamentos, descarte irregular de lixo, falhas de iluminação e barreiras de acessibilidade).

A aplicação foi projetada e conteinerizada seguindo as melhores práticas de **DevOps** e orquestração com **Docker Compose**, implementando isolamento de serviços em contêineres independentes e persistência desacoplada para o banco de dados e para as fotografias.

---

## 🏛️ 2. Arquitetura da Solução e Rede Docker

A solução é composta por **4 contêineres independentes**, interligados por uma rede interna do Docker (`geodocker-network`), com persistência garantida através de volumes dedicados.

```
                                  [ NAVEGADOR DO USUÁRIO ]
                                             |
                     +-----------------------+-----------------------+
                     | :8080                                         | :5000
                     v                                               v
        +-------------------------+                     +-------------------------+
        |   geodocker-frontend    |                     |   geodocker-backend     |
        |      (Nginx Alpine)     |                     |    (FastAPI / Python)   |
        |  HTML5 + Leaflet + CSS  |                     |  CRUD REST + Validações |
        +-------------------------+                     +-------------------------+
                     |                                               |
                     | proxy /api/                                   |
                     +-----------------------+-----------------------+
                                             |
                      [ REDE DOCKER EM BRIDGE: geodocker-network ]
                                             |
                     +-----------------------+-----------------------+
                     | (dns: database:5432)                          | (dns: storage:8888)
                     v                                               v
        +-------------------------+                     +-------------------------+
        |       geodocker-db      |                     |    geodocker-storage    |
        |  (PostgreSQL 16 Alpine) |                     |   (SeaweedFS c/ S3 API) |
        |  Coordenadas e Metadados|                     |  Fotografias Gravadas   |
        +-------------------------+                     +-------------------------+
                     |                                               |
                     v                                               v
             [ Volume Docker ]                               [ Volume Docker ]
           geodocker_postgres_data                         geodocker_storage_data
```

### 📋 Detalhamento dos Serviços e Portas

| Serviço | Contêiner | Imagem Base | Porta Host | Volume Docker | Descrição |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Frontend** | `geodocker-frontend` | `nginx:alpine` | **`8080:80`** | *(stateless)* | Interface SPA com mapa interativo Leaflet e formulários de CRUD. |
| **Backend** | `geodocker-backend` | `python:3.11-slim` | **`5000:5000`** | *(stateless)* | API REST com FastAPI, SQLAlchemy, Swagger docs e upload. |
| **Database** | `geodocker-db` | `postgres:16-alpine` | **`5432:5432`** | `geodocker_postgres_data` | Banco relacional persistindo ocorrências e coordenadas. |
| **Storage** | `geodocker-storage` | `chrislusf/seaweedfs` | **`8888:8888`** | `geodocker_storage_data` | Armazenamento de arquivos independente para fotos. |

---

## 🚀 3. Desafio DevOps A — Inicialização Automatizada

Todo o ambiente é provisionado automaticamente com um único comando, sem necessidade de instalar dependências locais na máquina hospedeira.

### Passo 1: Clonar o Repositório
```bash
git clone <URL_DO_REPOSITORIO_GITLAB>
cd geodocker-challenge
```

### Passo 2: Inicializar todos os Serviços
```bash
docker compose up -d --build
```

O Docker Compose cuidará da construção das imagens do backend e frontend, download do PostgreSQL e SeaweedFS, criação da rede bridge, montagem dos volumes e aplicação dos *healthchecks*.

### 🌐 Endereços de Acesso:
- **Aplicação Web (Frontend com Mapa):** [http://localhost:8080](http://localhost:8080)
- **Documentação Interativa da API (Swagger):** [http://localhost:5000/docs](http://localhost:5000/docs)
- **Diagnóstico de Saúde dos Serviços:** [http://localhost:5000/health](http://localhost:5000/health)
- **Serviço de Armazenamento SeaweedFS Filer:** [http://localhost:8888](http://localhost:8888)

---

## 🔄 4. Desafios DevOps B e C — Testes de Persistência

### Desafio B: Persistência dos Dados (PostgreSQL)
Demonstra que os registros das ocorrências e suas coordenadas geográficas sobrevivem à exclusão e recriação dos contêineres.

### Desafio C: Persistência das Imagens (SeaweedFS)
Demonstra que as fotografias anexadas continuam acessíveis nos mesmos caminhos e URLs após o ciclo de vida dos contêineres.

### Roteiro Prático de Comprovação da Persistência:

1. **Cadastrar pelo menos 5 ocorrências:**
   - Acesse [http://localhost:8080](http://localhost:8080) e cadastre as ocorrências clicando no mapa, ou simplesmente clique no botão superior **"Popular 5 Testes"** (que cadastra 5 problemas urbanos com imagens reais).
   - Alternativamente, via terminal:
     ```bash
     curl -X POST http://localhost:5000/api/seed
     ```

2. **Verificar os registros e imagens antes de derrubar:**
   ```bash
   curl -s http://localhost:5000/api/ocorrencias | grep -o '"id":' | wc -l
   ```
   *(Confirmará 5 ou mais ocorrências persistidas)*.

3. **Derrubar e remover completamente os contêineres (`down`):**
   ```bash
   docker compose down
   ```
   *(Todos os contêineres e a rede são destruídos. Os volumes `geodocker_postgres_data` e `geodocker_storage_data` são intencionalmente preservados pelo Docker)*.

4. **Recriar os serviços:**
   ```bash
   docker compose up -d
   ```

5. **Comprovar a permanência dos dados e imagens:**
   - Recarregue [http://localhost:8080](http://localhost:8080).
   - Todos os marcadores estarão nos mesmos pontos geográficos no mapa.
   - Ao clicar nos marcadores, as fotografias carregarão imediatamente a partir do volume do SeaweedFS.

> 💡 **Script Automatizado:** Você também pode rodar `pwsh scripts/test_persistence.ps1` ou `bash scripts/test_persistence.sh` para executar o teste de persistência em modo automatizado.

---

## 🔍 5. Desafio DevOps D — Diagnóstico e Comunicação

O Docker Compose isola os contêineres e provê um servidor DNS interno automático, permitindo que os serviços conversem entre si por **nomes de serviço**:

- O **Backend** conecta no banco usando a string:  
  `postgresql://postgres:postgres123@database:5432/geodocker_db`  
  *(onde `database` é resolvido automaticamente para o IP interno do contêiner PostgreSQL).*

- O **Backend** envia fotos para o storage via:  
  `http://storage:8888/ocorrencias/`  
  *(onde `storage` aponta para o SeaweedFS).*

### Comandos de Diagnóstico:

```bash
# 1. Verificar estado de saúde dos contêineres:
docker compose ps

# 2. Exibir logs em tempo real do backend:
docker compose logs -f backend

# 3. Exibir logs do banco de dados PostgreSQL:
docker compose logs database

# 4. Exibir logs do serviço de armazenamento SeaweedFS:
docker compose logs storage

# 5. Inspecionar a rede interna e verificar os IPs atribuídos a cada serviço:
docker network inspect geodocker_network
```

---

## 📡 6. Especificação da API REST (CRUD)

| Método | Rota | Descrição | Parâmetros |
| :--- | :--- | :--- | :--- |
| **`GET`** | `/api/ocorrencias` | Lista ocorrências com filtros opcionais | Query: `categoria`, `status`, `prioridade` |
| **`GET`** | `/api/ocorrencias/{id}` | Retorna detalhes de uma ocorrência | Path: `id` |
| **`POST`** | `/api/ocorrencias` | Cadastra nova ocorrência + foto | Form-data: `titulo`, `descricao`, `categoria`, `prioridade`, `status`, `latitude`, `longitude`, `foto` |
| **`PUT`** | `/api/ocorrencias/{id}` | Atualiza ocorrência e/ou nova foto | Form-data com campos a modificar |
| **`DELETE`** | `/api/ocorrencias/{id}` | Exclui registro e apaga foto do storage | Path: `id` |
| **`GET`** | `/api/images/{filename}` | Entrega a foto armazenada no SeaweedFS | Path: `filename` |
| **`GET`** | `/health` | Diagnóstico de integridade dos 4 serviços | *(Nenhum)* |
| **`POST`** | `/api/seed` | Popula 5 ocorrências de teste | *(Nenhum)* |

---

## 🛠️ 7. Explicação Técnica sobre a Persistência de Dados

No Docker, contêineres são efêmeros por padrão. Para garantir que dados sobrevivam a exclusões (`docker compose down`), utilizamos **Volumes Nomeados gerenciados pelo Docker Host**:

1. **Volume `geodocker_postgres_data`**:
   - Mapeado para `/var/lib/postgresql/data` no contêiner do PostgreSQL.
   - Contém as tabelas, índices e arquivos WAL do banco de dados relacional.
   
2. **Volume `geodocker_storage_data`**:
   - Mapeado para `/data` no contêiner do SeaweedFS.
   - Contém os metadados de volume, blocos binários e árvores de diretórios das fotografias enviadas.

Como esses volumes residem no host e são declarados sob a seção `volumes:` do `docker-compose.yml`, o comando `docker compose down` remove apenas os contêineres e a rede, mantendo os volumes intactos para a próxima inicialização.
