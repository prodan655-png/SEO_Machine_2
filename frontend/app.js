// ===== Configuration =====
const API_BASE_URL = 'http://localhost:8000';
const POLLING_INTERVAL = 2000; // 2 seconds
const SCORE_DEBOUNCE = 500; // 0.5 seconds

// ===== State Management ===== 
const state = {
    currentAnalysisId: null,
    analysisData: null,
    pollingInterval: null,
    scoreTimeout: null
};

// ===== DOM Elements =====
const elements = {
    // API Status
    apiStatus: document.getElementById('apiStatus'),
    apiStatusText: document.getElementById('apiStatusText'),

    // Tabs
    tabs: document.querySelectorAll('.tab-btn'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    resultsTab: document.getElementById('resultsTab'),
    scoringTab: document.getElementById('scoringTab'),

    // Form
    analysisForm: document.getElementById('analysisForm'),
    submitBtn: document.getElementById('submitBtn'),
    btnText: document.querySelector('.btn-text'),
    btnLoader: document.querySelector('.btn-loader'),

    // Status
    statusBadge: document.getElementById('statusBadge'),
    progressFill: document.getElementById('progressFill'),
    statusMessage: document.getElementById('statusMessage'),

    // Results
    resultsContent: document.getElementById('resultsContent'),
    competitorsBody: document.getElementById('competitorsBody'),
    termsBody: document.getElementById('termsBody'),
    guidelinesGrid: document.getElementById('guidelinesGrid'),

    // Scoring
    contentEditor: document.getElementById('contentEditor'),
    wordCount: document.getElementById('wordCount'),
    charCount: document.getElementById('charCount'),
    scoreNumber: document.getElementById('scoreNumber'),
    scoreCircle: document.getElementById('scoreCircle'),
    termsBar: document.getElementById('termsBar'),
    structureBar: document.getElementById('structureBar'),
    headingsBar: document.getElementById('headingsBar'),
    termsScore: document.getElementById('termsScore'),
    structureScore: document.getElementById('structureScore'),
    headingsScore: document.getElementById('headingsScore'),
    termDetailsCard: document.getElementById('termDetailsCard'),
    termsGrid: document.getElementById('termsGrid'),
    recommendations: document.getElementById('recommendations'),
    recommendationsList: document.getElementById('recommendationsList'),

    // Toast
    toastContainer: document.getElementById('toastContainer')
};

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    checkAPIStatus();
    initEventListeners();
});

function initEventListeners() {
    // Tab navigation
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Form submission
    elements.analysisForm.addEventListener('submit', handleFormSubmit);

    // Content editor
    elements.contentEditor.addEventListener('input', handleEditorInput);
}

// ===== API Functions =====
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            elements.apiStatus.classList.add('connected');
            elements.apiStatusText.textContent = 'API підключено';
        } else {
            throw new Error('API недоступний');
        }
    } catch (error) {
        elements.apiStatusText.textContent = 'API не підключено';
        showToast('Помилка підключення до API. Переконайтеся що сервер запущений.', 'error');
    }
}

async function createAnalysis(formData) {
    const response = await fetch(`${API_BASE_URL}/api/analysis/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    });

    if (!response.ok) {
        throw new Error('Помилка створення аналізу');
    }

    return await response.json();
}

async function getAnalysis(analysisId) {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}`);

    if (!response.ok) {
        throw new Error('Помилка отримання даних');
    }

    return await response.json();
}

async function scoreContent(analysisId, text, format) {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}/score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, format })
    });

    if (!response.ok) {
        throw new Error('Помилка оцінки контенту');
    }

    return await response.json();
}

