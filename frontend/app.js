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
    contentEditor: document.getElementById('draftContent'),
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

    // AI Writer
    useCoachCheckbox: document.getElementById('useCoachCheckbox'),

    // Toast
    toastContainer: document.getElementById('toastContainer'),

    // AI Coach
    coachBtn: document.getElementById('coachBtn')
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

    // AI Coach
    if (elements.coachBtn) {
        elements.coachBtn.addEventListener('click', (e) => {
            console.log('Coach button clicked via listener');
            e.preventDefault();
            getSEOCoaching();
        });
    }
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
    if (!state.currentAnalysisId) return;

    try {
        const data = await getAnalysis(state.currentAnalysisId);
        handleAnalysisResponse(data);
    } catch (error) {
        console.error('Polling error:', error);
        if (state.pollingInterval) {
            clearInterval(state.pollingInterval);
            state.pollingInterval = null;
        }
    }
}

function handleAnalysisResponse(data) {
    console.log('DEBUG analysis status:', data.status, data);

    const rawStatus = data.status || '';
    const status = rawStatus.toLowerCase();

    updateStatusDisplay(data);

    if (status === 'completed') {
        // Stop polling
        if (state.pollingInterval) {
            clearInterval(state.pollingInterval);
            state.pollingInterval = null;
        }

        state.analysisData = data;
        displayResults(data);
        elements.scoringTab.disabled = false;
        document.getElementById('aiWriterTab').disabled = false;
        showToast('Аналіз завершено!', 'success');
    } else if (status === 'failed') {
        if (state.pollingInterval) {
            clearInterval(state.pollingInterval);
            state.pollingInterval = null;
        }
        showToast(data.error_message || 'Аналіз завершився з помилкою.', 'error');
    }
}

