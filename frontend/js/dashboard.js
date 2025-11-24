// Dashboard Logic
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('createAnalysisForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const historyList = document.querySelector('.history-list');

    // Load History on Init
    loadHistory();

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // UI Loading State
            submitBtn.disabled = true;
            btnText.classList.add('hidden');
            btnLoader.classList.remove('hidden');

            const formData = new FormData(form);
            const keyword = formData.get('keyword');
            const language = formData.get('language');
            const location = formData.get('location');

            try {
                console.log('Starting analysis for:', keyword);

                // Use shared API
                const result = await window.API.createAnalysis(keyword, language, location);

                console.log('Analysis created:', result);

                // Save to History
                saveToHistory({
                    id: result.analysis_id,
                    keyword: keyword,
                    date: new Date().toISOString(),
                    status: 'processing'
                });

                // Redirect to Competitors (as requested by user)
                // They want to see competitors first
                window.location.href = `competitors.html?id=${result.analysis_id}`;

            } catch (error) {
                console.error('Analysis failed:', error);
                alert('Failed to start analysis: ' + error.message);

                // Reset UI
                submitBtn.disabled = false;
                btnText.classList.remove('hidden');
                btnLoader.classList.add('hidden');
            }
        });
    }

    function saveToHistory(item) {
        let history = JSON.parse(localStorage.getItem('seo_history') || '[]');
        // Add to beginning
        history.unshift(item);
        // Limit to 10
        history = history.slice(0, 10);
        localStorage.setItem('seo_history', JSON.stringify(history));
    }

    function loadHistory() {
        if (!historyList) return;

        const history = JSON.parse(localStorage.getItem('seo_history') || '[]');

        if (history.length === 0) {
            historyList.innerHTML = '<p style="color: var(--text-secondary); font-style: italic;">No recent history found.</p>';
            return;
        }

        historyList.innerHTML = history.map(item => `
            <div class="history-item" style="padding: 1rem; border-bottom: 1px solid var(--border); display: flex; flex-direction: column; gap: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-weight: 600; color: var(--text-primary); word-break: break-word;">${escapeHtml(item.keyword)}</div>
                        <div style="font-size: 0.85em; color: var(--text-secondary);">${new Date(item.date).toLocaleString()}</div>
                    </div>
                    <span class="status-badge ${item.status || 'processing'}" style="font-size: 0.7em; padding: 2px 6px; border-radius: 4px; background: var(--bg-secondary);">${item.status || 'processing'}</span>
                </div>
                <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                    <a href="competitors.html?id=${item.id}" class="btn btn-sm btn-secondary" style="flex: 1; text-align: center;">Competitors</a>
                    <a href="editor.html?id=${item.id}&keyword=${encodeURIComponent(item.keyword)}" class="btn btn-sm btn-primary" style="flex: 1; text-align: center;">Editor</a>
                </div>
            </div>
        `).join('');
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
