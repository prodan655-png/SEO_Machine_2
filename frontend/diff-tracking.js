// Live Diff Tracking Module
// Shows side-by-side comparison of AI changes with accept/reject options

(function () {
    'use strict';

    let originalContent = '';
    let revisedContent = '';
    let currentChanges = [];

    // Create diff modal HTML
    const diffModalHTML = `
        <div class="diff-modal hidden" id="diffModal">
            <div class="diff-overlay" onclick="closeDiffModal()"></div>
            <div class="diff-content">
                <div class="diff-header">
                    <h3>🔍 Зміни від SEO Coach</h3>
                    <div class="diff-actions-top">
                        <span id="diffScoreGain" class="score-gain">+0 балів</span>
                        <button class="close-btn" onclick="closeDiffModal()">✕</button>
                    </div>
                </div>

                <!-- Side by side comparison -->
                <div class="diff-comparison">
                    <div class="diff-column">
                        <h4>Оригінал</h4>
                        <div id="diffOld" class="diff-view"></div>
                    </div>
                    <div class="diff-separator"></div>
                    <div class="diff-column">
                        <h4>Покращено</h4>
                        <div id="diffNew" class="diff-view"></div>
                    </div>
                </div>

                <!-- Changes list -->
                <div class="changes-section">
                    <h4>Деталі змін:</h4>
                    <div id="changesList" class="changes-list">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <!-- Actions -->
                <div class="diff-actions">
                    <button class="btn btn-secondary" onclick="rejectAllChanges()">
                        Відхилити все
                    </button>
                    <button class="btn btn-primary" onclick="acceptAllChanges()">
                        ✅ Прийняти все
                    </button>
                </div>
            </div>
        </div>
    `;

    // Add modal to page
    document.addEventListener('DOMContentLoaded', () => {
        document.body.insertAdjacentHTML('beforeend', diffModalHTML);
    });

    // Show diff modal
    window.showDiffModal = function (oldContent, newContent, changes, scoreGain) {
        originalContent = oldContent;
        revisedContent = newContent;
        currentChanges = changes || [];

        const modal = document.getElementById('diffModal');
        const scoreEl = document.getElementById('diffScoreGain');

        if (scoreEl) {
            scoreEl.textContent = `+${scoreGain || 0} балів`;
        }

        // Render diff
        renderDiff(oldContent, newContent);

        // Render changes list
        renderChangesList(currentChanges);

        // Show modal
        modal.classList.remove('hidden');
        setTimeout(() => modal.classList.add('show'), 10);
    };

    // Close diff modal
    window.closeDiffModal = function () {
        const modal = document.getElementById('diffModal');
        modal.classList.remove('show');
        setTimeout(() => modal.classList.add('hidden'), 300);
    };

    // Render diff using simple line-by-line comparison
    function renderDiff(oldText, newText) {
        const diffOld = document.getElementById('diffOld');
        const diffNew = document.getElementById('diffNew');

        if (!diffOld || !diffNew) return;

        // Simple diff: split by lines and compare
        const oldLines = oldText.split('\n');
        const newLines = newText.split('\n');

        let oldHTML = '';
        let newHTML = '';

        const maxLines = Math.max(oldLines.length, newLines.length);

        for (let i = 0; i < maxLines; i++) {
            const oldLine = oldLines[i] || '';
            const newLine = newLines[i] || '';

            if (oldLine === newLine) {
                // Unchanged
                oldHTML += `<div class="diff-line">${escapeHtml(oldLine)}</div>`;
                newHTML += `<div class="diff-line">${escapeHtml(newLine)}</div>`;
            } else {
                // Changed
                if (oldLine) {
                    oldHTML += `<div class="diff-line removed">${escapeHtml(oldLine)}</div>`;
                }
                if (newLine) {
                    newHTML += `<div class="diff-line added">${escapeHtml(newLine)}</div>`;
                }
            }
        }

        diffOld.innerHTML = oldHTML;
        diffNew.innerHTML = newHTML;
    }

    // Render changes list
    function renderChangesList(changes) {
        const container = document.getElementById('changesList');
        if (!container) return;

        if (!changes || changes.length === 0) {
            container.innerHTML = '<p class="no-changes">Немає детальних змін</p>';
            return;
        }

        const html = changes.map((change, idx) => `
            <div class="change-item" id="change-${idx}">
                <div class="change-header">
                    <input type="checkbox" checked id="changeCheck-${idx}" class="change-checkbox">
                    <strong>${getChangeTypeLabel(change.type)}</strong>
                    ${change.term ? `<span class="change-term">"${change.term}"</span>` : ''}
                </div>
                <div class="change-details">
                    ${change.old_text ? `<div class="change-old"><del>${escapeHtml(change.old_text)}</del></div>` : ''}
                    ${change.new_text ? `<div class="change-new"><ins>${escapeHtml(change.new_text)}</ins></div>` : ''}
                    <p class="change-reason">${change.reason || ''}</p>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    function getChangeTypeLabel(type) {
        const labels = {
            'add_term': '➕ Додано термін',
            'improve_heading': '📝 Покращено заголовок',
            'expand_section': '📄 Розширено секцію',
            'reduce_term': '➖ Зменшено термін'
        };
        return labels[type] || type;
    }

    // Accept all changes
    window.acceptAllChanges = function () {
        const editor = document.getElementById('draftContent');
        if (editor) {
            editor.value = revisedContent;

            // Trigger input event to update score
            editor.dispatchEvent(new Event('input'));

            showToast('✅ Всі зміни прийнято!', 'success');
            closeDiffModal();

            // Re-score after 1 second
            setTimeout(() => {
                if (typeof performScoring === 'function') {
                    performScoring(revisedContent);
                }
            }, 1000);
        }
    };

    // Reject all changes
    window.rejectAllChanges = function () {
        showToast('❌ Зміни відхилено', 'info');
        closeDiffModal();
    };

    // Accept individual change
    window.acceptChange = function (index) {
        const checkbox = document.getElementById(`changeCheck-${index}`);
        if (checkbox) {
            checkbox.checked = true;
        }
        // TODO: Apply only this change
    };

    // Reject individual change
    window.rejectChange = function (index) {
        const checkbox = document.getElementById(`changeCheck-${index}`);
        if (checkbox) {
            checkbox.checked = false;
        }
    };

    // Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Add CSS
    const style = document.createElement('style');
    style.textContent = `
        .diff-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .diff-modal.show {
            opacity: 1;
        }

        .diff-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
        }

        .diff-content {
            position: relative;
            background: var(--bg-secondary);
            border-radius: var(--radius-lg);
            width: 95%;
            max-width: 1400px;
            max-height: 90vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        .diff-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--spacing-md);
            border-bottom: 1px solid var(--border);
            background: var(--bg-card);
        }

        .diff-header h3 {
            margin: 0;
            font-size: 1.25rem;
        }

        .diff-actions-top {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
        }

        .score-gain {
            padding: 0.5rem 1rem;
            background: rgba(16, 185, 129, 0.2);
            color: var(--success);
            border-radius: var(--radius-md);
            font-weight: 600;
        }

        .close-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 50%;
            transition: all 0.2s;
        }

        .close-btn:hover {
            background: rgba(239, 68, 68, 0.2);
            color: var(--error);
        }

        .diff-comparison {
            display: grid;
            grid-template-columns: 1fr 2px 1fr;
            gap: 0;
            flex: 1;
            overflow: hidden;
        }

        .diff-column {
            padding: var(--spacing-md);
            overflow-y: auto;
        }

        .diff-column h4 {
            margin: 0 0 var(--spacing-sm) 0;
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .diff-separator {
            background: var(--border);
        }

        .diff-view {
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
            line-height: 1.6;
        }

        .diff-line {
            padding: 0.25rem 0.5rem;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .diff-line.removed {
            background: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
            text-decoration: line-through;
        }

        .diff-line.added {
            background: rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
        }

        .changes-section {
            padding: var(--spacing-md);
            border-top: 1px solid var(--border);
            max-height: 300px;
            overflow-y: auto;
        }

        .changes-section h4 {
            margin: 0 0 var(--spacing-sm) 0;
            font-size: 1rem;
        }

        .changes-list {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-sm);
        }

        .change-item {
            background: rgba(51, 65, 85, 0.4);
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            border-left: 3px solid var(--accent);
        }

        .change-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            margin-bottom: var(--spacing-xs);
        }

        .change-checkbox {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }

        .change-term {
            color: var(--accent-light);
            font-weight: 600;
        }

        .change-details {
            margin-left: 26px;
            font-size: 0.875rem;
        }

        .change-old {
            margin: 0.5rem 0;
            color: var(--error);
        }

        .change-new {
            margin: 0.5rem 0;
            color: var(--success);
        }

        .change-reason {
            margin: 0.5rem 0 0 0;
            color: var(--text-secondary);
            font-size: 0.8125rem;
        }

        .change-old del,
        .change-new ins {
            text-decoration: none;
            padding: 2px 4px;
            border-radius: 3px;
        }

        .change-old del {
            background: rgba(239, 68, 68, 0.2);
        }

        .change-new ins {
            background: rgba(16, 185, 129, 0.2);
        }

        .no-changes {
            text-align: center;
            color: var(--text-secondary);
            padding: 2rem;
        }

        .diff-actions {
            padding: var(--spacing-md);
            border-top: 1px solid var(--border);
            display: flex;
            gap: var(--spacing-sm);
            justify-content: flex-end;
        }

        @media (max-width: 992px) {
            .diff-comparison {
                grid-template-columns: 1fr;
                grid-template-rows: 1fr 1fr;
            }
            
            .diff-separator {
                display: none;
            }
        }
    `;
    document.head.appendChild(style);

    console.log('📊 Diff tracking module loaded');
})();
