// Projects Management Logic
document.addEventListener('DOMContentLoaded', async () => {
    const modal = document.getElementById('project-modal');
    const form = document.getElementById('project-form');
    const projectsList = document.getElementById('projects-list');
    const btnNew = document.getElementById('btn-new-project');
    const btnCancel = document.getElementById('btn-cancel');

    // Load projects
    loadProjects();

    // Event listeners
    btnNew.addEventListener('click', () => {
        modal.style.display = 'flex';
    });

    btnCancel.addEventListener('click', () => {
        modal.style.display = 'none';
        form.reset();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            form.reset();
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const projectData = {
            name: document.getElementById('project-name').value,
            description: document.getElementById('project-description').value || null,
            target_audience: document.getElementById('project-audience').value || null,
            tone_of_voice: document.getElementById('project-tone').value || null
        };

        try {
            const response = await fetch('http://127.0.0.1:8000/api/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(projectData)
            });

            if (response.ok) {
                showToast('✅ Проект створено!', 'success');
                modal.style.display = 'none';
                form.reset();
                loadProjects();
            } else {
                showToast('❌ Помилка створення проекту', 'error');
            }
        } catch (error) {
            console.error(error);
            showToast('❌ Помилка з'єднання', 'error');
        }
    });

    async function loadProjects() {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/projects');
            const projects = await response.json();

            if (projects.length === 0) {
                projectsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">Немає проектів. Створіть перший!</p>';
                return;
            }

            projectsList.innerHTML = projects.map(p => `
                <div class="project-card">
                    <div class="project-header">
                        <h3>${p.name}</h3>
                        <button class="btn-icon" onclick="deleteProject('${p.id}')" title="Видалити">🗑️</button>
                    </div>
                    ${p.description ? `<p class="project-description">${p.description}</p>` : ''}
                    <div class="project-meta">
                        ${p.target_audience ? `<span>👥 ${p.target_audience}</span>` : ''}
                        ${p.tone_of_voice ? `<span>💬 ${p.tone_of_voice}</span>` : ''}
                    </div>
                    <div class="project-actions">
                        <button class="btn btn-sm btn-primary" onclick="createAnalysisForProject('${p.id}', '${p.name}')">
                            📊 Новий аналіз
                        </button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error(error);
            projectsList.innerHTML = '<p style="color: red;">Помилка завантаження проектів</p>';
        }
    }

    // Global functions
    window.deleteProject = async (id) => {
        if (!confirm('Видалити проект? Всі пов\'язані аналізи залишаться.')) return;

        try {
            await fetch(`http://127.0.0.1:8000/api/projects/${id}`, { method: 'DELETE' });
            showToast('✅ Проект видалено', 'success');
            loadProjects();
        } catch (error) {
            showToast('❌ Помилка видалення', 'error');
        }
    };

    window.createAnalysisForProject = (projectId, projectName) => {
        localStorage.setItem('selected_project_id', projectId);
        localStorage.setItem('selected_project_name', projectName);
        window.location.href = 'index.html';
    };

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed; bottom: 20px; right: 20px; z-index: 10000;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white; padding: 1rem 1.5rem; border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
});
