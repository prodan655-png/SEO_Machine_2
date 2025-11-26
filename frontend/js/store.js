// SEO Machine - Central State Management
// Uses Alpine.js for reactivity

document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        // State
        currentAnalysisId: null,
        keyword: '',
        language: 'uk',

        // Content
        content: '',
        wordCount: 0,
        charCount: 0,

        // Scoring
        score: 0,
        breakdown: {}, // Added breakdown
        terms: [],
        structure: {},
        headings: {},

        // UI State
        loading: {
            analysis: false,
            scoring: false,
            ai: false
        },
        activeTab: 'write',

        // Error handling
        error: {
            message: '',
            code: '',
            visible: false
        },

        // Actions
        init() {
            console.log('🚀 AppState Initialized');
        },

        setAnalysis(data) {
            this.currentAnalysisId = data.id;
            this.keyword = data.keyword;
            this.language = data.language;
        },

        updateContent(text) {
            this.content = text;
            this.wordCount = text.split(/\s+/).filter(w => w.length > 0).length;
            this.charCount = text.length;
        },

        updateScore(scoreData) {
            this.score = scoreData.total_score || 0;
            this.breakdown = scoreData.breakdown || {}; // Save breakdown
            this.terms = scoreData.term_details || [];
            this.structure = scoreData.structure_details || {};
            this.headings = scoreData.headings_details || {};
        },

        setLoading(key, value) {
            this.loading[key] = value;
        },

        setTab(tab) {
            this.activeTab = tab;
        },

        // Error handling methods
        showError(message, code = 'ERROR') {
            this.error = {
                message,
                code,
                visible: true
            };
            // Auto-hide after 5 seconds
            setTimeout(() => this.clearError(), 5000);
        },

        clearError() {
            this.error = {
                message: '',
                code: '',
                visible: false
            };
        },

        // API error handler
        handleApiError(error) {
            if (error.error) {
                // Standardized error from backend
                this.showError(error.error, error.error_code || 'API_ERROR');
            } else if (error.message) {
                // JavaScript error
                this.showError(error.message, 'CLIENT_ERROR');
            } else {
                // Unknown error
                this.showError('An unexpected error occurred', 'UNKNOWN_ERROR');
            }
        }
    });
});
