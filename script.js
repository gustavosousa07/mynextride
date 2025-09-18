// ==============================================================================
// SCRIPT PRINCIPAL DO FRONTEND - MYNEXTRIDE
// ==============================================================================

// --- CONSTANTES E FUNÇÕES GERAIS ---
const API_URL = 'http://127.0.0.1:5001';

async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`);
        if (!response.ok) {
            console.error(`Erro do servidor para ${endpoint}:`, response.status, response.statusText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Falha ao buscar dados do endpoint ${endpoint}:`, error);
    }
}

// ==============================================================================
// FUNÇÕES DE CARREGAMENTO DE DADOS E GRÁFICOS
// ==============================================================================

// --- Funções para a aba "Visão Geral" ---

async function loadKPIs() {
    const data = await fetchData('/api/kpis');
    if (data) {
        // Formata a receita como moeda brasileira (R$, ponto de milhar, vírgula de decimal)
        document.getElementById('kpi-receita').textContent = data.receita_total.toLocaleString('pt-BR', { 
            style: 'currency', 
            currency: 'BRL' 
        });
        
        // Formata os números inteiros com o ponto de milhar
        document.getElementById('kpi-passagens').textContent = data.passagens_total.toLocaleString('pt-BR');
        document.getElementById('kpi-clientes').textContent = data.clientes_unicos.toLocaleString('pt-BR');
    }
}

async function loadTopRoutesChart() {
    const data = await fetchData('/api/top-routes');
    if (data && data.length > 0) {
        const ctx = document.getElementById('topRoutesChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.rota),
                datasets: [{
                    label: 'Quantidade de Viagens',
                    data: data.map(item => item.quantidade),
                    backgroundColor: 'rgba(74, 20, 140, 0.7)',
                    borderColor: 'rgba(74, 20, 140, 1)'
                }]
            },
            options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }
}

