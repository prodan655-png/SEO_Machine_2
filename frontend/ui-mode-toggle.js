// UI Mode Toggle - Switches between Classic and SurferSEO layouts
(function () {
    'use strict';

    // Add toggle button when scoring tab becomes active
    function initToggleButton() {
        const scoringTab = document.getElementById('scoringTab');
        if (!scoringTab || document.getElementById('uiModeToggle')) return;

        // Create toggle button container
        const toggleContainer = document.createElement('div');
        toggleContainer.style.cssText = 'display: flex; justify-content: flex-end; margin-bottom: 1rem;';
        toggleContainer.innerHTML = `
            <button id="uiModeToggle" class="btn btn-secondary" style="display: flex; align-items: center; gap: 0.5rem;">
                <span id="uiModeIcon">🎨</span>
                <span id="uiModeText">Режим SurferSEO</span>
            </button>
        `;

        // Insert at the top of scoring tab
        scoringTab.insertBefore(toggleContainer, scoringTab.firstChild);

        // Attach click handler
        document.getElementById('uiModeToggle').addEventListener('click', toggleUIMode);

        // Load saved preference
        loadUIMode();
    }

    // Toggle between Classic and SurferSEO UI
    window.toggleUIMode = function () {
        const currentMode = localStorage.getItem('uiMode') || 'classic';
        const newMode = currentMode === 'classic' ? 'surfer' : 'classic';

        localStorage.setItem('uiMode', newMode);
        applyUIMode(newMode);
    };

    // Apply UI mode
    function applyUIMode(mode) {
        const scoringTab = document.getElementById('scoringTab');
        const toggleBtn = document.getElementById('uiModeToggle');
        const iconEl = document.getElementById('uiModeIcon');
        const textEl = document.getElementById('uiModeText');
        const classicUI = scoringTab?.querySelector('.scoring-layout');

        if (!scoringTab || !toggleBtn) return;

        if (mode === 'surfer') {
            // Switch to SurferSEO mode
            iconEl.textContent = '📝';
            textEl.textContent = 'Класичний режим';

            // Hide classic UI
            if (classicUI) {
                classicUI.style.display = 'none';
            }

            // Initialize SurferSEO layout if available
            if (typeof window.initSurferLayout === 'function') {
                setTimeout(() => window.initSurferLayout(), 100);
            } else {
                console.warn('initSurferLayout not found. Make sure surfer-integration.js is loaded.');
            }
        } else {
            // Switch to Classic mode
            iconEl.textContent = '🎨';
            textEl.textContent = 'Режим SurferSEO';

            // Show classic UI
            if (classicUI) {
                classicUI.style.display = '';
            }

            // Remove SurferSEO layout if present
            const surferContainer = scoringTab.querySelector('.surfer-layout');
            if (surferContainer && surferContainer !== classicUI) {
                surferContainer.remove();
            }
        }

        console.log(`UI Mode: ${mode}`);
    }

    // Load saved UI mode on page load
    function loadUIMode() {
        const savedMode = localStorage.getItem('uiMode') || 'classic';
        if (savedMode !== 'classic') {
            applyUIMode(savedMode);
        }
    }

    // Initialize when document is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initToggleButton);
    } else {
        initToggleButton();
    }

    // Also try to initialize when switching to scoring tab
    const originalSwitchTab = window.switchTab;
    if (originalSwitchTab) {
        window.switchTab = function (tabName) {
            originalSwitchTab(tabName);
            if (tabName === 'scoring') {
                setTimeout(initToggleButton, 100);
            }
        };
    }

    console.log('🎨 UI Mode Toggle loaded');
})();
