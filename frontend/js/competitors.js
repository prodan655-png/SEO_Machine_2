// Competitors Logic
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const analysisId = urlParams.get('id');

    const els = {
        compBody: document.getElementById('competitorsBody'),
        termsBody: document.getElementById('termsBody'),
        keywordDisplay: document.getElementById('comp-keyword'),
        backBtn: document.getElementById('back-to-editor'),
        briefBtn: document.getElementById('btn-generate-brief')
    };

    if (analysisId) {
        // Fix Back Button immediately
        // We need to fetch analysis to get the keyword for the link if possible, 
        // but for now just link to ID. Editor will handle missing keyword via API fetch if needed.
        els.backBtn.href = `editor.html?id=${analysisId}`;

        // Show brief button and set up handler
        els.briefBtn.style.display = 'block';
        els.briefBtn.addEventListener('click', () => {
            // Save analysis ID to localStorage for easy access
            localStorage.setItem('current_analysis_id', analysisId);

            // Show toast notification
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #10b981;
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                z-index: 9999;
                font-weight: 500;
            `;
            toast.textContent = 'Analysis ID saved! Now you can use AI Writer features.';
            document.body.appendChild(toast);

            setTimeout(() => toast.remove(), 3000);

            // Redirect to main page where all features are available
            // User can navigate to AI Writer or other features from there
            setTimeout(() => {
                window.location.href = `index.html`;
            }, 1000);
        });

        // Start polling/loading
        startPolling(analysisId);
    } else {
        showError('No analysis ID provided.');
    }

    async function startPolling(id) {
        let attempts = 0;
        const maxAttempts = 30; // 30 * 2s = 60s timeout

        const poll = async () => {
            try {
                els.compBody.innerHTML = '<tr><td colspan="5" style="padding: 2rem; text-align: center;">Loading analysis data... <span class="spinner"></span></td></tr>';

                const data = await window.API.getAnalysis(id);
                console.log('Analysis Status:', data.status);

                if (data.status === 'completed') {
                    renderData(data);
                } else if (data.status === 'failed') {
                    showError(`Analysis failed: ${data.error_message || 'Unknown error'}`);
                } else {
                    // Processing
                    if (attempts < maxAttempts) {
                        attempts++;
                        els.compBody.innerHTML = `<tr><td colspan="5" style="padding: 2rem; text-align: center;">Processing... (Attempt ${attempts}/${maxAttempts}) <span class="spinner"></span></td></tr>`;
                        setTimeout(poll, 2000);
                    } else {
                        showError('Analysis timed out. Please try again later.');
                    }
                }
            } catch (e) {
                console.error('Polling error:', e);
                showError('Failed to connect to server.');
            }
        };

        poll();
    }

    function renderData(data) {
        // Update Header
        els.keywordDisplay.textContent = `- ${data.keyword}`;

        // Update Back Button with keyword
        els.backBtn.href = `editor.html?id=${data.id}&keyword=${encodeURIComponent(data.keyword)}`;

        // Render Competitors
        if (data.competitors && data.competitors.length > 0) {
            els.compBody.innerHTML = data.competitors.map(c => `
                <tr style="border-bottom: 1px solid var(--border);">
                    <td style="padding: 1rem;">${c.position}</td>
                    <td style="padding: 1rem;">
                        <a href="${c.url}" target="_blank" style="color: var(--primary); text-decoration: none; display: block; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            ${c.url}
                        </a>
                    </td>
                    <td style="padding: 1rem;">${c.title || 'No Title'}</td>
                    <td style="padding: 1rem;">${c.word_count}</td>
                    <td style="padding: 1rem;">
                        <span style="background: ${c.status === 'valid' ? '#10b98120' : '#ef444420'}; color: ${c.status === 'valid' ? '#10b981' : '#ef4444'}; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: bold; font-size: 0.85em;">
                            ${c.status}
                        </span>
                    </td>
                </tr>
            `).join('');
        } else {
            els.compBody.innerHTML = '<tr><td colspan="5" style="padding: 2rem; text-align: center;">No competitors found.</td></tr>';
        }

        // Render Terms
        if (data.terms && data.terms.length > 0) {
            els.termsBody.innerHTML = data.terms.slice(0, 20).map(t => `
                <tr style="border-bottom: 1px solid var(--border);">
                    <td style="padding: 1rem; font-weight: 500;">${t.term}</td>
                    <td style="padding: 1rem;">${t.min_recommended}</td>
                    <td style="padding: 1rem;">${t.max_recommended}</td>
                    <td style="padding: 1rem;">${t.avg_usage.toFixed(1)}</td>
                </tr>
            `).join('');
        } else {
            els.termsBody.innerHTML = '<tr><td colspan="4" style="padding: 2rem; text-align: center;">No keywords extracted.</td></tr>';
        }
    }

    function showError(msg) {
        els.compBody.innerHTML = `<tr><td colspan="5" style="padding: 2rem; text-align: center; color: var(--error);">${msg}</td></tr>`;
        els.termsBody.innerHTML = `<tr><td colspan="4" style="padding: 2rem; text-align: center; color: var(--text-secondary);">Data unavailable</td></tr>`;
    }
});