async function loadSeasonalityChart() {
    const data = await fetchData('/api/seasonality');
    if (data && data.length > 0) {
        const ctx = document.getElementById('seasonalityChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.mes),
                datasets: [{
                    label: 'Receita (R$)',
                    data: data.map(item => item.receita),
                    fill: true,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.2
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}

async function loadSegmentDistributionChart() {
    const data = await fetchData('/api/segment_distribution');
    if (data && data.length > 0) {
        const ctx = document.getElementById('segmentDistributionChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.segmento),
                datasets: [{
                    label: 'Nº de Clientes',
                    data: data.map(item => item.contagem),
                    backgroundColor: ['rgba(74, 20, 140, 0.8)', 'rgba(255, 99, 132, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 206, 86, 0.8)'],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                plugins: { 
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                const currentValue = tooltipItem.raw;
                                const total = tooltipItem.chart.getDatasetMeta(0).total;
                                const percentage = ((currentValue / total) * 100).toFixed(1);
                                return `${tooltipItem.label}: ${percentage}%`;
                            }
                        }
                    }
                } 
            }
        });
    }
}

async function loadNewCustomersChart() {
    const data = await fetchData('/api/new_customers_over_time');
    if (data && data.length > 0) {
        const ctx = document.getElementById('newCustomersChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.mes_aquisicao),
                datasets: [{
                    label: 'Novos Clientes',
                    data: data.map(item => item.quantidade),
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }
}

// --- Funções para a aba "Análise de Hubs" ---

async function loadHubs() {
    const data = await fetchData('/api/hubs');
    if (data && data.length > 0) {
        const listContainer = document.getElementById('hubs-list');
        listContainer.innerHTML = '';
        
        data.forEach((hub, index) => {
            const percentage = 100 - (index * 7);
            const hubElement = document.createElement('div');
            hubElement.classList.add('hub-item');
            hubElement.innerHTML = `
                <div class="hub-rank">${index + 1}.</div>
                <div class="hub-info">
                    <div class="hub-name">${hub.cidade}</div>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
            listContainer.appendChild(hubElement);
        });
    }
}

async function loadHubDetailsChart() {
    const data = await fetchData('/api/hub_details');
    if (data && data.length > 0) {
        const ctx = document.getElementById('hubDetailsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(hub => hub.cidade),
                datasets: [
                    {
                        label: 'Chegadas',
                        data: data.map(hub => hub.chegadas),
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Partidas',
                        data: data.map(hub => hub.partidas),
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, title: { display: true, text: 'Volume de Viagens' } } },
                plugins: { legend: { position: 'top' }, tooltip: { mode: 'index', intersect: false } }
            }
        });
    }
}

// --- Funções para a aba "Segmentação de Clientes" ---

async function loadClustersChart() {
    const data = await fetchData('/api/clusters');
    if (data && data.length > 0) {
        const gridContainer = document.getElementById('clusters-grid');
        gridContainer.innerHTML = '';

        const metrics = ['total_gasto', 'total_viagens', 'destinos_unicos'];
        const maxValues = {};
        metrics.forEach(metric => {
            maxValues[metric] = Math.max(...data.map(d => d[metric]));
        });

        data.forEach((cluster, index) => {
            const cardElement = document.createElement('div');
            cardElement.classList.add('col-lg-6', 'mb-4');
            cardElement.innerHTML = `<div class="card chart-card"><div class="card-body"><h5 class="mb-3">Perfil do ${cluster.nome_segmento}</h5><canvas id="clustersChart${cluster.cluster}"></canvas></div></div>`;
            gridContainer.appendChild(cardElement);

            const ctx = document.getElementById(`clustersChart${cluster.cluster}`).getContext('2d');
            const colors = ['rgba(255, 99, 132, 0.5)', 'rgba(54, 162, 235, 0.5)', 'rgba(255, 206, 86, 0.5)', 'rgba(75, 192, 192, 0.5)'];
            const borderColors = ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 206, 86)', 'rgb(75, 192, 192)'];
            
            const dataset = {
                label: cluster.nome_segmento,
                data: metrics.map(metric => maxValues[metric] > 0 ? (cluster[metric] / maxValues[metric]) * 100 : 0),
                backgroundColor: colors[index % colors.length],
                borderColor: borderColors[index % borderColors.length],
                borderWidth: 2,
                pointBackgroundColor: borderColors[index % borderColors.length]
            };

            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Gasto Total', 'Frequência', 'Variedade Destinos'],
                    datasets: [dataset]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { r: { angleLines: { display: false }, suggestedMin: 0, suggestedMax: 100, pointLabels: { font: { size: 12 } } } },
                    plugins: { legend: { display: false } }
                }
            });
        });
    }
}

// ==============================================================================
// INTERATIVIDADE DO MENU E INICIALIZAÇÃO
// ==============================================================================

function setupNavigation() {
    const navLinks = document.querySelectorAll('[data-target]');
    const contentSections = document.querySelectorAll('.content-section');

    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const targetId = this.getAttribute('data-target');
            
            contentSections.forEach(s => s.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');

            navLinks.forEach(l => {
                l.classList.remove('active');
                if (l.getAttribute('data-target') === targetId) {
                    l.classList.add('active');
                }
            });
        });
    });
}

// --- Função para a aba "Fale Conosco" ---

function setupContactForm() {
    const form = document.getElementById('contact-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Impede o recarregamento da página

            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;

            submitButton.textContent = 'Enviando...';
            submitButton.disabled = true;

            fetch("https://formspree.io/f/xovngqla", {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            }).then(response => {
                if (response.ok) {
                    alert('Obrigado pela sua mensagem! Responderemos em breve.');
                    form.reset(); // Limpa o formulário
                } else {
                    response.json().then(data => {
                        if (Object.hasOwn(data, 'errors')) {
                            alert(data["errors"].map(error => error["message"]).join(", "));
                        } else {
                            alert('Oops! Ocorreu um problema ao enviar seu formulário.');
                        }
                    })
                }
            }).catch(error => {
                alert('Oops! Ocorreu um problema ao enviar seu formulário.');
            }).finally(() => {
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Chama TODAS as funções para carregar os dados
    loadKPIs();
    loadTopRoutesChart();
    loadSeasonalityChart();
    loadSegmentDistributionChart();
    loadNewCustomersChart();
    loadHubs();
    loadHubDetailsChart();
    loadClustersChart();
    setupContactForm();
    
    // Configura a interatividade dos menus
    setupNavigation();
});