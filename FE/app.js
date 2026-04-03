// Financial News Intelligence System - Frontend Logic

const API_URL = 'http://localhost:8000/api';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('clearBtn');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const errorState = document.getElementById('errorState');
const resultsContainer = document.getElementById('resultsContainer');
const resultsList = document.getElementById('resultsList');
const resultsTitle = document.getElementById('resultsTitle');
const resultsCount = document.getElementById('resultsCount');
const errorMessage = document.getElementById('errorMessage');
const retryBtn = document.getElementById('retryBtn');
const showEntitiesBtn = document.getElementById('showEntitiesBtn');
const entitiesModal = document.getElementById('entitiesModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const entitiesContent = document.getElementById('entitiesContent');
const connectionStatus = document.getElementById('connectionStatus');

// State
let currentQuery = '';

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});
searchInput.addEventListener('input', (e) => {
    clearBtn.style.display = e.target.value ? 'block' : 'none';
});
clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    searchInput.focus();
});
retryBtn.addEventListener('click', handleSearch);
showEntitiesBtn.addEventListener('click', showEntities);
closeModalBtn.addEventListener('click', () => {
    entitiesModal.style.display = 'none';
});
entitiesModal.addEventListener('click', (e) => {
    if (e.target === entitiesModal) {
        entitiesModal.style.display = 'none';
    }
});

// Quick queries
document.querySelectorAll('.quick-query').forEach(btn => {
    btn.addEventListener('click', () => {
        searchInput.value = btn.dataset.query;
        handleSearch();
    });
});

// Functions
async function handleSearch() {
    const query = searchInput.value.trim();

    if (!query) {
        return;
    }

    currentQuery = query;
    showLoadingState();

    try {
        const response = await fetch(`${API_URL}/news/query?q=${encodeURIComponent(query)}&limit=20`);

        if (!response.ok) {
            throw new Error('Search failed');
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Search error:', error);
        showErrorState(error.message);
    }
}

function showLoadingState() {
    hideAllStates();
    loadingState.style.display = 'block';
}

function showErrorState(message) {
    hideAllStates();
    errorState.style.display = 'block';
    errorMessage.textContent = message || 'Unable to fetch results. Please check if the backend server is running.';
}

function hideAllStates() {
    loadingState.style.display = 'none';
    emptyState.style.display = 'none';
    errorState.style.display = 'none';
    resultsContainer.style.display = 'none';
}

function displayResults(data) {
    hideAllStates();

    if (!data.results || data.results.length === 0) {
        emptyState.style.display = 'block';
        emptyState.innerHTML = `
            <div class="empty-icon">🔍</div>
            <h3>No results found</h3>
            <p>Try a different search query or browse suggested topics.</p>
        `;
        return;
    }

    resultsContainer.style.display = 'block';
    resultsTitle.textContent = `Results for "${currentQuery}"`;
    resultsCount.textContent = `${data.total_results} article${data.total_results !== 1 ? 's' : ''}`;

    resultsList.innerHTML = data.results.map(article => createArticleCard(article)).join('');
}

function createArticleCard(article) {
    const entities = article.entities || [];
    const stocks = article.stocks || [];

    // Group entities by type
    const companies = entities.filter(e => e.type === 'company' || e.type === 'companie');
    const sectors = entities.filter(e => e.type === 'sector');
    const regulators = entities.filter(e => e.type === 'regulator');
    const people = entities.filter(e => e.type === 'people' || e.type === 'person');

    // Format timestamp
    const timestamp = new Date(article.timestamp).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });

    // Relevance score display
    const relevanceScore = article.relevance_score ? (article.relevance_score * 100).toFixed(0) : null;
    const relevanceReason = article.relevance_reason || '';

    return `
        <div class="article-card">
            <div class="article-header">
                <div class="article-meta">
                    <span>📰 ${article.source || 'Unknown'}</span>
                    <span>📅 ${timestamp}</span>
                </div>
                ${relevanceScore ? `<div class="relevance-badge">${relevanceScore}% Match</div>` : ''}
            </div>
            
            <h3 class="article-headline">${article.headline}</h3>
            <p class="article-content">${truncateText(article.content, 200)}</p>
            
            ${entities.length > 0 ? `
                <div class="article-tags">
                    ${companies.map(e => `<span class="tag tag-company">🏢 ${e.name}</span>`).join('')}
                    ${sectors.map(e => `<span class="tag tag-sector">📊 ${e.name}</span>`).join('')}
                    ${regulators.map(e => `<span class="tag tag-regulator">🏛️ ${e.name}</span>`).join('')}
                    ${people.map(e => `<span class="tag tag-people">👤 ${e.name}</span>`).join('')}
                </div>
            ` : ''}
            
            ${stocks.length > 0 ? `
                <div class="stocks-section">
                    <div class="stocks-title">Impacted Stocks:</div>
                    <div class="stocks-list">
                        ${stocks.slice(0, 5).map(stock => `
                            <div class="stock-badge">
                                <span class="stock-symbol">${stock.symbol}</span>
                                <span class="stock-confidence">${(stock.confidence * 100).toFixed(0)}%</span>
                            </div>
                        `).join('')}
                        ${stocks.length > 5 ? `
                            <span onclick="this.nextElementSibling.style.display = 'contents'; this.style.display = 'none';" style="cursor: pointer; color: var(--gold-primary); font-size: 0.875rem; display: flex; align-items: center; border: 1px solid var(--black-tertiary); padding: 0.5rem 1rem; border-radius: 8px; background: var(--black-tertiary);">+${stocks.length - 5} more</span>
                            <div style="display: none;">
                                ${stocks.slice(5).map(stock => `
                                    <div class="stock-badge">
                                        <span class="stock-symbol">${stock.symbol}</span>
                                        <span class="stock-confidence">${(stock.confidence * 100).toFixed(0)}%</span>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${relevanceReason ? `<p style="color: var(--text-muted); font-size: 0.875rem; margin-top: 1rem;">💡 ${relevanceReason}</p>` : ''}
        </div>
    `;
}

async function showEntities() {
    entitiesModal.style.display = 'flex';
    entitiesContent.innerHTML = '<div class="spinner"></div>';

    try {
        const response = await fetch(`${API_URL}/entities`);

        if (!response.ok) {
            throw new Error('Failed to fetch entities');
        }

        const data = await response.json();
        displayEntities(data);
    } catch (error) {
        console.error('Entities error:', error);
        entitiesContent.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <p style="color: var(--error-color);">Failed to load entities</p>
            </div>
        `;
    }
}

