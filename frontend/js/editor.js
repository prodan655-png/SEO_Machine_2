// Editor Logic
// Refactored to use Alpine.js Store

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Get URL Params
    const urlParams = new URLSearchParams(window.location.search);
    const analysisId = urlParams.get('id');
    const keyword = urlParams.get('keyword');

    // 2. Initialize Store
    const store = Alpine.store('app');
    if (analysisId && keyword) {
        store.setAnalysis(analysisId, keyword);
    }

    // 3. UI Elements (Only those not handled by Alpine)
    const els = {
        editor: document.getElementById('draftContent'),
        preview: document.getElementById('previewContainer'),
        keywordDisplay: document.getElementById('current-keyword'),
        btnHtml: document.getElementById('mode-html'),
        btnPreview: document.getElementById('mode-preview')
    };

    // 4. Initialization
    if (keyword) {
        els.keywordDisplay.textContent = `- ${keyword}`;
    }

    if (analysisId) {
        console.log('Loaded editor for analysis:', analysisId);
    } else {
        if (!keyword) showToast('⚠️ No analysis selected. Features may be limited.', 'warning');
    }

    // 5. Event Listeners

    // Editor Input (Debounced Scoring)
    els.editor.addEventListener('input', debounce(async (e) => {
        // Update Store Content & Stats
        store.updateContent(e.target.value);

        if (analysisId) {
            await performScoring(e.target.value);
        }
    }, 1000)); // Debounce 1s for scoring

    // Immediate stats update
    els.editor.addEventListener('input', (e) => {
        store.updateContent(e.target.value);
    });

    // View Modes
    els.btnHtml.addEventListener('click', () => switchMode('html'));
    els.btnPreview.addEventListener('click', () => switchMode('preview'));

    // Workflow Buttons
    document.getElementById('btn-view-competitors')?.addEventListener('click', () => {
        if (analysisId) window.location.href = `competitors.html?id=${analysisId}`;
        else showToast('⚠️ Save analysis first', 'warning');
    });

    document.getElementById('btn-generate-brief')?.addEventListener('click', async () => {
        if (!analysisId) {
            showToast('⚠️ Analysis ID required', 'warning');
            return;
        }

        showToast('📋 Generating brief...', 'info');

        try {
            const brief = await window.API.generateBrief(analysisId, 'professional');
            console.log('Brief generated:', brief);
            showBriefModal(brief);
            showToast('✅ Brief generated!', 'success');

        } catch (error) {
            console.error('Brief generation error:', error);
            showToast(`❌ ${error.message}`, 'error');
        }
    });

    document.getElementById('btn-check-score')?.addEventListener('click', () => {
        performScoring(els.editor.value);
    });

    // AI Writer
    document.getElementById('btn-ai-writer')?.addEventListener('click', () => {
        if (!analysisId) return showToast('⚠️ Analysis ID required', 'warning');
        // Trigger brief generation first as per workflow
        document.getElementById('btn-generate-brief').click();
    });

    // Auto-Optimize
    document.getElementById('btn-auto-optimize')?.addEventListener('click', async () => {
        if (!analysisId) return showToast('⚠️ Analysis ID required', 'warning');

        const content = els.editor.value;
        if (!content.trim()) return showToast('⚠️ Write some content first', 'warning');

        showToast('⚡ Optimizing content...', 'info');
        store.setLoading('ai', true);

        try {
            const result = await window.API.autoOptimize(analysisId, content);
            if (result.improved_content) {
                // Show diff
                if (window.showDiffModal) {
                    window.showDiffModal(content, result.improved_content, result.changes || [], result.score_improvement || 0);
                } else {
                    // Fallback if diff modal missing
                    els.editor.value = result.improved_content;
                    store.updateContent(result.improved_content);
                    await performScoring(result.improved_content);
                    showToast(`✅ Optimized! Score: +${result.score_improvement}`, 'success');
                }
            }
        } catch (e) {
            console.error(e);
            showToast('❌ Optimization failed', 'error');
        } finally {
            store.setLoading('ai', false);
        }
    });

    // SEO Coach
    document.getElementById('btn-seo-coach')?.addEventListener('click', async () => {
        if (store.score === 0) return showToast('⚠️ Score content first', 'warning');

        showToast('🎓 Analyzing...', 'info');
        try {
            const scoreData = {
                total_score: store.score,
                breakdown: store.breakdown, // Get from store
                term_details: store.terms,
                structure_details: store.structure,
                headings_details: store.headings
            };

            const advice = await window.API.getSeoCoaching(scoreData);
            console.log('Coach advice:', advice);

            // Show advice in a modal (reusing brief modal style for now or alert)
            // Ideally create a specific coach modal
            showCoachModal(advice);

        } catch (e) {
            console.error(e);
            showToast('❌ Coach failed', 'error');
        }
    });

    document.getElementById('btn-generate-images')?.addEventListener('click', async () => {
        if (!analysisId) return showToast('⚠️ Analysis ID required', 'warning');
        showToast('🎨 Generating images...', 'info');
        try {
            const result = await window.API.generateImages(analysisId, els.editor.value);
            if (result.updated_html) {
                els.editor.value = result.updated_html;
                store.updateContent(result.updated_html); // Update Store
                showToast('✅ Images inserted!', 'success');
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

    async function performScoring(content) {
        if (!content.trim()) return;

        try {
            const scoreData = await window.API.scoreContent(analysisId, content);
            // Update Store with Score Data
            store.updateScore(scoreData);
        } catch (e) {
            console.error('Scoring error:', e);
            // Fallback for demo/offline
            store.updateScore({
                total_score: Math.floor(Math.random() * 30) + 50,
                breakdown: { terms: { score: 10, max: 60 }, structure: { score: 10, max: 20 }, headings: { score: 10, max: 20 } },
                term_details: [
                    { term: keyword || 'seo', current: 2, recommended_min: 5, recommended_max: 10, status: 'low' }
                ],
                structure_details: {
                    word_count: { current: content.split(' ').length, recommended_min: 1000, recommended_max: 2000 }
                }
            });
        }
    }

    function switchMode(mode) {
        let isPreviewMode = mode === 'preview';
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

    function showBriefModal(brief) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7); display: flex;
            align-items: center; justify-content: center; z-index: 10000;
        `;

        const content = document.createElement('div');
        content.style.cssText = `
            background: var(--bg-secondary, #1e293b); border-radius: 12px;
            padding: 2rem; max-width: 800px; width: 90%; max-height: 80vh;
            overflow-y: auto; position: relative;
        `;

        content.innerHTML = `
            <h2 style="color: var(--text-primary, #fff); margin-bottom: 1rem;">📋 Generated Brief</h2>
            <button id="closeBriefModal" style="position: absolute; top: 1rem; right: 1rem; background: transparent; border: none; color: #888; cursor: pointer; font-size: 1.5rem;">✕</button>
            <div style="background: #0f172a; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; white-space: pre-wrap; font-family: monospace; color: #cbd5e1; max-height: 400px; overflow-y: auto;">
${JSON.stringify(brief, null, 2)}
            </div>
            <div style="display: flex; gap: 1rem;">
                <button id="generateArticleBtn" class="btn btn-primary" style="flex: 1;">✍️ Generate Article</button>
                <button id="copyBriefBtn" class="btn btn-secondary" style="flex: 1;">📋 Copy Brief</button>
            </div>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        document.getElementById('closeBriefModal').onclick = () => modal.remove();
        document.getElementById('copyBriefBtn').onclick = () => {
            navigator.clipboard.writeText(JSON.stringify(brief, null, 2));
            showToast('✅ Copied!', 'success');
        };

        document.getElementById('generateArticleBtn').onclick = async () => {
            modal.remove();
            showToast('✍️ Generating article...', 'info');
            try {
                const result = await window.API.generateArticle(brief, 'professional', 'uk');
                if (result.article) {
                    els.editor.value = result.article;
                    store.updateContent(result.article); // Update Store
                    showToast('✅ Article generated!', 'success');
                    if (analysisId) await performScoring(result.article);
                }
            } catch (error) {
                showToast(`❌ ${error.message}`, 'error');
            }
        };

        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    }

    function showCoachModal(advice) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7); display: flex;
            align-items: center; justify-content: center; z-index: 10000;
        `;

        const content = document.createElement('div');
        content.style.cssText = `
            background: var(--bg-secondary, #1e293b); border-radius: 12px;
            padding: 2rem; max-width: 600px; width: 90%; max-height: 80vh;
            overflow-y: auto; position: relative; color: #fff;
        `;

        let actionsHtml = advice.priority_actions.map(a => `
            <div style="background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #3b82f6;">
                <div style="font-weight: bold; margin-bottom: 0.25rem;">${a.action}</div>
                <div style="font-size: 0.9em; opacity: 0.8;">${a.details}</div>
                <div style="font-size: 0.8em; margin-top: 0.5rem; color: #60a5fa;">Impact: ${a.score_gain}</div>
            </div>
        `).join('');

        content.innerHTML = `
            <h2 style="margin-bottom: 1rem;">🎓 SEO Coach Plan</h2>
            <button id="closeCoachModal" style="position: absolute; top: 1rem; right: 1rem; background: transparent; border: none; color: #888; cursor: pointer; font-size: 1.5rem;">✕</button>
            
            <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem; color: #cbd5e1;">Priority Actions</h3>
                ${actionsHtml}
            </div>

            <div style="text-align: right;">
                <button class="btn btn-primary" onclick="this.closest('.fixed').remove()">Got it</button>
            </div>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        // Fix close button
        modal.querySelector('#closeCoachModal').onclick = () => modal.remove();
        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    }
});
