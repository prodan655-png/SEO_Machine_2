# 🚀 SEO Machine 2.0 - Exhaustive Project Documentation

**Date:** 25.11.2024
**Version:** 2.0 (Production Ready Candidate)
**Status:** Feature Complete (82%), In Testing Phase

---

## 📋 Project Overview
**SEO Machine** is a self-hosted, AI-powered content optimization platform inspired by SurferSEO. It helps users write SEO-optimized articles by providing real-time scoring, keyword guidelines, and AI writing assistance.

### 🛠 Tech Stack
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (SQLite), BeautifulSoup4, spaCy (NLP).
- **Frontend:** Vanilla JavaScript (ES6+), HTML5, CSS3 (Variables, Flexbox/Grid). **No frameworks**.
- **AI:** Google Gemini (via `google-generativeai`) for text and image prompting.

---

## � Complete File Inventory (Recursive)

### 1. Root Directory (`/`)
| File | Description |
|------|-------------|
| `README.md` | Main project documentation and quick start guide. |
| `TASKS.md` | Detailed task tracking and progress checklist. |
| `PROGRESS.md` | High-level progress summary and phase tracking. |
| `CHANGES.md` | Changelog of modifications. |
| `BUGS_FIXED.md` | Record of resolved issues. |
| `BUG_REPORT.md` | Template for reporting bugs. |
| `FINAL_TESTING_REPORT.md` | Results of final testing phase. |
| `SESSION_SUMMARY.md` | Summary of the last development session. |
| `WORK_SUMMARY.md` | Comprehensive work log. |
| `TEST_RESULTS.md` | Log of test execution results. |
| `GIT_COMMIT_COMMANDS.txt` | Helper file with git commands. |
| `.gitignore` | Git exclusion rules. |
| `.env.development` | Environment variables for development (mocks enabled). |
| `.env.production` | Environment variables template for production. |
| `.env.example` | Example environment configuration. |
| `start_dev.ps1` | **Startup Script**. PowerShell script to launch backend and frontend. |
| `start_dev.sh` | Bash startup script for Linux/Mac. |
| `setup.sh` | Setup script for dependencies. |
| `fix_scripts.ps1` | Utility script for fixes. |
| `remove_duplicates.ps1` | Utility script to clean up duplicates. |
| `check_env.py` | Script to verify environment setup. |
| `check_analysis.py` | Script to debug analysis logic. |
| `reproduce_issue.py` | Script to reproduce specific bugs. |

### 2. Backend Core (`/backend`)
| File | Description |
|------|-------------|
| `main.py` | **Entry Point**. FastAPI app, API endpoints, CORS, static file serving. |
| `config.py` | **Config Loader**. Pydantic models for configuration validation. |
| `config.yaml` | **Rules**. Scoring weights, thresholds, feature flags. |
| `database.py` | **DB**. SQLAlchemy engine, session handling. |
| `models.py` | **Schema**. DB models: `Analysis`, `Competitor`, `Term`, `Guideline`. |
| `logger.py` | **Logging**. Custom logging configuration. |
| `requirements.txt` | Python dependencies list. |
| `dev_seo_analyzer.db` | SQLite database file (Development). |
| `debug_extractor.py` | Debug script for content extraction. |
| `debug_iteration.py` | Debug script for iteration logic. |
| `debug_serp.py` | Debug script for SERP fetching. |
| `test_lxml.py` | Test script for lxml library. |

### 3. Backend Modules (`/backend/modules`)
| File | Description |
|------|-------------|
| `content_scorer.py` | **Core Logic**. Calculates SEO score (0-100). |
| `content_extractor.py` | **Scraper**. Fetches and cleans content from URLs. |
| `semantic_analyzer.py` | **NLP**. Term extraction, TF-IDF calculation. |
| `guidelines_generator.py` | **Math**. Calculates term frequency ranges. |
| `serp_fetcher.py` | **Search**. Google Search API integration (or mock). |
| `sitemap_parser.py` | **Utility**. Parses XML sitemaps. |
| `__init__.py` | Package marker. |