function updateStatusDisplay(data) {
    const status = String(data.status).toLowerCase();

    if (status === 'completed') {
        elements.statusBadge.textContent = 'Завершено';
        elements.statusBadge.className = 'badge completed';
        elements.progressFill.className = 'progress-fill determinate';
        elements.progressFill.style.width = '100%';
        elements.statusMessage.textContent = 'Аналіз успішно завершено!';
    } else if (status === 'failed') {
        elements.statusBadge.textContent = 'Помилка';
        elements.statusBadge.style.background = 'var(--error)';
        elements.statusMessage.textContent = data.error_message || 'Щось пішло не так під час аналізу.';
    } else {
        elements.statusBadge.textContent = 'Обробка...';
        elements.statusBadge.className = 'badge';
        elements.statusMessage.textContent = 'Завантаження даних з пошукової видачі...';
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
    elements.competitorsBody.innerHTML = competitors.map((comp, index) => {
        let hostname = 'N/A';
        try {
            // Handle mock:// URLs manually or standard URLs via URL object
            if (comp.url.startsWith('mock://')) {
                hostname = comp.url.replace('mock://', '').split('/')[0];
            } else {
                hostname = new URL(comp.url).hostname;
            }
        } catch (e) {
            hostname = comp.url;
        }

        return `
        <tr>
            <td>${comp.position}</td>
            <td><a href="${comp.url}" target="_blank" class="text-accent">${hostname}</a></td>
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
    `}).join('');
}

function displayTerms(terms) {
    const topTerms = terms.slice(0, 30); // Show top 30
    elements.termsBody.innerHTML = topTerms.map(term => `
        <tr>
            <td><strong>${term.term}</strong></td>
            <td>${term.min_recommended || 0}</td>
            <td>${term.max_recommended || 0}</td>
            <td>${(term.avg_usage || 0).toFixed(1)}</td>
        </tr>
    `).join('');
}

function displayGuidelines(guidelines) {
    const wc = guidelines.word_count || {};
    const headings = guidelines.headings || {};
    const images = guidelines.images || {};

    elements.guidelinesGrid.innerHTML = `
        <div class="guideline-item">
            <h4>📝 Кількість слів</h4>
            <p>${wc.min != null ? wc.min : 0} - ${wc.max != null ? wc.max : 0}</p>
            <small>Медіана: ${wc.median != null ? wc.median : 0}</small>
        </div>
        <div class="guideline-item">
            <h4>📑 Заголовки</h4>
            <p>${headings.min != null ? headings.min : 0} - ${headings.max != null ? headings.max : 0}</p>
            <small>Медіана: ${headings.median != null ? headings.median : 0}</small>
        </div>
        <div class="guideline-item">
            <h4>🖼️ Зображення</h4>
            <p>${images.min != null ? images.min : 0} - ${images.max != null ? images.max : 0}</p>
            <small>Медіана: ${images.median != null ? images.median : 0}</small>
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
    const text = elements.contentEditor?.value || '';

    console.log('DEBUG handleEditorInput called, text length:', text.length);

    // Update stats
    const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
    const chars = text.length;

    if (elements.wordCount) elements.wordCount.textContent = words;
    if (elements.charCount) elements.charCount.textContent = chars;

    // Debounced scoring
    clearTimeout(state.scoringTimeout);
    if (text.trim().length > 0) {
        state.scoringTimeout = setTimeout(() => {
            console.log('DEBUG triggering performScoring');
            performScoring(text);
        }, 500);
    }
}

async function performScoring(text) {
    if (!state.currentAnalysisId) return;

    const formatInput = document.querySelector('input[name="contentMode"]:checked');
    const format = formatInput ? formatInput.value : 'html';

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

// ===== SEO Coach (AI) =====
async function getSEOCoaching() {
    console.log('DEBUG getSEOCoaching called');
    console.log('DEBUG Current Analysis ID:', state.currentAnalysisId);

    if (!state.currentAnalysisId) {
        console.error('DEBUG No analysis ID found');
        showToast('Спочатку створіть аналіз', 'error');
        return;
    }

    const currentScore = parseInt(elements.scoreNumber?.textContent || 0);
    console.log('DEBUG currentScore:', currentScore);

    if (currentScore === 0) {
        showToast('Спочатку оцініть ваш контент', 'error');
        return;
    }

    const targetScore = 85;
    const coachPanel = document.getElementById('coachPanel');
    const coachContent = document.getElementById('coachContent');

    console.log('DEBUG Opening coach panel');
    coachPanel.classList.remove('hidden');
    // Small delay to allow display:block to apply before transition
    setTimeout(() => {
        coachPanel.classList.add('show');
    }, 10);

    // Show loading
    coachContent.innerHTML = `
        <div class="coach-loader">
            <div class="spinner"></div>
            <p>Генерую рекомендації...</p>
        </div>
    `;

    try {
        console.log('DEBUG Sending request to backend');
        const response = await fetch(`${API_BASE_URL}/api/ai/coach`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                analysis_id: state.currentAnalysisId,
                current_score: currentScore,
                target_score: targetScore
            })
        });

        console.log('DEBUG Response status:', response.status);

        if (!response.ok) {
            const error = await response.json();
            console.error('DEBUG Backend error:', error);
            throw new Error(error.detail || 'AI Coach недоступний');
        }

        const coaching = await response.json();
        console.log('DEBUG Received coaching:', coaching);

        // Store for AI Writer
        state.lastCoaching = coaching;

        displayCoachingPanel(coaching, currentScore, targetScore);

    } catch (error) {
        console.error('Coaching error:', error);
        coachContent.innerHTML = `
            <div class="coach-error">
                <p>⚠️ ${error.message}</p>
                <p style="margin-top: 1rem; font-size: 0.875rem;">
                    Переконайтеся що AI_ENABLED=true в конфігурації
                </p>
            </div>
        `;
    }
}

function displayCoachingPanel(coaching, currentScore, targetScore) {
    console.log('DEBUG displayCoachingPanel called with:', coaching);
    const coachContent = document.getElementById('coachContent');
    console.log('DEBUG coachContent element:', coachContent);

    let html = `
        <div class="coach-intro">
            <p>Ваш score: <strong>${currentScore}/100</strong></p>
            <p>Мета: <strong>${targetScore}/100</strong></p>
            <p style="color: var(--accent-light); margin-top: 0.5rem;">
                Гайд покращень ↓
            </p>
        </div>
        <hr style="border-color: var(--border); margin: 1.5rem 0;">
    `;

    // Priority Actions
    if (coaching.priority_actions && coaching.priority_actions.length > 0) {
        html += `
            <div class="coach-section">
                <h4>🎯 Пріоритетні дії</h4>
                <ul class="priority-actions">
        `;

        coaching.priority_actions.forEach((action, index) => {
            html += `
                <li class="action-item" id="action-${index}">
                    <div class="action-header">
                        <input type="checkbox" class="action-checkbox" 
                               onchange="toggleActionItem(${index})">
                        <div class="action-title">${action.action}</div>
                        <span class="impact-badge impact-${action.impact}">${action.impact}</span>
                    </div>
                    <div class="action-meta">
                        <span>📊 ${action.score_gain}</span>
                        <span>⏱️ ${action.difficulty}</span>
                    </div>
                    <div class="action-details">${action.details}</div>
                </li>
            `;
        });

        html += `
                </ul>
            </div>
        `;
    }

    // Content Suggestions
    if (coaching.content_suggestions && coaching.content_suggestions.length > 0) {
        html += `
            <div class="coach-section">
                <h4>💡 Поради</h4>
                <ul class="content-suggestions">
        `;

        coaching.content_suggestions.forEach(suggestion => {
            html += `<li>${suggestion}</li>`;
        });

        html += `
                </ul>
            </div>
        `;
    }

    // Term Recommendations
    if (coaching.term_recommendations) {
        const { add_more, reduce } = coaching.term_recommendations;

        if ((add_more && add_more.length > 0) || (reduce && reduce.length > 0)) {
            html += `
                <div class="coach-section">
                    <h4>🔑 Терміни</h4>
                    <div class="term-recommendations">
            `;

            if (add_more && add_more.length > 0) {
                html += `
                    <div class="term-list">
                        <h5>Додати:</h5>
                        <div class="term-chips">
                `;
                add_more.forEach(term => {
                    html += `<span class="term-chip">${term}</span>`;
                });
                html += `
                        </div>
                    </div>
                `;
            }

            if (reduce && reduce.length > 0) {
                html += `
                    <div class="term-list">
                        <h5>Зменшити:</h5>
                        <div class="term-chips">
                `;
                reduce.forEach(term => {
                    html += `<span class="term-chip reduce">${term}</span>`;
                });
                html += `
                        </div>
                    </div>
                `;
            }

            html += `
                    </div>
                </div>
            `;
        }
    }

    // Estimated Time
    if (coaching.estimated_time) {
        html += `
            <div class="estimated-time">
                ⏱️ Орієнтовний час: ${coaching.estimated_time}
            </div>
        `;
    }

    coachContent.innerHTML = html;

    // Add "Iterate" button if we have content
    if (currentBrief || elements.contentEditor?.value) {
        const btnContainer = document.createElement('div');
        btnContainer.style.marginTop = '2rem';
        btnContainer.style.display = 'flex';
        btnContainer.style.gap = '1rem';
        btnContainer.innerHTML = `
            <button class="btn btn-primary" onclick="startIterationFromCoach()" style="flex: 1;">
                <span class="btn-text">🔄 Покращити ітеративно</span>
            </button>
            <button class="btn btn-secondary" onclick="rewriteWithCoach()" style="flex: 1;">
                <span class="btn-text">⚠️ Переписати (старий)</span>
            </button>
        `;
        coachContent.appendChild(btnContainer);

        // Add explanation
        const explanation = document.createElement('div');
        explanation.style.marginTop = '1rem';
        explanation.style.padding = '1rem';
        explanation.style.background = 'rgba(59, 130, 246, 0.1)';
        explanation.style.borderRadius = '0.5rem';
        explanation.style.fontSize = '0.85rem';
        explanation.style.color = 'var(--text-secondary)';
        explanation.innerHTML = `
            <strong>💡 Рекомендація:</strong> Використовуйте "Покращити ітеративно" - це гарантує покращення score.
            Старий метод може погіршити результат.
        `;
        coachContent.appendChild(explanation);
    }
}

function rewriteWithCoach() {
    // 1. Close coach panel
    closeCoachPanel();

    // 2. Switch to AI Writer tab
    switchTab('ai-writer');

    // 3. Reset to Step 2 (Brief) if we are in Step 3, to allow regeneration
    document.getElementById('aiStep3').classList.add('hidden');
    document.getElementById('aiStep2').classList.remove('hidden');

    // 4. Check the "Use Coach" checkbox
    if (elements.useCoachCheckbox) {
        elements.useCoachCheckbox.checked = true;
    }

    // 5. Scroll to generate button
    const generateBtn = document.querySelector('#aiStep2 .btn-primary');
    if (generateBtn) {
        generateBtn.scrollIntoView({ behavior: 'smooth' });

        // Auto-trigger generation
        showToast('🔄 Покращуємо статтю...', 'info');
        generateArticle();
    }
}

function closeCoachPanel() {
    const panel = document.getElementById('coachPanel');
    panel.classList.remove('show');
    setTimeout(() => {
        panel.classList.add('hidden');
    }, 300); // Wait for transition
}

function toggleActionItem(index) {
    const item = document.getElementById(`action-${index}`);
    const checkbox = item.querySelector('.action-checkbox');

    if (checkbox.checked) {
        item.classList.add('checked');
    } else {
        item.classList.remove('checked');
    }
}

// ===== AI Writer =====
let currentBrief = null;

async function generateBrief() {
    if (!state.currentAnalysisId) {
        showToast('Спочатку створіть аналіз', 'error');
        return;
    }

    const btn = document.querySelector('#aiStep1 .btn-primary');
    const loader = btn.querySelector('.btn-loader');
    const text = btn.querySelector('.btn-text');

    btn.disabled = true;
    text.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/api/ai/brief`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                analysis_id: state.currentAnalysisId,
                tone: 'professional'
            })
        });

        if (!response.ok) throw new Error('Помилка генерації брифу');

        currentBrief = await response.json();

        // Show step 2
        document.getElementById('aiStep1').classList.add('hidden');
        document.getElementById('aiStep2').classList.remove('hidden');

        // Fill editor
        const editor = document.getElementById('briefEditor');
        editor.value = JSON.stringify(currentBrief, null, 2);

        showToast('Бриф згенеровано!', 'success');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.disabled = false;
        text.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

