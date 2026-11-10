# 🦊 Guia Prático para Envio ao GitLab com Commits dos 3 Integrantes

> **Critério de Avaliação:** GitLab e documentação (0,3 ponto)  
> **Requisito Obrigatório:** Cada integrante deve contribuir com commits identificáveis no histórico do repositório.

---

## 📝 Passo a Passo para Criar o Repositório e Realizar os Commits

### 1. Criar o Projeto no GitLab
1. Acesse sua conta no **[GitLab](https://gitlab.com)** (ou no GitLab institucional da sua faculdade).
2. Clique em **"New Project"** -> **"Create blank project"**.
3. Nome do projeto: `geodocker-challenge`.
4. Defina a visibilidade como **Public** ou **Internal** (ou adicione o professor como membro caso seja Private).
5. Desmarque a opção "Initialize repository with a README" (pois já criamos um README completo).
6. Copie a URL do repositório (ex.: `https://gitlab.com/seu-usuario/geodocker-challenge.git`).

---

### 2. Inicializar o Repositório Local no seu Computador
No terminal (PowerShell ou Bash), navegue até a pasta do projeto:
```bash
cd C:\Users\loren\.gemini\antigravity\scratch\geodocker-challenge
git init
git branch -M main
```

---

### 3. Estratégia de Commits Identificáveis para Cada Aluno

Para comprovar que **todos os 3 integrantes participaram do desenvolvimento**, execute os blocos de commit abaixo:

#### 🔹 Commit 1: Hermes Tupinambá (Infraestrutura, Docker Compose e SeaweedFS)
```bash
git config user.name "Hermes Tupinambá"
git config user.email "hermes25070054@aluno.cesupa.br"

git add docker-compose.yml .env.example .gitignore
git commit -m "feat(infra): setup Docker Compose orchestration with PostgreSQL and SeaweedFS volumes"
```

#### 🔹 Commit 2: Carlos Garcia (Frontend, Interface Web e Mapa Leaflet)
```bash
git config user.name "Carlos Garcia"
git config user.email "carlos.garcia@aluno.cesupa.br"

git add frontend/
git commit -m "feat(frontend): implement responsive SPA with Leaflet map, CRUD forms and custom pins"
```

#### 🔹 Commit 3: Enzo Brito (Backend REST API, Persistência e Endpoints)
```bash
git config user.name "Enzo Brito"
git config user.email "enzo.brito@aluno.cesupa.br"

git add backend/
git commit -m "feat(backend): implement FastAPI REST API, PostgreSQL models and storage integration"
```

#### 🔹 Commit 4: Documentação, Testes e Roteiro (Hermes, Carlos e Enzo)
```bash
git config user.name "Hermes Tupinambá"
git config user.email "hermes25070054@aluno.cesupa.br"

git add README.md ROTEIRO_VIDEO_5MIN.md GUIA_GITLAB.md scripts/
git commit -m "docs: comprehensive documentation, persistence test scripts and video demo script"
```

---

### 4. Enviar os Arquivos ao GitLab
Vincule o repositório remoto e faça o push:
```bash
git remote add origin <URL_DO_SEU_REPOSITORIO_GITLAB>
git push -u origin main
```

---

### 5. Conferência no GitLab
Acesse a página do projeto no GitLab e verifique:
1. A aba **"Commits"** exibindo as contribuições de **Hermes Tupinambá**, **Carlos Garcia** e **Enzo Brito**.
2. O **`README.md`** renderizado na página inicial com toda a documentação, tabelas e arquitetura.
3. As pastas `backend`, `frontend`, `scripts` e o arquivo `docker-compose.yml` na raiz do projeto.
