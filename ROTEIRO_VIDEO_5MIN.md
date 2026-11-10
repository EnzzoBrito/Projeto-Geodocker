# 🎬 Roteiro de Gravação do Vídeo de Demonstração (Até 5 Minutos)

> **Critério de Avaliação:** Demonstração (0,5 ponto)  
> **Requisito Obrigatório:** Câmera aberta para cada integrante que for falar, identificando-se pelo nome.  
> **Equipe:** Hermes Tupinambá, Carlos Garcia e Enzo Brito.

---

## ⏱️ Cronograma Geral do Vídeo (5:00 max)

| Bloco | Integrante | Minutagem | Tema Principal |
| :--- | :--- | :--- | :--- |
| **Parte 1** | **Hermes Tupinambá** | 0:00 – 1:35 | Abertura, Arquitetura Docker Compose, Volumes e Inicialização Automatizada (`up -d`) |
| **Parte 2** | **Carlos Garcia** | 1:35 – 3:15 | Aplicação Web, Mapa Leaflet, Upload de Fotos e CRUD Completo (Criar, Listar, Editar, Excluir) |
| **Parte 3** | **Enzo Brito** | 3:15 – 5:00 | Desafios DevOps: Persistência de Dados e Fotos (`down` & `up -d`), Diagnóstico e Logs (`ps` / `logs`) |

---

## 🗣️ Script Detalhado Passo a Passo

### 🟢 PARTE 1 — Hermes Tupinambá (0:00 até 1:35)
*Câmera aberta. Compartilhar tela no VS Code mostrando o arquivo `docker-compose.yml` e o terminal.*

1. **Apresentação Inicial (15s):**
   > *"Olá professor! Meu nome é Hermes Tupinambá e, junto com meus colegas Carlos Garcia e Enzo Brito, estamos apresentando o projeto **GeoDocker Challenge**, nossa atividade prática de DevOps de mapeamento colaborativo de ocorrências urbanas."*

2. **Apresentação da Arquitetura e Decisões Técnicas (45s):**
   *(Mostra o `docker-compose.yml`)*
   > *"Nossa arquitetura foi desenhada com 4 serviços independentes e desacoplados:*  
   > *1. **Frontend**: Aplicação web com Nginx na porta 8080, utilizando Leaflet e Tailwind CSS.*  
   > *2. **Backend**: API REST em Python com FastAPI na porta 5000, com documentação Swagger interativa.*  
   > *3. **Database**: PostgreSQL 16 Alpine com volume nomeado `postgres_data` montado em `/var/lib/postgresql/data`.*  
   > *4. **Storage**: SeaweedFS com API compatível com S3, executando em contêiner separado com volume nomeado `storage_data` montado em `/data`.*  
   > *Todos os serviços comunicam-se de forma isolada pela rede em modo bridge `geodocker-network`."*

3. **Desafio DevOps A — Inicialização Automatizada (35s):**
   *(No terminal, executa o comando)*:
   ```bash
   docker compose up -d --build
   ```
   > *"Para cumprir o Desafio A, toda a infraestrutura inicializa de forma automatizada com apenas um comando `docker compose up -d --build`, sem nenhuma instalação manual no host.*  
   > *(Executa `docker compose ps`)*  
   > *Como podemos ver, os 4 contêineres estão saudáveis e operacionais. Agora passo a palavra para o Carlos Garcia demonstrar o sistema no navegador."*

---

### 🔵 PARTE 2 — Carlos Garcia (1:35 até 3:15)
*Câmera aberta. Compartilhar tela no navegador em `http://localhost:8080`.*

1. **Apresentação Pessoal e Interface (20s):**
   > *"Olá professor, meu nome é Carlos Garcia. Estou na interface da nossa aplicação web, acessível em `http://localhost:8080`. Podemos ver o mapa interativo centrado na malha urbana e a lista lateral de ocorrências."*

2. **Demonstração do Cadastro com Mapa e Upload (45s):**
   *(Clica em um ponto qualquer da rua no mapa)*
   > *"Para registrar uma ocorrência, basta o cidadão clicar diretamente no mapa. O sistema captura a latitude e longitude exatas e abre o formulário.*  
   > *Vou cadastrar: 'Buraco profundo na faixa da direita', categoria 'Buraco em via pública', prioridade 'Alta'. Seleciono uma fotografia do meu computador e clico em 'Cadastrar'.*  
   > *Imediatamente a foto é transmitida para o contêiner SeaweedFS e os dados para o PostgreSQL. O marcador aparece no mapa com o ícone temático."*

3. **Demonstração do Popup, Edição e Exclusão (35s):**
   *(Clica no marcador criado)*
   > *"Ao clicar no marcador, o popup exibe a fotografia recuperada do storage, detalhes e botões de ação.*  
   > *Vou clicar em 'Editar' e mudar o status para 'Em Andamento'. Vemos a atualização imediata no card.*  
   > *Também temos o botão 'Excluir', que remove o registro do banco e deleta a foto correspondente do SeaweedFS.*  
   > *Agora passo para o Enzo Brito demonstrar os desafios de persistência e diagnóstico."*

---

### 🟣 PARTE 3 — Enzo Brito (3:15 até 5:00)
*Câmera aberta. Tela dividida entre o navegador e o terminal.*

1. **Apresentação Pessoal e Estado Inicial (20s):**
   > *"Olá professor, meu nome é Enzo Brito. Vou demonstrar agora os Desafios DevOps B, C e D.*  
   > *Como podemos ver no navegador, temos mais de cinco ocorrências cadastradas com coordenadas e fotos visíveis."*

2. **Desafios DevOps B e C — Comprovação da Persistência (50s):**
   *(No terminal, digita)*:
   ```bash
   docker compose down
   ```
   > *"Agora vou executar `docker compose down`. Observem que todos os contêineres foram finalizados e completamente removidos do Docker.*  
   > *Se tentarmos recarregar a página agora, nada responde, comprovando que os contêineres caíram.*  
   > *Agora recrio os serviços:*
   ```bash
   docker compose up -d
   ```
   *(Aguarda 5 segundos e dá F5 no navegador)*  
   > *"Ao recarregar o navegador: todas as ocorrências e coordenadas continuam aqui intactas no mapa (Desafio B), e todas as fotografias continuam abrindo perfeitamente a partir do volume do SeaweedFS (Desafio C)."*

3. **Desafio DevOps D — Diagnóstico e Comunicação entre Serviços (35s):**
   *(No terminal, executa)*:
   ```bash
   docker compose ps
   docker compose logs backend
   ```
   > *"Para o Desafio D, utilizamos `docker compose ps` para inspecionar os serviços e `docker compose logs` para auditar a comunicação.*  
   > *Os contêineres conversam internamente utilizando os nomes de serviço `database:5432` e `storage:8888`, resolvidos pelo DNS interno da rede `geodocker-network`.*  
   > *Com isso, cobrimos com êxito todos os requisitos solicitados na atividade. Muito obrigado!"*

---

## 💡 Dicas de Ouro para a Gravação
1. **Gravação:** Podem gravar via Google Meet, Teams ou OBS Studio (onde os 3 entram na chamada com câmeras ligadas).
2. **Tempo:** Mantenham o cronômetro visível para garantir que não ultrapasse 5 minutos!
3. **Botão de Teste Rápido:** No topo da aplicação web há o botão **"Popular 5 Testes"**, que insere em 1 clique as 5 ocorrências já com imagens para o teste de persistência se quiserem agilizar a gravação!
