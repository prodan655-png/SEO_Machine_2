// SurferSEO App - API Integration and Functionality
(function () {
    'use strict';

    const API_BASE = 'http://localhost:8000';

    // State
    let currentAnalysisId = null;
    let currentScore = null;

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        console.log('🚀 SurferSEO App initializing...');

        // Attach event listeners
        attachEventListeners();

        // Check API connection
        checkAPIConnection();
    }

    function attachEventListeners() {
        // Editor input - update word count
        const editor = document.getElementById('draftContent');
        if (editor) {
            editor.addEventListener('input', debounce(handleEditorInput, 500));
        }

        // Workflow buttons
        attachWorkflowButtons();
    }

    function attachWorkflowButtons() {
        // All workflow buttons
        document.querySelectorAll('.workflow-action-btn').forEach((btn) => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const text = this.textContent.trim();

                if (text.includes('View Competitors')) {
                    window.open('index.html', '_blank');
                } else if (text.includes('Generate Outline')) {
                    window.open('index.html', '_blank');
                } else if (text.includes('AI Writer')) {
                    window.open('index.html', '_blank');
                } else if (text.includes('Auto-Optimize')) {
                    autoOptimize();
                } else if (text.includes('Iterate')) {
                    showToast('Iterate Content - в розробці', 'info');
                } else if (text.includes('Check Score')) {
                    performScoring();
                } else if (text.includes('SEO Coach')) {
                    showToast('SEO Coach - в розробці', 'info');
                } else if (text.includes('Export HTML')) {
                    exportHTML();
                } else if (text.includes('Copy Code')) {
                    copyToClipboard();
                }
            });
        });

        // Auto-Optimize button in sidebar
        const autoOptBtn = document.querySelector('.auto-optimize-btn');
        if (autoOptBtn) {
            autoOptBtn.addEventListener('click', performScoring);
        }
    }

    function handleEditorInput(e) {
        const text = e.target.value;

        // Update word/char count
        const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
        const chars = text.length;

        const wordCount = document.getElementById('wordCount');
        const charCount = document.getElementById('charCount');

        if (wordCount) wordCount.textContent = words;
        if (charCount) charCount.textContent = chars;
    }

    async function checkAPIConnection() {
        try {
            const response = await fetch(`${API_BASE}/health`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                showToast('✅ API Connected', 'success');
                console.log('✅ Backend API connected');
            } else {
                showToast('⚠️ API connection issue', 'warning');
            }
        } catch (error) {
            console.error('API connection error:', error);
            showToast('⚠️ Backend запущений? (порт 8000)', 'warning');
        }
    }

    async function performScoring() {
        const editor = document.getElementById('draftContent');
        if (!editor || !editor.value.trim()) {
            showToast('⚠️ Додайте контент для аналізу', 'warning');
            return;
        }

        const text = editor.value;
        const words = text.trim().split(/\s+/).length;

        if (words < 50) {
            showToast('⚠️ Потрібно мінімум 50 слів для аналізу', 'warning');
            return;
        }

        showToast('🔍 Аналізую контент...', 'info');

        try {
            // Create analysis if needed
            if (!currentAnalysisId) {
                const analysisResponse = await fetch(`${API_BASE}/api/analysis/create`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: 'SEO аналіз контенту',
                        location: 'Ukraine',
                        language: 'uk',
                        limit: 10
                    })
                });

                if (!analysisResponse.ok) {
                    throw new Error('Failed to create analysis');
                }

                const analysisData = await analysisResponse.json();
                currentAnalysisId = analysisData.analysis_id;
                console.log('Created analysis:', currentAnalysisId);
            }

            // Score the content
            const scoreResponse = await fetch(`${API_BASE}/api/analysis/${currentAnalysisId}/score`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: text
                })
            });

            if (!scoreResponse.ok) {
                throw new Error('Scoring failed');
            }

            currentScore = await scoreResponse.json();
            console.log('Score data:', currentScore);

            // Update UI with real data
            updateScoreUI(currentScore);
            showToast(`✅ Оцінка: ${currentScore.total_score}/100`, 'success');

        } catch (error) {
            console.error('Scoring error:', error);
            showToast('ℹ️ Використовую demo дані', 'info');

            // Show demo data on error
            updateScoreUI({
                total_score: 75,
                term_details: [
                    { term: 'SEO', current: 5, recommended_min: 3, recommended_max: 7, status: 'good' },
                    { term: 'контент', current: 3, recommended_min: 4, recommended_max: 8, status: 'medium' },
                    { term: 'аналіз', current: 1, recommended_min: 3, recommended_max: 6, status: 'low' }
                ],
                structure_details: {
                    word_count: { current: words, recommended_min: 1800, recommended_max: 2500 }
                },
                headings_details: {
                    h2_count: 5,
                    h3_count: 3
                }
            });
        }
    }

    function updateScoreUI(scoreData) {
        if (!scoreData) return;

        // Update score circle
        const scoreValue = document.querySelector('.score-value-small');
        const scoreCircle = document.querySelector('.score-circle-small circle:nth-child(2)');

        if (scoreValue && scoreCircle) {
            const score = scoreData.total_score || 0;
            scoreValue.textContent = score;

            // Update circle (339 = circumference of r=54)
            const offset = 339 - (score / 100) * 339;
            scoreCircle.style.strokeDashoffset = offset;

            // Change color based on score
            if (score >= 80) {
                scoreCircle.style.stroke = '#10b981'; // green
            } else if (score >= 60) {
                scoreCircle.style.stroke = '#f59e0b'; // yellow
            } else {
                scoreCircle.style.stroke = '#ef4444'; // red
            }
        }

        // Update terms list
        if (scoreData.term_details && scoreData.term_details.length > 0) {
            const termsList = document.querySelector('.terms-list');
            if (termsList) {
                const topTerms = scoreData.term_details.slice(0, 10);
                termsList.innerHTML = topTerms.map(term => {
                    const status = term.status || 'medium';
                    return `
                        <li class="term-item ${status}">
                            <span class="term-name">${term.term}</span>
                            <span class="term-count">${term.current}/${term.recommended_min}-${term.recommended_max}</span>
                        </li>
                    `;
                }).join('');
            }
        }

        // Update metrics
        if (scoreData.structure_details) {
            const wc = scoreData.structure_details.word_count;
            if (wc) {
                updateMetric('Words', wc.current, wc.recommended_min, wc.recommended_max);
            }
        }

        if (scoreData.headings_details) {
            const totalHeadings = (scoreData.headings_details.h2_count || 0) +
                (scoreData.headings_details.h3_count || 0);
            updateMetric('Headings', totalHeadings, 6, 10);
        }

        // Estimate images from content
        const imageCount = (text.match(/<img/gi) || []).length;
        updateMetric('Images', imageCount, 3, 6);
    }

    function updateMetric(name, current, min, max) {
        const metricsList = document.querySelector('.metrics-list');
        if (!metricsList) return;

        const items = metricsList.querySelectorAll('.metric-item');
        let metricItem = null;

        items.forEach(item => {
            const label = item.querySelector('.metric-label');
            if (label && label.textContent === name) {
                metricItem = item;
            }
        });

        if (!metricItem) return;

        const valueEl = metricItem.querySelector('.metric-value');
        const barEl = metricItem.querySelector('.metric-bar-fill');

        if (!valueEl || !barEl) return;

        valueEl.textContent = `${current}/${min}-${max}`;

        // Calculate status
        const percentage = (current / max) * 100;
        let status = 'low';
        if (current >= min && current <= max) {
            status = 'good';
        } else if (current >= min * 0.8) {
            status = 'medium';
        }

        valueEl.className = `metric-value ${status}`;
        barEl.className = `metric-bar-fill ${status}`;
        barEl.style.width = `${Math.min(percentage, 100)}%`;
    }

    function autoOptimize() {
        performScoring();
    }

    function exportHTML() {
        const content = document.getElementById('draftContent')?.value || '';
        if (!content.trim()) {
            showToast('⚠️ Немає контенту для експорту', 'warning');
            return;
        }

        const blob = new Blob([content], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `article-${Date.now()}.html`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('✅ HTML експортовано!', 'success');
    }

    function copyToClipboard() {
        const content = document.getElementById('draftContent')?.value || '';
        if (!content.trim()) {
            showToast('⚠️ Немає контенту для копіювання', 'warning');
            return;
        }

        navigator.clipboard.writeText(content).then(() => {
            showToast('✅ Скопійовано в буфер обміну!', 'success');
        }).catch(() => {
            showToast('❌ Помилка копіювання', 'error');
        });
    }

    // Utility functions
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    let toastContainer = null;
    function showToast(message, type = 'info') {
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            `;
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
            color: white;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
            font-size: 0.875rem;
            min-width: 250px;
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                toast.remove();
                if (toastContainer.children.length === 0) {
                    toastContainer.remove();
                    toastContainer = null;
                }
            }, 300);
        }, 3000);
    }

    // Add animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    console.log('✅ SurferSEO App loaded');
})();
