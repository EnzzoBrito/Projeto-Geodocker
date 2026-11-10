/**
 * GeoDocker Challenge - Lógica da Aplicação Web e Consumo da API REST
 */

// A API REST roda na porta 5000 do host, ou relativa caso haja proxy Nginx
const API_BASE = window.location.port === "8080" 
  ? "http://localhost:5000" 
  : (window.location.origin.includes(":5000") ? window.location.origin : "http://localhost:5000");

let ocorrenciasCache = [];
let editandoId = null;

// Elementos da DOM
const sidebar = document.getElementById("sidebar");
const btnToggleSidebar = document.getElementById("btn-toggle-sidebar");
const btnCloseSidebar = document.getElementById("btn-close-sidebar");
const listaOcorrencias = document.getElementById("lista-ocorrencias");
const badgeTotal = document.getElementById("badge-total");
const btnNovaOcorrencia = document.getElementById("btn-nova-ocorrencia");
const btnAtualizar = document.getElementById("btn-atualizar");
const btnSeed = document.getElementById("btn-seed");
const btnStatus = document.getElementById("btn-status");

// Modal de Formulário
const modalForm = document.getElementById("modal-form");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnCancelar = document.getElementById("btn-cancelar");
const formOcorrencia = document.getElementById("form-ocorrencia");
const modalTitle = document.getElementById("modal-title");
const btnSalvarTexto = document.getElementById("btn-salvar-texto");
const formFoto = document.getElementById("form-foto");
const fotoPreview = document.getElementById("foto-preview");
const fotoPreviewContainer = document.getElementById("foto-preview-container");
const fotoPrompt = document.getElementById("foto-prompt");
const fotoNome = document.getElementById("foto-nome");
const labelFoto = document.getElementById("label-foto");

// Modal de Diagnóstico
const modalStatus = document.getElementById("modal-status");
const btnCloseStatus = document.getElementById("btn-close-status");
const btnCloseStatusOk = document.getElementById("btn-close-status-ok");

// Filtros
const filtroBusca = document.getElementById("filtro-busca");
const filtroCategoria = document.getElementById("filtro-categoria");
const filtroStatus = document.getElementById("filtro-status");

// =============================================================================
// INICIALIZAÇÃO
// =============================================================================
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  carregarOcorrencias();
  setupEventListeners();
});

function setupEventListeners() {
  // Toggle Sidebar
  btnToggleSidebar?.addEventListener("click", () => sidebar.classList.toggle("translate-x-full"));
  btnCloseSidebar?.addEventListener("click", () => sidebar.classList.add("translate-x-full"));

  // Botões de Abertura de Modais
  btnNovaOcorrencia.addEventListener("click", () => window.openNewOccurrenceModal(-1.4558, -48.4902));
  btnCloseModal.addEventListener("click", fecharModalForm);
  btnCancelar.addEventListener("click", fecharModalForm);

  // Botão de Atualização
  btnAtualizar.addEventListener("click", carregarOcorrencias);

  // Botão DevOps Seed (5 ocorrências)
  btnSeed?.addEventListener("click", executarSeedingDevOps);

  // Botão Diagnóstico de Serviços
  btnStatus.addEventListener("click", abrirModalDiagnostico);
  btnCloseStatus.addEventListener("click", () => modalStatus.classList.add("hidden"));
  btnCloseStatusOk.addEventListener("click", () => modalStatus.classList.add("hidden"));

  // Filtros
  filtroBusca.addEventListener("input", aplicarFiltros);
  filtroCategoria.addEventListener("change", aplicarFiltros);
  filtroStatus.addEventListener("change", aplicarFiltros);

  // Preview de Foto
  formFoto.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      fotoNome.textContent = file.name;
      const reader = new FileReader();
      reader.onload = (evt) => {
        fotoPreview.src = evt.target.result;
        fotoPreviewContainer.classList.remove("hidden");
        fotoPreviewContainer.classList.add("flex");
        fotoPrompt.classList.add("hidden");
      };
      reader.readAsDataURL(file);
    }
  });

  // Submit do Formulário (POST ou PUT)
  formOcorrencia.addEventListener("submit", submeterFormulario);
}

// =============================================================================
// CONSUMO DA API REST (CRUD)
// =============================================================================

