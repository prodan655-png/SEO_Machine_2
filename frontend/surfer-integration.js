// SurferSEO Layout Integration for Scoring Tab
// This file adds the new 3-column layout to the scoring tab

(function () {
    'use strict';

    // HTML template for new scoring layout
    const SURFER_LAYOUT_HTML = `
        <div class="surfer-layout">
            <!-- Workflow Sidebar -->
            <aside class="workflow-sidebar" id="workflowSidebar">
                <h3>WORKFLOW</h3>

                <!-- Get Started -->
                <div class="workflow-step">
                    <div class="workflow-step-header completed" data-step="start">
                        <div class="workflow-step-icon">🎯</div>
                        <div class="workflow-step-title">Get Started</div>
                    </div>
                    <ul class="workflow-actions">
                        <li class="workflow-action">
                            <button class="workflow-action-btn completed" onclick="switchTab('results')">
                                📊 View Competitors
                                <span class="check-icon">✓</span>
                            </button>
                        </li>
                        <li class="workflow-action">
                            <button class="workflow-action-btn completed" onclick="switchTab('ai-writer')">
                                📋 Generate Outline
                                <span class="check-icon">✓</span>
                            </button>
                        </li>
                    </ul>
                </div>

                <!-- Write & Optimize -->
                <div class="workflow-step">
                    <div class="workflow-step-header active" data-step="write">
                        <div class="workflow-step-icon">✍️</div>
                        <div class="workflow-step-title">Write & Optimize</div>
                    </div>
                    <ul class="workflow-actions">
                        <li class="workflow-action">
                            <button class="workflow-action-btn" onclick="switchTab('ai-writer')">
                                🤖 AI Writer
                            </button>
                        </li>
                        <li class="workflow-action">
                            <button class="workflow-action-btn" onclick="triggerAutoOptimize()">
                                ⚡ Auto-Optimize
                            </button>
                        </li>
                        <li class="workflow-action">
                            <button class="workflow-action-btn" onclick="startIterationFromWorkflow()">
                                🔄 Iterate Content
                            </button>
                        </li>
                    </ul>
                </div>

                <!-- Review -->
                <div class="workflow-step">
                    <div class="workflow-step-header" data-step="review">
                        <div class="workflow-step-icon">🔍</div>
                        <div class="workflow-step-title">Review</div>
                    </div>
                    <ul class="workflow-actions">
                        <li class="workflow-action">
                            <button class="workflow-action-btn" onclick="refreshContentScore()">
                                📊 Check Score
                            </button>
                        </li>
                        <li class="workflow-action">
                            <button class="workflow-action-btn" onclick="getSEOCoaching()">
                                🎓 SEO Coach
                            </button>
                        </li>
                    </ul>
                </div>

                <!-- Publish -->
                <div class="workflow-step">
                    <div class="workflow-step-header" data-step="publish">
                        <div class="workflow-step-icon">🚀</div>
                        <div class="workflow-step-title">Publish</div>
                    </div>
                    <ul class="workflow-actions">
                        <li class="workflow-action">
                            <button class="workflow-action-btn" onclick="exportHTML()">
                                📤 Export HTML
                            </button>
                        </li>
                        <li class="workflow-action">
                            <button class="workflow-action-btn" onclick="copyToClipboard()">
                                📋 Copy Code
                            </button>
                        </li>
                    </ul>
                </div>
            </aside>

            <!-- Main Editor Area -->
            <main class="editor-area">
                <div class="editor-header">
                    <h2 class="editor-title">✍️ Content Editor</h2>
                </div>

                <div class="editor-toolbar">
                    <button class="toolbar-btn active" data-mode="html" onclick="switchEditorMode('html')">
                        💻 HTML
                    </button>
                    <button class="toolbar-btn" data-mode="preview" onclick="switchEditorMode('preview')">
                        📄 Preview
                    </button>
                    <button class="toolbar-btn" data-mode="markdown" onclick="switchEditorMode('markdown')">
                        📝 Markdown
                    </button>
                </div>

                <!-- HTML Editor (visible by default) -->
                <div id="htmlEditorContainer" class="editor-container">
                    <textarea id="draftContent" class="content-editor" placeholder="Вставте ваш HTML або текст..."></textarea>
                    <div class="editor-stats">
                        <span>Слів: <strong id="wordCount">0</strong></span>
                        <span>Символів: <strong id="charCount">0</strong></span>
                    </div>
                </div>

                <!-- Preview Container (hidden by default) -->
                <div id="previewContainer" class="editor-container hidden">
                    <div class="rich-editor-container">
                        <div id="content Preview" class="rich-editor-content"></div>
                    </div>
                </div>
            </main>

            <!-- Guidelines Sidebar -->
            <aside class="guidelines-sidebar" id="guidelinesSidebar">
                <div class="guidelines-header">
                    <h3 class="guidelines-title">📋 Guidelines</h3>
                </div>

                <!-- Content Score Widget -->
                <div class="score-widget">
                    <div class="score-circle-small">
                        <svg viewBox="0 0 120 120">
                            <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(30, 41, 59, 0.6)" stroke-width="8"/>
                            <circle cx="60" cy="60" r="54" fill="none" stroke="url(#gradient)" stroke-width="8"
                                    stroke-dasharray="339" stroke-dashoffset="339" stroke-linecap="round" id="scoreCircleSmall"/>
                            <defs>
                                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#60a5fa"/>
                                    <stop offset="100%" style="stop-color:#3b82f6"/>
                                </linearGradient>
                            </defs>
                        </svg>
                        <div class="score-value-small" id="scoreValueSmall">0</div>
                    </div>
                    <span class="score-label-small">CONTENT SCORE</span>
                </div>

                <!-- Auto-Optimize Button -->
                <button class="auto-optimize-btn" onclick="triggerAutoOptimize()">
                    ⚡ Auto-Optimize
                </button>

                <!-- Important Terms -->
                <div class="guidelines-section">
                    <h4 class="guidelines-section-title">
                        <span class="icon">🔑</span>
                        Important Terms
                    </h4>
                    <ul class="terms-list" id="importantTermsList">
                        <li class="term-item">
                            <span class="term-name">No terms yet</span>
                            <span class="term-count">-</span>
                        </li>
                    </ul>
                </div>

                <!-- Content Structure -->
                <div class="guidelines-section">
                    <h4 class="guidelines-section-title">
                        <span class="icon">📊</span>
                        Content Structure
                    </h4>
                    <ul class="metrics-list" id="structureMetricsList">
                        <li class="metric-item">
                            <span class="metric-label">Words</span>
                            <div>
                                <span class="metric-value" id="metricWords">0/0-0</span>
                                <div class="metric-bar">
                                    <div class="metric-bar-fill" id="metricWordsBar" style="width: 0%"></div>
                                </div>
                            </div>
                        </li>
                        <li class="metric-item">
                            <span class="metric-label">Headings</span>
                            <div>
                                <span class="metric-value" id="metricHeadings">0/0-0</span>
                                <div class="metric-bar">
                                    <div class="metric-bar-fill" id="metricHeadingsBar" style="width: 0%"></div>
                                </div>
                            </div>
                        </li>
                        <li class="metric-item">
                            <span class="metric-label">Images</span>
                            <div>
                                <span class="metric-value" id="metricImages">0/0-0</span>
                                <div class="metric-bar">
                                    <div class="metric-bar-fill" id="metricImagesBar" style="width: 0%"></div>
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
            </aside>
        </div>
    `;

    // Initialize new layout when switching to scoring tab
    function initSurferLayout() {
        const scoringTab = document.getElementById('scoringTab');
        if (!scoringTab) return;

        // Replace content with new layout
        scoringTab.innerHTML = SURFER_LAYOUT_HTML;

        // Re-attach event listeners
        const editor = document.getElementById('draftContent');
        if (editor) {
            editor.addEventListener('input', handleEditorInput);
        }

        console.log('✅ SurferSEO layout initialized');
    }

    // Update Guidelines sidebar with real data
    window.updateGuidelinesSidebar = function (analysisData, scoreData) {
        if (!analysisData || !scoreData) return;

        // Update score widget
        const scoreValue = document.getElementById('scoreValueSmall');
        const scoreCircle = document.getElementById('scoreCircleSmall');

        if (scoreValue && scoreCircle) {
            scoreValue.textContent = scoreData.total_score || 0;

            // Update circle (339 = circumference of r=54)
            const offset = 339 - (scoreData.total_score / 100) * 339;
            scoreCircle.style.strokeDashoffset = offset;
        }

        // Update terms list
        if (scoreData.term_details && scoreData.term_details.length > 0) {
            const termsList = document.getElementById('importantTermsList');
            if (termsList) {
                const topTerms = scoreData.term_details.slice(0, 10);
                termsList.innerHTML = topTerms.map(term => {
                    const status = term.status || 'medium';
                    return `
                        <li class="term-item ${status}" onclick="highlightTermInPreview('${term.term}')" style="cursor: pointer;">
                            <span class="term-name">${term.term}</span>
                            <span class="term-count">${term.current}/${term.recommended_min}-${term.recommended_max}</span>
                        </li>
                    `;
                }).join('');
            }
        }

        // Update structure metrics
        if (scoreData.structure_details) {
            const wc = scoreData.structure_details.word_count;
            if (wc) {
                updateMetric('Words', wc.current, wc.recommended_min, wc.recommended_max);
            }
        }

        if (scoreData.headings_details) {
            const hc = scoreData.headings_details;
            updateMetric('Headings', hc.h2_count + hc.h3_count, 6, 10);
        }
    };

    function updateMetric(name, current, min, max) {
        const valueEl = document.getElementById(`metric${name}`);
        const barEl = document.getElementById(`metric${name}Bar`);

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

    // Workflow helper functions
    window.triggerAutoOptimize = function () {
        showToast('Auto-Optimize працює...', 'info');
        // TODO: Implement auto-optimize logic
    };

    window.startIterationFromWorkflow = function () {
        if (typeof startIteration === 'function') {
            startIteration(85, 10);
        }
    };

    window.refreshContentScore = function () {
        const text = document.getElementById('draftContent')?.value;
        if (text && typeof performScoring === 'function') {
            performScoring(text);
        }
    };

    window.exportHTML = function () {
        const content = document.getElementById('draftContent')?.value || '';
        const blob = new Blob([content], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'article.html';
        a.click();
        URL.revokeObjectURL(url);
        showToast('HTML експортовано!', 'success');
    };

    window.copyToClipboard = function () {
        const content = document.getElementById('draftContent')?.value || '';
        navigator.clipboard.writeText(content).then(() => {
            showToast('Скопійовано в буфер обміну!', 'success');
        });
    };

    // Initialize on tab switch to scoring
    const originalSwitchTab = window.switchTab;
    window.switchTab = function (tabName) {
        originalSwitchTab(tabName);

        if (tabName === 'scoring') {
            // Small delay to ensure tab is visible
            setTimeout(initSurferLayout, 100);
        }
    };

    // Also initialize if scoring tab is already active on load
    if (document.readyContent === 'complete') {
        const activeTab = document.querySelector('.tab-pane.active');
        if (activeTab && activeTab.id === 'scoringTab') {
            initSurferLayout();
        }
    }

    console.log('📦 Surfer layout integration loaded');
})();
