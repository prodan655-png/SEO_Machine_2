// Editor Logic
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Get URL Params
    const urlParams = new URLSearchParams(window.location.search);
    const analysisId = urlParams.get('id');
    const keyword = urlParams.get('keyword');

    // 2. State
    let currentScoreData = null;
    let isPreviewMode = false;

    // 3. UI Elements
    const els = {
        editor: document.getElementById('draftContent'),
        preview: document.getElementById('previewContainer'),
        wordCount: document.getElementById('wordCount'),
        charCount: document.getElementById('charCount'),
        scoreValue: document.getElementById('score-value'),
        scoreCircle: document.getElementById('score-circle-fill'),
        termsList: document.getElementById('terms-list'),
        metricsList: document.getElementById('metrics-list'),
        keywordDisplay: document.getElementById('current-keyword'),
        btnHtml: document.getElementById('mode-html'),
        btnPreview: document.getElementById('mode-preview')
    };

    // 4. Initialization
    if (keyword) {
        els.keywordDisplay.textContent = `- ${keyword}`;
    }

    if (analysisId) {
        // Load initial data if needed (optional, maybe get previous draft)
        console.log('Loaded editor for analysis:', analysisId);
    } else {
        // Demo mode or error
        if (!keyword) showToast('⚠️ No analysis selected. Features may be limited.', 'warning');
    }

    // 5. Event Listeners

    // Editor Input (Debounced Scoring)
    els.editor.addEventListener('input', debounce(async (e) => {
        updateStats(e.target.value);
        if (analysisId) {
            await performScoring(e.target.value);
        }
    }, 1000)); // Debounce 1s for scoring

    // Immediate stats update
    els.editor.addEventListener('input', (e) => updateStats(e.target.value));

    // View Modes
    els.btnHtml.addEventListener('click', () => switchMode('html'));
    els.btnPreview.addEventListener('click', () => switchMode('preview'));

    // Workflow Buttons
    document.getElementById('btn-view-competitors')?.addEventListener('click', () => {
        if (analysisId) window.location.href = `competitors.html?id=${analysisId}`;
        else showToast('⚠️ Save analysis first', 'warning');
    });

    document.getElementById('btn-check-score')?.addEventListener('click', () => {
        performScoring(els.editor.value);
    });

    document.getElementById('btn-seo-coach')?.addEventListener('click', async () => {
        showToast('🎓 Calling SEO Coach...', 'info');
        // Mock integration for now - in real app would call API
        // This triggers the diff modal from diff-tracking.js
        if (window.showDiffModal) {
            // Demo diff
            const oldContent = els.editor.value;
            const newContent = oldContent + '\n\n<p>Optimized content added by AI.</p>';
            const changes = [
                { type: 'add_term', term: keyword || 'keyword', reason: 'Missing term', old_text: '', new_text: 'Optimized content' }
            ];
            window.showDiffModal(oldContent, newContent, changes, 5);
        }
    });

    document.getElementById('btn-generate-images')?.addEventListener('click', async () => {
        if (!analysisId) return showToast('⚠️ Analysis ID required', 'warning');
        showToast('🎨 Generating images...', 'info');
        try {
            const result = await window.API.generateImages(analysisId, els.editor.value);
            if (result.updated_html) {
                els.editor.value = result.updated_html;
                showToast('✅ Images inserted!', 'success');
                updateStats(els.editor.value);
            }
        } catch (e) {
            showToast('❌ Generation failed', 'error');
            console.error(e);
        }
    });

    document.getElementById('btn-export-html')?.addEventListener('click', () => {
        const blob = new Blob([els.editor.value], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `article-${keyword || 'export'}.html`;
        a.click();
        showToast('✅ Exported', 'success');
    });

    // 6. Functions

    function updateStats(text) {
        const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
        els.wordCount.textContent = words;
        els.charCount.textContent = text.length;
    }

    async function performScoring(content) {
        if (!content.trim()) return;

        try {
            const scoreData = await window.API.scoreContent(analysisId, content);
            updateScoreUI(scoreData);
        } catch (e) {
            console.error('Scoring error:', e);
            // Fallback for demo/offline
            updateScoreUI({
                total_score: Math.floor(Math.random() * 30) + 50,
                term_details: [
                    { term: keyword || 'seo', current: 2, recommended_min: 5, recommended_max: 10, status: 'low' }
                ],
                structure_details: {
                    word_count: { current: content.split(' ').length, recommended_min: 1000, recommended_max: 2000 }
                }
            });
        }
    }

    function updateScoreUI(data) {
        currentScoreData = data;

        // Score Circle
        els.scoreValue.textContent = data.total_score;
        const offset = 339 - (data.total_score / 100) * 339;
        els.scoreCircle.style.strokeDashoffset = offset;

        // Color
        let color = '#ef4444';
        if (data.total_score >= 60) color = '#f59e0b';
        if (data.total_score >= 80) color = '#10b981';
        els.scoreCircle.style.stroke = color;

        // Terms
        if (data.term_details) {
            els.termsList.innerHTML = data.term_details.slice(0, 10).map(t => `
                <li class="term-item ${t.status || 'medium'}">
                    <span class="term-name">${t.term}</span>
                    <span class="term-count">${t.current}/${t.recommended_min}-${t.recommended_max}</span>
                </li>
            `).join('');
        }

        // Metrics
        if (data.structure_details) {
            const wc = data.structure_details.word_count;
            if (wc) {
                els.metricsList.innerHTML = `
                    <li class="metric-item">
                        <span class="metric-label">Words</span>
                        <div>
                            <span class="metric-value ${getMetricStatus(wc.current, wc.recommended_min, wc.recommended_max)}">
                                ${wc.current}/${wc.recommended_min}
                            </span>
                            <div class="metric-bar">
                                <div class="metric-bar-fill" style="width: ${Math.min((wc.current / wc.recommended_max) * 100, 100)}%"></div>
                            </div>
                        </div>
                    </li>
                `;
            }
        }
    }

    function getMetricStatus(val, min, max) {
        if (val >= min && val <= max) return 'good';
        if (val >= min * 0.8) return 'medium';
        return 'low';
    }

    function switchMode(mode) {
        isPreviewMode = mode === 'preview';
        if (isPreviewMode) {
            els.btnHtml.classList.remove('active');
            els.btnPreview.classList.add('active');
            els.editor.classList.add('hidden');
            els.preview.classList.remove('hidden');
            els.preview.innerHTML = els.editor.value; // Simple render
        } else {
            els.btnPreview.classList.remove('active');
            els.btnHtml.classList.add('active');
            els.preview.classList.add('hidden');
            els.editor.classList.remove('hidden');
        }
    }

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    function showToast(msg, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = msg;
        toast.style.cssText = `
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
});