async function carregarOcorrencias() {
  listaOcorrencias.innerHTML = `
    <div class="text-center py-10 text-slate-500 text-xs">
      <svg class="animate-spin h-5 w-5 mx-auto text-emerald-400 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      Conectando ao PostgreSQL...
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/api/ocorrencias`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    
    // Normaliza URLs de imagem para o backend correto
    ocorrenciasCache = data.map(item => ({
      ...item,
      imagem_url: item.imagem_url.startsWith("http") ? item.imagem_url : `${API_BASE}${item.imagem_url}`
    }));

    badgeTotal.textContent = ocorrenciasCache.length;
    renderMarkersOnMap(ocorrenciasCache);
    aplicarFiltros();
  } catch (err) {
    console.error("Erro ao listar ocorrências:", err);
    listaOcorrencias.innerHTML = `
      <div class="p-4 text-center text-rose-400 text-xs space-y-2 bg-rose-950/20 border border-rose-900/50 rounded-xl">
        <p class="font-semibold">Falha na conexão com a API REST</p>
        <p class="text-[10px] text-slate-400">Verifique se o backend na porta 5000 está em execução no Docker.</p>
        <button onclick="carregarOcorrencias()" class="px-3 py-1 bg-rose-800 text-white rounded text-[11px]">Tentar Novamente</button>
      </div>
    `;
  }
}

function aplicarFiltros() {
  const busca = filtroBusca.value.toLowerCase().trim();
  const cat = filtroCategoria.value;
  const stat = filtroStatus.value;

  const filtrados = ocorrenciasCache.filter(item => {
    const matchBusca = !busca || item.titulo.toLowerCase().includes(busca) || item.descricao.toLowerCase().includes(busca);
    const matchCat = !cat || item.categoria === cat;
    const matchStat = !stat || item.status === stat;
    return matchBusca && matchCat && matchStat;
  });

  renderListaSidebar(filtrados);
}

function renderListaSidebar(itens) {
  if (itens.length === 0) {
    listaOcorrencias.innerHTML = `
      <div class="text-center py-12 text-slate-500 text-xs">
        Nenhuma ocorrência encontrada para os filtros aplicados.
      </div>
    `;
    return;
  }

  listaOcorrencias.innerHTML = itens.map(item => `
    <div class="p-3 hover:bg-slate-800/60 rounded-xl transition cursor-pointer group space-y-2" onclick="window.focarOcorrencia(${item.latitude}, ${item.longitude})">
      <div class="flex items-start gap-3">
        <img src="${item.imagem_url}" alt="${item.titulo}" class="w-14 h-14 object-cover rounded-lg border border-slate-800 flex-shrink-0 group-hover:scale-105 transition">
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="text-[10px] font-semibold text-emerald-400 truncate">${item.categoria}</span>
            <span class="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">${item.status}</span>
          </div>
          <h4 class="text-xs font-bold text-white truncate mt-0.5">${item.titulo}</h4>
          <p class="text-[11px] text-slate-400 line-clamp-1 mt-0.5">${item.descricao}</p>
        </div>
      </div>
      <div class="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800/50">
        <span class="font-mono">${item.latitude.toFixed(4)}, ${item.longitude.toFixed(4)}</span>
        <div class="flex items-center gap-2">
          <button onclick="event.stopPropagation(); window.editarOcorrencia(${item.id})" class="text-indigo-400 hover:text-indigo-300 font-medium">Editar</button>
          <span>&bull;</span>
          <button onclick="event.stopPropagation(); window.excluirOcorrencia(${item.id})" class="text-rose-400 hover:text-rose-300 font-medium">Excluir</button>
        </div>
      </div>
    </div>
  `).join("");
}

// =============================================================================
// SUBMISSÃO DO FORMULÁRIO (POST E PUT)
// =============================================================================