async function generateArticle() {
    if (!currentBrief) return;

    const btn = document.querySelector('#aiStep2 .btn-primary');
    const loader = btn.querySelector('.btn-loader');
    const text = btn.querySelector('.btn-text');

    // Get updated brief from editor
    try {
        const editorContent = document.getElementById('briefEditor').value;
        currentBrief = JSON.parse(editorContent);
    } catch (e) {
        showToast('Помилка в JSON форматі брифу', 'error');
        return;
    }

    btn.disabled = true;
    text.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
        const useCoach = document.getElementById('useCoachCheckbox')?.checked;
        let coachActions = null;

        if (useCoach && state.lastCoaching) {
            // Format coach actions for the AI
            coachActions = state.lastCoaching.priority_actions
                .map(a => `- ${a.action} (${a.details})`)
                .join('\n');

            if (state.lastCoaching.term_recommendations?.add_more) {
                coachActions += '\n\nТакож додай ці терміни: ' +
                    state.lastCoaching.term_recommendations.add_more.join(', ');
            }
        }

        console.log('🚀 Sending to AI Writer:', {
            brief: currentBrief,
            coachActions: coachActions
        });

        const response = await fetch(`${API_BASE_URL}/api/ai/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                brief: currentBrief,
                tone: 'professional',
                language: document.getElementById('language').value,
                coach_actions: coachActions
            })
        });

        if (!response.ok) throw new Error('Помилка генерації статті');

        const result = await response.json();

        // Store result temporarily
        state.generatedContent = result.article;

        // Show preview
        const previewDiv = document.getElementById('articlePreview');
        const htmlCode = document.getElementById('htmlCode');
        previewDiv.innerHTML = result.article;
        htmlCode.value = result.article;

        // Show step 3
        document.getElementById('aiStep2').classList.add('hidden');
        document.getElementById('aiStep3').classList.remove('hidden');

        showToast('Статтю написано!', 'success');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.disabled = false;
        text.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

function copyToEditor() {
    if (state.generatedContent) {
        if (elements.contentEditor) {
            elements.contentEditor.value = state.generatedContent;
        }
        handleEditorInput(); // Trigger scoring
        switchTab('scoring');
        showToast('Контент перенесено в редактор. Перевірте оцінку!', 'success');

        // Reset steps
        // resetAiSteps(); // Don't reset steps to allow iterative workflow
        document.getElementById('aiStep1').classList.add('hidden'); // Hide brief input
        document.getElementById('aiStep2').classList.add('hidden'); // Hide generation
        document.getElementById('aiStep3').classList.add('hidden'); // Hide preview
    }
}

function resetAiSteps() {
    document.getElementById('aiStep1').classList.remove('hidden');
    document.getElementById('aiStep2').classList.add('hidden');
    document.getElementById('aiStep3').classList.add('hidden');
    currentBrief = null;
    state.generatedContent = null;
}

function togglePreview() {
    const preview = document.getElementById('articlePreview');
    const htmlCode = document.getElementById('htmlCode');
    const toggle = document.getElementById('previewToggle');

    if (htmlCode.classList.contains('hidden')) {
        // Show HTML code
        preview.classList.add('hidden');
        htmlCode.classList.remove('hidden');
        toggle.textContent = 'Показати Preview';
    } else {
        // Show preview
        htmlCode.classList.add('hidden');
        preview.classList.remove('hidden');
        toggle.textContent = 'Показати HTML';
    }
}

function switchEditorMode(mode) {
    const htmlContainer = document.getElementById('htmlEditorContainer');
    const previewContainer = document.getElementById('previewContainer');
    const previewDiv = document.getElementById('contentPreview');
    const editor = document.getElementById('draftContent');
    const btnHtml = document.getElementById('editorModeHtml');
    const btnPreview = document.getElementById('editorModePreview');

    if (mode === 'preview') {
        // Show preview
        htmlContainer.classList.add('hidden');
        previewContainer.classList.remove('hidden');
        previewDiv.innerHTML = editor.value;
        btnHtml.classList.remove('btn-primary');
        btnHtml.classList.add('btn-secondary');
        btnPreview.classList.remove('btn-secondary');
        btnPreview.classList.add('btn-primary');
    } else {
        // Show HTML editor
        previewContainer.classList.add('hidden');
        htmlContainer.classList.remove('hidden');
        btnPreview.classList.remove('btn-primary');
        btnPreview.classList.add('btn-secondary');
        btnHtml.classList.remove('btn-secondary');
        btnHtml.classList.add('btn-primary');
    }
}

// ===== Utility Functions =====
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// ===== Iteration Functions =====
let iterationState = {
    running: false,
    currentStep: 0,
    maxSteps: 5,
    initialScore: 0,
    targetScore: 85,
    iterations: []
};

async function startIteration(targetScore = 85, maxIterations = 10) {
    console.log('🔄 startIteration called', { targetScore, maxIterations });
    console.log('State:', { analysisId: state.currentAnalysisId, currentScore: state.currentScore });

    if (!state.currentAnalysisId) {
        console.error('❌ No analysis ID');
        showToast('Спочатку створіть аналіз', 'error');
        return;
    }

    const content = elements.contentEditor?.value;
    console.log('Content length:', content?.length);

    if (!content) {
        console.error('❌ No content');
        showToast('Немає контенту для покращення', 'error');
        return;
    }

    console.log('✅ Starting iteration...');

    // Show immediate feedback
    showToast('🔄 Запускаю ітеративне покращення... Це займе 2-3 хвилини', 'info');

    iterationState.running = true;
    iterationState.currentStep = 0;
    iterationState.maxSteps = maxIterations;
    iterationState.initialScore = state.currentScore || 0;
    iterationState.targetScore = targetScore;
    iterationState.iterations = [];

    // Show modal
    console.log('Opening iteration modal...');
    const modal = document.getElementById('iterationModal');
    console.log('Modal element:', modal);

    if (!modal) {
        console.error('❌ Modal element not found!');
        showToast('Помилка: модальне вікно не знайдено', 'error');
        return;
    }

    modal.classList.remove('hidden');
    modal.style.display = 'flex';  // Force display
    modal.style.zIndex = '9999';   // Ensure it's on top
    console.log('Modal classes after remove hidden:', modal.className);
    console.log('Modal computed style:', window.getComputedStyle(modal).display);

    document.getElementById('iterationScoreTracker').textContent =
        `${iterationState.initialScore} → ${targetScore}`;
    document.getElementById('iterationCounter').textContent =
        `Обробка... 0/${maxIterations}`;
    document.getElementById('iterationProgressBar').style.width = '0%';

    // Show loading state
    const stepsContainer = document.getElementById('iterationSteps');
    stepsContainer.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div class="spinner" style="margin: 0 auto 1rem;"></div>
            <p style="color: var(--text-secondary);">⏳ Аналізую контент та генерую покращення...</p>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.5rem;">Це може зайняти 1-3 хвилини</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE_URL}/api/ai/iterate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content: content,
                analysis_id: state.currentAnalysisId,
                max_iterations: maxIterations,
                target_score: targetScore
            })
        });

        if (!response.ok) throw new Error('Помилка ітерації');

        const result = await response.json();
        console.log('✅ Iteration response:', result);
        console.log('Iterations count:', result.iterations?.length);
        console.log('Final score:', result.final_score);

        displayIterationResult(result);

    } catch (error) {
        console.error('Iteration error:', error);
        showToast('Помилка при покращенні', 'error');
        closeIterationModal();
    }
}

function displayIterationResult(result) {
    console.log('📊 displayIterationResult called with:', result);

    iterationState.running = false;
    iterationState.iterations = result.iterations || [];

    const stepsContainer = document.getElementById('iterationSteps');
    stepsContainer.innerHTML = '';

    result.iterations.forEach((iteration) => {
        const stepDiv = document.createElement('div');
        stepDiv.className = `iteration-step ${iteration.success ? 'success' : 'failed'}`;

        const scoreDelta = iteration.score_delta;
        const scoreClass = scoreDelta > 0 ? 'positive' : scoreDelta < 0 ? 'negative' : '';
        const scoreSign = scoreDelta > 0 ? '+' : '';

        stepDiv.innerHTML = `
            <div class="step-header">
                <span class="step-number">Крок ${iteration.step}</span>
                <span class="step-score ${scoreClass}">
                    ${iteration.old_score} → ${iteration.new_score} (${scoreSign}${scoreDelta})
                </span>
            </div>
            <div class="step-action">${iteration.action}</div>
            <div class="step-status">
                ${iteration.success ? '✅ Застосовано' : '❌ ' + (iteration.reason || 'Відхилено')}
            </div>
        `;

        stepsContainer.appendChild(stepDiv);
    });

    const progress = (result.final_score / result.target_score) * 100;
    document.getElementById('iterationProgressBar').style.width = `${Math.min(progress, 100)}%`;
    document.getElementById('iterationScoreTracker').textContent =
        `${result.initial_score} → ${result.final_score}`;
    document.getElementById('iterationCounter').textContent =
        `Завершено: ${result.improvements_made} покращень`;

    if (result.final_score > result.initial_score && result.final_content) {
        elements.contentEditor.value = result.final_content;
        handleEditorInput();
    }

    document.getElementById('stopIterationBtn').classList.add('hidden');
    document.getElementById('doneIterationBtn').classList.remove('hidden');

    showToast(
        result.success ?
            `✅ Ціль досягнуто! ${result.final_score}/${result.target_score}` :
            `🔄 Покращено: ${result.initial_score} → ${result.final_score}`,
        result.success ? 'success' : 'info'
    );
}

function stopIteration() {
    iterationState.running = false;
    showToast('Ітерацію зупинено', 'info');
    closeIterationModal();
}

function closeIterationModal() {
    const modal = document.getElementById('iterationModal');
    modal.classList.add('hidden');
    iterationState.running = false;
    document.getElementById('stopIterationBtn').classList.remove('hidden');
    document.getElementById('doneIterationBtn').classList.add('hidden');
}

// Start iteration from Coach panel
function startIterationFromCoach() {
    closeCoachPanel();
    startIteration(85, 10);  // Increased to 10 iterations
}