### 4. AI Modules (`/backend/modules/ai`)
| File | Description |
|------|-------------|
| `coach.py` | **SEO Coach**. Generates improvement advice and Diff changes. |
| `image_generator.py` | **Image Gen**. Prompts for images based on article structure. |
| `content_writer.py` | **Writer**. Generates article content. |
| `brief_generator.py` | **Planner**. Creates content briefs/outlines. |
| `content_iterator.py` | **Refiner**. Iteratively improves content. |
| `score_validator.py` | **Quality**. Validates scores against thresholds. |
| `term_extractor.py` | **NLP Helper**. Specialized term extraction. |
| `ai_client.py` | **API Wrapper**. Google Gemini client. |
| `__init__.py` | Package marker. |

### 5. Mocks (`/backend/modules/mocks`)
| File | Description |
|------|-------------|
| `ai_mock.py` | Mock responses for AI services. |
| `serp_mock.py` | Mock results for Google Search. |

### 6. Stop Words (`/backend/stop_words`)
| File | Description |
|------|-------------|
| `uk.txt` | Ukrainian stop words list. |
| `en.txt` | English stop words list. |

### 7. Tests (`/backend/tests`)
| File | Description |
|------|-------------|
| `test_api.py` | Integration tests for API endpoints. |
| `test_content_scorer.py` | Unit tests for scoring logic. |
| `test_content_extractor.py` | Unit tests for scraper. |
| `test_semantic_analyzer.py` | Unit tests for NLP. |
| `test_guidelines_generator.py` | Unit tests for guidelines. |
| `__init__.py` | Package marker. |

### 8. Frontend Core (`/frontend`)
| File | Description |
|------|-------------|
| `index.html` | **Dashboard**. Main entry page. |
| `editor.html` | **Editor**. The main working interface. |
| `competitors.html` | **Competitors**. View competitor analysis data. |
| `scoring-surfer.html` | Legacy scoring view. |
| `surfer-ui.html` | Legacy UI prototype. |
| `surfer-demo.html` | Demo page for Surfer layout. |
| `toggle-inline.html` | Component test file. |
| `layout-redesign.css` | **Main CSS**. Current production styles. |
| `styles.css` | Legacy CSS. |
| `app.js` | Legacy main script. |
| `surfer-app.js` | Legacy app script. |
| `ui-mode-toggle.js` | Dark/Light mode toggle logic. |

### 9. Frontend Logic (`/frontend/js`)
| File | Description |
|------|-------------|
| `surfer-integration.js` | **Layout**. Manages the 3-column UI. |
| `keyword-highlighting.js` | **Visuals**. Real-time term highlighting. |
| `diff-tracking.js` | **Diff**. Changes review modal. |
| `editor.js` | **Editor**. TinyMCE/ContentEditable logic. |
| `dashboard.js` | **Home**. Dashboard logic. |
| `competitors.js` | **Data**. Competitor data visualization. |
| `api.js` | **Network**. API client wrapper. |

### 10. Frontend Components (`/frontend/components`)
| File | Description |
|------|-------------|
| `header.js` | Reusable header component. |

### 11. Documentation (`/docs`)
| File | Description |
|------|-------------|
| `DEPLOYMENT.md` | Deployment instructions. |
| `HOW_TO_RUN.md` | User guide for running the app. |
| `TESTING_GUIDE.md` | Guide for QA/Testing. |
| `UI_GUIDE.md` | UI/UX design system guide. |
| `decisions.md` | Architectural Decision Records (ADR). |
| `phase6_ai_integration.md` | Spec for AI features. |
| `tasks_backlog.md` | Future ideas and backlog. |
| `walkthrough_phase2.md` | Walkthrough of Phase 2 features. |

---

## 🧩 Key Workflows

### 1. Analysis Flow
`User Input Keyword` -> `backend/main.py` -> `serp_fetcher.py` (Get Top 10) -> `content_extractor.py` (Scrape) -> `semantic_analyzer.py` (NLP) -> `guidelines_generator.py` (Calc Ranges) -> `DB Save`.

### 2. Scoring Flow
`Editor Change` -> `frontend/js/editor.js` (Debounce) -> `API /score` -> `content_scorer.py` -> `JSON Response` -> `frontend/js/surfer-integration.js` (Update UI).

### 3. AI Coaching & Diff
`User Click "Auto-Optimize"` -> `coach.py` -> `Gemini API` -> `JSON with "changes"` -> `frontend/js/diff-tracking.js` (Show Modal) -> `User Accept` -> `Update Editor`.

---

**Instruction for ChatGPT:**
This file is the **absolute source of truth** for the project structure. Use it to understand where specific logic resides.
