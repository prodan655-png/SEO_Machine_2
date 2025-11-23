// Keyword Highlighting Module for Preview Mode
// Highlights important terms in real-time with color-coding

(function () {
    'use strict';

    let highlightingEnabled = false;
    let currentTerms = [];
    let currentTermDetails = [];

    // Editor mode management
    window.switchEditorMode = function (mode) {
        const htmlContainer = document.getElementById('htmlEditorContainer');
        const previewContainer = document.getElementById('previewContainer');
        const toolbarBtns = document.querySelectorAll('.toolbar-btn');

        // Update toolbar buttons
        toolbarBtns.forEach(btn => {
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Show/hide containers
        if (mode === 'html' || mode === 'markdown') {
            htmlContainer?.classList.remove('hidden');
            previewContainer?.classList.add('hidden');
            highlightingEnabled = false;
        } else if (mode === 'preview') {
            htmlContainer?.classList.add('hidden');
            previewContainer?.classList.remove('hidden');
            highlightingEnabled = true;
            updatePreview();
        }
    };

    // Update preview with highlighted content
    function updatePreview() {
        const editor = document.getElementById('draftContent');
        const preview = document.getElementById('contentPreview');

        if (!editor || !preview) return;

        const content = editor.value;
        const highlightedContent = highlightKeywords(content);

        preview.innerHTML = highlightedContent;
    }

    // Highlight keywords in content
    function highlightKeywords(html) {
        if (!currentTermDetails || currentTermDetails.length === 0) {
            return html;
        }

        let result = html;
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        // Process text nodes only (avoid breaking HTML tags)
        processTextNodes(tempDiv);

        return tempDiv.innerHTML;
    }

    function processTextNodes(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent;
            const highlightedText = highlightTextNode(text);

            if (highlightedText !== text) {
                const span = document.createElement('span');
                span.innerHTML = highlightedText;
                node.parentNode.replaceChild(span, node);
            }
        } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'SCRIPT' && node.tagName !== 'STYLE') {
            Array.from(node.childNodes).forEach(child => processTextNodes(child));
        }
    }

    function highlightTextNode(text) {
        let result = text;

        // Sort terms by length (longest first) to avoid partial matches
        const sortedTerms = [...currentTermDetails].sort((a, b) =>
            b.term.length - a.term.length
        );

        sortedTerms.forEach(termDetail => {
            const term = termDetail.term;
            const status = getTermStatus(termDetail);

            // Create case-insensitive regex
            const regex = new RegExp(`\\b(${escapeRegex(term)})\\b`, 'gi');

            result = result.replace(regex, (match) => {
                const tooltip = `${termDetail.current}/${termDetail.recommended_min}-${termDetail.recommended_max} використань`;
                return `<span class="keyword-highlight ${status}" data-term="${term}" title="${tooltip}">${match}</span>`;
            });
        });

        return result;
    }

    function getTermStatus(termDetail) {
        const current = termDetail.current || 0;
        const min = termDetail.recommended_min || 0;
        const max = termDetail.recommended_max || 0;

        if (current >= min && current <= max) {
            return 'good';
        } else if (current >= min * 0.7 || (current <= max && current >= min * 0.5)) {
            return 'medium';
        } else {
            return 'low';
        }
    }

    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Update terms when scoring happens
    window.updateHighlightTerms = function (termDetails) {
        currentTermDetails = termDetails || [];

        if (highlightingEnabled) {
            updatePreview();
        }
    };

    // Auto-update preview when content changes
    let previewUpdateTimeout;
    function schedulePreviewUpdate() {
        clearTimeout(previewUpdateTimeout);
        previewUpdateTimeout = setTimeout(() => {
            if (highlightingEnabled) {
                updatePreview();
            }
        }, 500);
    }

    // Listen to editor changes
    document.addEventListener('DOMContentLoaded', () => {
        const editor = document.getElementById('draftContent');
        if (editor) {
            editor.addEventListener('input', schedulePreviewUpdate);
        }
    });

    // Integrate with existing displayScore function
    const originalDisplayScore = window.displayScore;
    if (originalDisplayScore) {
        window.displayScore = function (scoreData) {
            originalDisplayScore(scoreData);

            // Update highlighted terms
            if (scoreData.term_details) {
                updateHighlightTerms(scoreData.term_details);
            }
        };
    }

    // Click on term in Guidelines to highlight in preview
    window.highlightTermInPreview = function (term) {
        // Switch to preview mode
        switchEditorMode('preview');

        // Wait for preview to render
        setTimeout(() => {
            const preview = document.getElementById('contentPreview');
            if (!preview) return;

            // Find all highlights for this term
            const highlights = preview.querySelectorAll(`.keyword-highlight[data-term="${term}"]`);

            if (highlights.length > 0) {
                // Scroll to first occurrence
                highlights[0].scrollIntoView({ behavior: 'smooth', block: 'center' });

                // Add temporary emphasis
                highlights.forEach(el => {
                    el.style.animation = 'pulse 1s';
                    setTimeout(() => {
                        el.style.animation = '';
                    }, 1000);
                });
            }
        }, 100);
    };

    // Add pulse animation CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); box-shadow: 0 0 10px currentColor; }
        }
        
        .keyword-highlight {
            position: relative;
            cursor: help;
            border-radius: 3px;
            padding: 2px 4px;
            margin: 0 1px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .keyword-highlight:hover {
            transform: translateY(-1px);
        }
        
        .keyword-highlight.good {
            background: rgba(16, 185, 129, 0.25);
            color: var(--success);
            border-bottom: 2px solid var(--success);
        }
        
        .keyword-highlight.medium {
            background: rgba(245, 158, 11, 0.25);
            color: var(--warning);
            border-bottom: 2px solid var(--warning);
        }
        
        .keyword-highlight.low {
            background: rgba(239, 68, 68, 0.25);
            color: var(--error);
            border-bottom: 2px solid var(--error);
        }
        
        .editor-container {
            height: calc(100vh - 300px);
        }
        
        .rich-editor-content {
            padding: 2rem;
            background: rgba(51, 65, 85, 0.3);
            border-radius: var(--radius-md);
            min-height: 100%;
            font-size: 1rem;
            line-height: 1.8;
            color: var(--text-primary);
        }
        
        .rich-editor-content h1 {
            font-size: 2rem;
            margin: 1.5rem 0 1rem;
            color: var(--text-primary);
        }
        
        .rich-editor-content h2 {
            font-size: 1.5rem;
            margin: 1.25rem 0 0.75rem;
            color: var(--text-primary);
        }
        
        .rich-editor-content h3 {
            font-size: 1.25rem;
            margin: 1rem 0 0.5rem;
            color: var(--text-primary);
        }
        
        .rich-editor-content p {
            margin: 0.75rem 0;
        }
        
        .rich-editor-content ul, .rich-editor-content ol {
            margin: 1rem 0;
            padding-left: 2rem;
        }
        
        .rich-editor-content li {
            margin: 0.5rem 0;
        }
    `;
    document.head.appendChild(style);

    console.log('✨ Keyword highlighting module loaded');
})();
