// HH Parser Service - JavaScript

// Global configuration
const CONFIG = {
    API_BASE_URL: window.location.origin + '/api/v1'
};

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatSalary(salaryFrom, salaryTo, currency) {
    if (!salaryFrom && !salaryTo) {
        return 'Не указана';
    }
    const from = salaryFrom ? salaryFrom.toLocaleString('ru-RU') : '?';
    const to = salaryTo ? salaryTo.toLocaleString('ru-RU') : '?';
    const curr = currency || '';
    return `${from} - ${to} ${curr}`.trim();
}

function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// API functions
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showMessage(`Ошибка загрузки данных: ${error.message}`, 'danger');
        throw error;
    }
}

// Export functions for use in templates
window.hhParser = {
    formatDate,
    formatSalary,
    showMessage,
    fetchAPI
};

// Initialize tooltips and popovers if Bootstrap is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    console.log('HH Parser Service UI loaded');
});