async function submeterFormulario(e) {
  e.preventDefault();
  btnSalvarTexto.textContent = "Salvando...";
  document.getElementById("btn-salvar").disabled = true;

  const formData = new FormData();
  formData.append("titulo", document.getElementById("form-titulo").value);
  formData.append("descricao", document.getElementById("form-descricao").value);
  formData.append("categoria", document.getElementById("form-categoria").value);
  formData.append("prioridade", document.getElementById("form-prioridade").value);
  formData.append("status", document.getElementById("form-status").value);
  formData.append("latitude", document.getElementById("form-lat").value);
  formData.append("longitude", document.getElementById("form-lng").value);

  const fotoInput = document.getElementById("form-foto");
  if (fotoInput.files.length > 0) {
    formData.append("foto", fotoInput.files[0]);
  }

  try {
    let url = `${API_BASE}/api/ocorrencias`;
    let method = "POST";

    if (editandoId) {
      url = `${API_BASE}/api/ocorrencias/${editandoId}`;
      method = "PUT";
    }

    const res = await fetch(url, {
      method: method,
      body: formData
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Erro HTTP ${res.status}`);
    }

    fecharModalForm();
    await carregarOcorrencias();
    clearTemporaryMarker();
  } catch (err) {
    alert(`Erro ao salvar ocorrência: ${err.message}`);
  } finally {
    btnSalvarTexto.textContent = "Salvar Ocorrência";
    document.getElementById("btn-salvar").disabled = false;
  }
}

// =============================================================================
// EXCLUSÃO (DELETE)
// =============================================================================

window.excluirOcorrencia = async function(id) {
  if (!confirm(`Deseja realmente excluir a ocorrência ID #${id}? A imagem associada também será removida do SeaweedFS.`)) {
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/ocorrencias/${id}`, {
      method: "DELETE"
    });

    if (!res.ok && res.status !== 204) {
      throw new Error(`HTTP ${res.status}`);
    }

    await carregarOcorrencias();
  } catch (err) {
    alert(`Erro ao excluir ocorrência: ${err.message}`);
  }
};

// =============================================================================
// CONTROLE DE MODAL (NOVA E EDITAR)
// =============================================================================

window.openNewOccurrenceModal = function(lat, lng) {
  editandoId = null;
  formOcorrencia.reset();
  document.getElementById("form-id").value = "";
  document.getElementById("form-lat").value = lat.toFixed(6);
  document.getElementById("form-lng").value = lng.toFixed(6);

  modalTitle.textContent = "Registrar Nova Ocorrência";
  btnSalvarTexto.textContent = "Cadastrar Ocorrência";
  labelFoto.textContent = "Fotografia da Ocorrência *";
  formFoto.required = true;

  fotoPreviewContainer.classList.add("hidden");
  fotoPrompt.classList.remove("hidden");

  modalForm.classList.remove("hidden");
  modalForm.classList.add("flex");
};

window.editarOcorrencia = function(id) {
  const item = ocorrenciasCache.find(o => o.id === id);
  if (!item) return;

  editandoId = id;
  document.getElementById("form-id").value = item.id;
  document.getElementById("form-titulo").value = item.titulo;
  document.getElementById("form-descricao").value = item.descricao;
  document.getElementById("form-categoria").value = item.categoria;
  document.getElementById("form-prioridade").value = item.prioridade;
  document.getElementById("form-status").value = item.status;
  document.getElementById("form-lat").value = item.latitude;
  document.getElementById("form-lng").value = item.longitude;

  modalTitle.textContent = `Editar Ocorrência #${item.id}`;
  btnSalvarTexto.textContent = "Salvar Alterações";
  labelFoto.textContent = "Trocar Fotografia (Opcional)";
  formFoto.required = false;

  fotoPreview.src = item.imagem_url;
  fotoNome.textContent = item.imagem_nome;
  fotoPreviewContainer.classList.remove("hidden");
  fotoPreviewContainer.classList.add("flex");
  fotoPrompt.classList.add("hidden");

  modalForm.classList.remove("hidden");
  modalForm.classList.add("flex");
};

function fecharModalForm() {
  modalForm.classList.add("hidden");
  modalForm.classList.remove("flex");
  clearTemporaryMarker();
}

window.focarOcorrencia = function(lat, lng) {
  zoomToLocation(lat, lng);
  if (window.innerWidth < 768) {
    sidebar.classList.add("translate-x-full");
  }
};

// =============================================================================
// SEEDING DEVOPS E DIAGNÓSTICO
// =============================================================================

async function executarSeedingDevOps() {
  if (!confirm("Inserir as 5 ocorrências de teste com fotos persistidas no SeaweedFS?")) return;

  try {
    const res = await fetch(`${API_BASE}/api/seed`, { method: "POST" });
    const data = await res.json();
    alert(data.mensagem || "Ocorrências inseridas com sucesso!");
    await carregarOcorrencias();
  } catch (err) {
    alert(`Erro ao executar seeding: ${err.message}`);
  }
}

async function abrirModalDiagnostico() {
  modalStatus.classList.remove("hidden");
  modalStatus.classList.add("flex");

  const statusBackend = document.getElementById("status-backend");
  const statusPostgres = document.getElementById("status-postgres");
  const statusStorage = document.getElementById("status-storage");

  statusBackend.textContent = "Testando...";
  statusPostgres.textContent = "Testando...";
  statusStorage.textContent = "Testando...";

  try {
    const res = await fetch(`${API_BASE}/health`);
    const health = await res.json();

    statusBackend.textContent = "ONLINE (FastAPI)";
    statusBackend.className = "px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 font-mono text-[11px] border border-emerald-500/20";

    statusPostgres.textContent = health.database_postgres.toUpperCase();
    statusPostgres.className = health.database_postgres === "healthy" 
      ? "px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 font-mono text-[11px] border border-emerald-500/20"
      : "px-2 py-1 rounded bg-rose-500/10 text-rose-400 font-mono text-[11px] border border-rose-500/20";

    statusStorage.textContent = health.storage_seaweedfs.toUpperCase();
    statusStorage.className = health.storage_seaweedfs === "healthy"
      ? "px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 font-mono text-[11px] border border-emerald-500/20"
      : "px-2 py-1 rounded bg-rose-500/10 text-rose-400 font-mono text-[11px] border border-rose-500/20";

  } catch (err) {
    statusBackend.textContent = "FALHA";
    statusBackend.className = "px-2 py-1 rounded bg-rose-500/10 text-rose-400 font-mono text-[11px]";
    statusPostgres.textContent = "INACESSÍVEL";
    statusStorage.textContent = "INACESSÍVEL";
  }
}