function displayEntities(entities) {
    const entityTypes = [
        { key: 'company', label: 'Companies', icon: '🏢' },
        { key: 'sector', label: 'Sectors', icon: '📊' },
        { key: 'regulator', label: 'Regulators', icon: '🏛️' },
        { key: 'people', label: 'People', icon: '👤' },
        { key: 'event', label: 'Events', icon: '📢' }
    ];

    let html = '';

    entityTypes.forEach(type => {
        const items = entities[type] || entities[type + 's'] || [];
        if (items.length > 0) {
            html += `
                <div class="entity-group">
                    <h3>${type.icon} ${type.label} (${items.length})</h3>
                    <div class="entity-items">
                        ${items.map(item => `
                            <div class="entity-item">${item.name || item}</div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    });

    if (!html) {
        html = `
            <div style="text-align: center; padding: 2rem;">
                <p style="color: var(--text-muted);">No entities extracted yet. Ingest some news articles first!</p>
            </div>
        `;
    }

    entitiesContent.innerHTML = html;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Check backend connection on load
async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            connectionStatus.textContent = 'Connected';
            connectionStatus.parentElement.style.background = 'rgba(16, 185, 129, 0.1)';
            connectionStatus.parentElement.style.borderColor = 'rgba(16, 185, 129, 0.2)';
            connectionStatus.style.color = '#10b981';
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        connectionStatus.textContent = 'Disconnected';
        connectionStatus.parentElement.style.background = 'rgba(239, 68, 68, 0.1)';
        connectionStatus.parentElement.style.borderColor = 'rgba(239, 68, 68, 0.2)';
        connectionStatus.style.color = '#ef4444';
    }
}

// Initialize
checkConnection();
setInterval(checkConnection, 30000); // Check every 30 seconds
