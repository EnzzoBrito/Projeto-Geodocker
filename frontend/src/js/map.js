/**
 * GeoDocker Challenge - Módulo de Mapa Interativo (Leaflet + OpenStreetMap)
 */

let map;
let markersLayer;
let temporaryMarker = null;

// Cores e ícones temáticos por categoria
const CATEGORIA_CORES = {
  "Buraco em via pública": { bg: "#ef4444", icon: "🕳️" },     // Vermelho
  "Alagamento": { bg: "#3b82f6", icon: "🌊" },                 // Azul
  "Descarte irregular de lixo": { bg: "#eab308", icon: "🗑️" }, // Amarelo
  "Iluminação pública": { bg: "#a855f7", icon: "💡" },         // Roxo
  "Acessibilidade": { bg: "#10b981", icon: "♿" },             // Verde
  "Outros": { bg: "#64748b", icon: "⚠️" }                      // Cinza
};

function initMap(initialLat = -1.4558, initialLng = -48.4902, zoom = 14) {
  // Inicializa mapa centrado nas coordenadas padrão (ex.: Belém)
  map = L.map("map", {
    zoomControl: false
  }).setView([initialLat, initialLng], zoom);

  // Adiciona controle de zoom no canto superior esquerdo
  L.control.zoom({ position: "topleft" }).addTo(map);

  // Camada de Tiles do OpenStreetMap
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // Grupo de marcadores
  markersLayer = L.layerGroup().addTo(map);

  // Evento de clique no mapa para selecionar coordenadas e cadastrar ocorrência
  map.on("click", function(e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;
    
    // Adiciona ou reposiciona marcador temporário
    setTemporaryMarker(lat, lng);

    // Abre o modal de cadastro pré-preenchendo latitude e longitude
    window.openNewOccurrenceModal(lat, lng);
  });
}

function setTemporaryMarker(lat, lng) {
  if (temporaryMarker) {
    map.removeLayer(temporaryMarker);
  }

  const tempIcon = L.divIcon({
    className: "temp-pin",
    html: `<div style="background-color: #10b981; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 0 15px rgba(16,185,129,0.8); color: white; font-size: 16px;">📍</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 36]
  });

  temporaryMarker = L.marker([lat, lng], { icon: tempIcon }).addTo(map);
}

function clearTemporaryMarker() {
  if (temporaryMarker) {
    map.removeLayer(temporaryMarker);
    temporaryMarker = null;
  }
}

function createMarkerIcon(categoria) {
  const config = CATEGORIA_CORES[categoria] || CATEGORIA_CORES["Outros"];
  return L.divIcon({
    className: "custom-marker-wrapper",
    html: `<div class="custom-pin" style="background-color: ${config.bg};">${config.icon}</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -34]
  });
}

function renderMarkersOnMap(ocorrencias) {
  markersLayer.clearLayers();

  if (!ocorrencias || ocorrencias.length === 0) return;

  const bounds = [];

  ocorrencias.forEach(item => {
    if (item.latitude && item.longitude) {
      bounds.push([item.latitude, item.longitude]);
      const icon = createMarkerIcon(item.categoria);
      const marker = L.marker([item.latitude, item.longitude], { icon: icon });

      // Monta conteúdo do Popup
      const popupHtml = `
        <div class="flex flex-col">
          <div class="relative w-full h-36 bg-slate-950 overflow-hidden">
            <img src="${item.imagem_url}" alt="${item.titulo}" class="w-full h-full object-cover">
            <span class="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider text-white bg-slate-900/80 backdrop-blur border border-slate-700">
              ${item.categoria}
            </span>
          </div>
          <div class="p-3.5 space-y-2">
            <div>
              <h4 class="text-xs font-bold text-white line-clamp-1">${item.titulo}</h4>
              <p class="text-[11px] text-slate-300 mt-1 line-clamp-2">${item.descricao}</p>
            </div>
            
            <div class="flex items-center gap-1.5 text-[10px]">
              <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">Status: ${item.status}</span>
              <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">Prioridade: ${item.prioridade}</span>
            </div>

            <div class="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
              <button onclick="window.editarOcorrencia(${item.id})" class="text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1">
                ✏️ Editar
              </button>
              <button onclick="window.excluirOcorrencia(${item.id})" class="text-rose-400 hover:text-rose-300 font-medium flex items-center gap-1">
                🗑️ Excluir
              </button>
            </div>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);
      markersLayer.addLayer(marker);
    }
  });

  // Ajusta visão para englobar os marcadores
  if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
  }
}

function zoomToLocation(lat, lng, zoomLevel = 16) {
  if (map) {
    map.flyTo([lat, lng], zoomLevel, {
      duration: 1.2
    });
  }
}