async function toggleCompetitor(analysisId, url, enabled) {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}/competitors`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ competitor_url: url, enabled })
    });

    if (!response.ok) {
        throw new Error('Помилка оновлення конкурента');
    }

    return await response.json();
}

// ===== Form Handling =====
async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = {
        keyword: document.getElementById('keyword').value.trim(),
        language: document.getElementById('language').value,
        location: document.getElementById('location').value.trim(),
        device: document.querySelector('input[name="device"]:checked').value
    };

    // Show loading
    elements.btnText.classList.add('hidden');
    elements.btnLoader.classList.add('active');
    elements.submitBtn.disabled = true;

    try {
        const result = await createAnalysis(formData);
        state.currentAnalysisId = result.analysis_id;

        showToast('Аналіз розпочато! Очікуйте завершення...', 'success');

        // Switch to results tab
        elements.resultsTab.disabled = false;
        switchTab('results');

        // Start polling
        startPolling();

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        elements.btnText.classList.remove('hidden');
        elements.btnLoader.classList.remove('active');
        elements.submitBtn.disabled = false;
    }
}

// ===== Polling =====
function startPolling() {
    // Initial load
    pollAnalysisStatus();

    // Poll every 2 seconds
    state.pollingInterval = setInterval(pollAnalysisStatus, POLLING_INTERVAL);
}

function stopPolling() {
    if (state.pollingInterval) {
        clearInterval(state.pollingInterval);
        state.pollingInterval = null;
    }
}

async function pollAnalysisStatus() {
    try {
        const data = await getAnalysis(state.currentAnalysisId);
        state.analysisData = data;

        updateStatusDisplay(data);

        if (data.status === 'COMPLETED') {
            stopPolling();
            displayResults(data);
            elements.scoringTab.disabled = false;
            showToast('Аналіз завершено!', 'success');
        } else if (data.status === 'FAILED') {
            stopPolling();
            elements.statusBadge.textContent = 'Помилка';
            elements.statusBadge.style.background = 'var(--error)';
            elements.statusMessage.textContent = data.error_message || 'Виникла помилка';
            showToast('Помилка аналізу', 'error');
        }

    } catch (error) {
        console.error('Polling error:', error);
    }
}

function updateStatusDisplay(data) {
    if (data.status === 'PROCESSING') {
        elements.statusBadge.textContent = 'Обробка...';
        elements.statusMessage.textContent = 'Аналізуємо конкурентів і витягуємо терміни...';
    } else if (data.status === 'COMPLETED') {
        elements.statusBadge.textContent = 'Завершено';
        elements.statusBadge.classList.add('completed');
        elements.progressFill.classList.add('determinate');
        elements.progressFill.style.width = '100%';
        elements.statusMessage.textContent = 'Аналіз успішно завершено!';
    }
}

function displayResults(data) {
    elements.resultsContent.classList.remove('hidden');

    // Display competitors
    if (data.competitors) {
        displayCompetitors(data.competitors);
    }

    // Display terms
    if (data.terms) {
        displayTerms(data.terms);
    }

    // Display guidelines
    if (data.guidelines) {
        displayGuidelines(data.guidelines);
    }
}

function displayCompetitors(competitors) {
    elements.competitorsBody.innerHTML = competitors.map((comp, index) => `
        <tr>
            <td>${comp.position}</td>
            <td><a href="${comp.url}" target="_blank" class="text-accent">${new URL(comp.url).hostname}</a></td>
            <td>${comp.title || 'N/A'}</td>
            <td>${comp.word_count || 0}</td>
            <td><span class="badge ${comp.status === 'VALID' ? 'completed' : ''}">${comp.status}</span></td>
            <td>
                <label class="toggle">
                    <input type="checkbox" ${comp.enabled ? 'checked' : ''} 
                           onchange="handleCompetitorToggle('${comp.url}', this.checked)">
                    <span class="toggle-slider"></span>
                </label>
            </td>
        </tr>
    `).join('');
}

function displayTerms(terms) {
    const topTerms = terms.slice(0, 30); // Show top 30
    elements.termsBody.innerHTML = topTerms.map(term => `
        <tr>
            <td><strong>${term.term}</strong></td>
            <td>${term.range.min}</td>
            <td>${term.range.max}</td>
            <td>${term.range.median}</td>
        </tr>
    `).join('');
}

function displayGuidelines(guidelines) {
    elements.guidelinesGrid.innerHTML = `
        <div class="guideline-item">
            <h4>📝 Кількість слів</h4>
            <p>${guidelines.word_count.min} - ${guidelines.word_count.max}</p>
            <small>Медіана: ${guidelines.word_count.median}</small>
        </div>
        <div class="guideline-item">
            <h4>📑 Заголовки</h4>
            <p>${guidelines.headings_count.min} - ${guidelines.headings_count.max}</p>
            <small>Медіана: ${guidelines.headings_count.median}</small>
        </div>
        <div class="guideline-item">
            <h4>🖼️ Зображення</h4>
            <p>${guidelines.images.min} - ${guidelines.images.max}</p>
            <small>Медіана: ${guidelines.images.median}</small>
        </div>
    `;
}

async function handleCompetitorToggle(url, enabled) {
    try {
        await toggleCompetitor(state.currentAnalysisId, url, enabled);
        showToast(`Конкурент ${enabled ? 'увімкнено' : 'вимкнено'}`, 'success');
    } catch (error) {
        showToast('Помилка оновлення', 'error');
    }
}

// ===== Content Scoring =====
function handleEditorInput() {
    const text = elements.contentEditor.value;

    // Update stats
    const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
    const chars = text.length;

    elements.wordCount.textContent = words;
    elements.charCount.textContent = chars;

    // Debounce scoring
    if (state.scoreTimeout) {
        clearTimeout(state.scoreTimeout);
    }

    if (text.trim().length > 0) {
        state.scoreTimeout = setTimeout(() => performScoring(text), SCORE_DEBOUNCE);
    }
}

async function performScoring(text) {
    if (!state.currentAnalysisId) return;

    const format = document.querySelector('input[name="format"]:checked').value;

    try {
        const scoreData = await scoreContent(state.currentAnalysisId, text, format);
        displayScore(scoreData);
    } catch (error) {
        console.error('Scoring error:', error);
    }
}

function displayScore(scoreData) {
    // Animate total score
    animateScore(scoreData.total_score);

    // Update breakdown
    if (scoreData.breakdown) {
        updateBreakdown('terms', scoreData.breakdown.terms);
        updateBreakdown('structure', scoreData.breakdown.structure);
        updateBreakdown('headings', scoreData.breakdown.headings);
    }

    // Show term details
    if (scoreData.term_details) {
        displayTermDetails(scoreData.term_details);
    }

    // Show recommendations
    if (scoreData.structure_details || scoreData.headings_details) {
        generateRecommendations(scoreData);
    }
}

function animateScore(targetScore) {
    const startScore = parseInt(elements.scoreNumber.textContent) || 0;
    const duration = 1000;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentScore = Math.round(startScore + (targetScore - startScore) * easeOutQuart);

        elements.scoreNumber.textContent = currentScore;

        // Update circle
        const circumference = 2 * Math.PI * 90;
        const offset = circumference - (currentScore / 100) * circumference;
        elements.scoreCircle.style.strokeDashoffset = offset;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

function updateBreakdown(type, data) {
    const bar = elements[`${type}Bar`];
    const score = elements[`${type}Score`];

    if (bar && score && data) {
        const percentage = (data.score / data.max) * 100;
        bar.style.width = `${percentage}%`;
        score.textContent = `${data.score}/${data.max}`;
    }
}

function displayTermDetails(termDetails) {
    elements.termDetailsCard.classList.remove('hidden');

    elements.termsGrid.innerHTML = termDetails.map(term => `
        <div class="term-badge ${term.status}">
            <div class="term-name">${term.term}</div>
            <div class="term-count">
                ${term.current} / ${term.recommended_min}-${term.recommended_max}
            </div>
        </div>
    `).join('');
}

function generateRecommendations(scoreData) {
    const recommendations = [];

    // Check word count
    if (scoreData.structure_details && scoreData.structure_details.word_count) {
        const wc = scoreData.structure_details.word_count;
        if (wc.current < wc.recommended_min) {
            recommendations.push(`Збільште кількість слів до ${wc.recommended_min}`);
        }
    }

    // Check headings
    if (scoreData.headings_details) {
        if (!scoreData.headings_details.has_h1) {
            recommendations.push('Додайте заголовок H1');
        }
    }

    if (recommendations.length > 0) {
        elements.recommendations.classList.remove('hidden');
        elements.recommendationsList.innerHTML = recommendations.map(r => `<li>${r}</li>`).join('');
    }
}

// ===== Tab Management =====
function switchTab(tabName) {
    // Update active tab
    elements.tabs.forEach(tab => {
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Update active pane
    elements.tabPanes.forEach(pane => {
        if (pane.id === `${tabName}Tab`) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
}

// ===== Toast Notifications =====
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== Utility Functions =====
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}
