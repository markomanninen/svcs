// Utility Functions
class Utils {
    // DOM helpers
    static $(id) {
        return document.getElementById(id);
    }

    static $$(selector) {
        return document.querySelectorAll(selector);
    }

    static createElement(tag, className = '', innerHTML = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (innerHTML) element.innerHTML = innerHTML;
        return element;
    }

    // Show/hide elements
    static show(elementOrId) {
        const element = typeof elementOrId === 'string' ? this.$(elementOrId) : elementOrId;
        if (element) element.style.display = 'block';
    }

    static hide(elementOrId) {
        const element = typeof elementOrId === 'string' ? this.$(elementOrId) : elementOrId;
        if (element) element.style.display = 'none';
    }

    static toggle(elementOrId) {
        const element = typeof elementOrId === 'string' ? this.$(elementOrId) : elementOrId;
        if (element) {
            element.style.display = element.style.display === 'none' ? 'block' : 'none';
        }
    }

    // Message display
    static showError(message, container = null) {
        this.showMessage(message, 'error', container);
    }

    static showSuccess(message, container = null) {
        this.showMessage(message, 'success', container);
    }

    static showMessage(message, type = 'info', container = null) {
        // Remove existing messages
        this.$$('.error, .success, .info').forEach(el => el.remove());

        const messageDiv = this.createElement('div', type, message);
        
        const targetContainer = container ? 
            (typeof container === 'string' ? this.$(container) : container) :
            this.$('content-area') || document.body;
            
        targetContainer.insertBefore(messageDiv, targetContainer.firstChild);

        // Auto-remove after delay
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, type === 'error' ? 5000 : 3000);
    }

    // Form helpers
    static getFormData(formId) {
        const form = this.$(formId);
        if (!form) return {};

        const data = {};
        const formData = new FormData(form);
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    }

    static clearForm(formId) {
        const form = this.$(formId);
        if (form) form.reset();
    }

    static setSelectOptions(selectId, options, selectedValue = null) {
        const select = this.$(selectId);
        if (!select) return;

        select.innerHTML = '';
        
        // Add default option
        const defaultOption = this.createElement('option', '', 'Select...');
        defaultOption.value = '';
        select.appendChild(defaultOption);

        // Add options
        options.forEach(option => {
            const optionElement = this.createElement('option');
            
            if (typeof option === 'string') {
                optionElement.value = option;
                optionElement.textContent = option;
            } else {
                optionElement.value = option.value;
                optionElement.textContent = option.label || option.text || option.value;
            }
            
            if (selectedValue && optionElement.value === selectedValue) {
                optionElement.selected = true;
            }
            
            select.appendChild(optionElement);
        });
    }

    // Date formatting
    static formatDate(timestamp) {
        if (!timestamp) return 'Unknown';
        
        let date;
        
        // Handle different timestamp formats
        if (typeof timestamp === 'number') {
            // Unix timestamp (seconds) - convert to milliseconds
            date = new Date(timestamp < 1e10 ? timestamp * 1000 : timestamp);
        } else if (typeof timestamp === 'string') {
            // Try parsing as ISO string first
            date = new Date(timestamp);
            
            // If invalid, try parsing as Unix timestamp string
            if (isNaN(date.getTime())) {
                const parsed = parseFloat(timestamp);
                if (!isNaN(parsed)) {
                    date = new Date(parsed < 1e10 ? parsed * 1000 : parsed);
                }
            }
        } else {
            date = new Date(timestamp);
        }
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
            console.warn('Invalid timestamp format:', timestamp);
            return 'Invalid Date';
        }
        
        return date.toLocaleString();
    }

    static extractTimestamp(event) {
        // Use only the actual field from the original schema
        return event.created_at || null;
    }

    static formatRelativeDate(timestamp) {
        if (!timestamp) return 'Unknown';
        
        const date = new Date(typeof timestamp === 'number' ? timestamp * 1000 : timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
        return `${Math.floor(diffDays / 365)} years ago`;
    }

    // String helpers
    static truncate(str, maxLength = 100) {
        if (!str || str.length <= maxLength) return str;
        return str.substring(0, maxLength - 3) + '...';
    }

    static capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    static formatEventType(eventType) {
        if (!eventType) return 'Unknown';
        return eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    // Loading states
    static showLoading(containerOrId, message = 'Loading...') {
        const container = typeof containerOrId === 'string' ? this.$(containerOrId) : containerOrId;
        if (container) {
            container.innerHTML = `<div class="loading">${message}</div>`;
        }
    }

    static hideLoading(containerId) {
        const container = this.$(containerId);
        if (container) {
            const loading = container.querySelector('.loading');
            if (loading) loading.remove();
        }
    }

    // JSON formatting
    static formatJSON(obj, indent = 2) {
        return JSON.stringify(obj, null, indent);
    }

    static formatJSONForDisplay(obj) {
        return `<pre class="json-output">${this.formatJSON(obj)}</pre>`;
    }

    // Validation
    static validateRequired(value, fieldName = 'Field') {
        if (!value || (typeof value === 'string' && value.trim() === '')) {
            throw new Error(`${fieldName} is required`);
        }
        return true;
    }

    static validateRepositoryPath(path) {
        this.validateRequired(path, 'Repository path');
        if (!path.startsWith('/')) {
            throw new Error('Repository path must be absolute');
        }
        return true;
    }

    // Debounce function
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Local storage helpers
    static getFromStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(`svcs_${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn(`Failed to get ${key} from storage:`, error);
            return defaultValue;
        }
    }

    static saveToStorage(key, value) {
        try {
            localStorage.setItem(`svcs_${key}`, JSON.stringify(value));
        } catch (error) {
            console.warn(`Failed to save ${key} to storage:`, error);
        }
    }

    static removeFromStorage(key) {
        try {
            localStorage.removeItem(`svcs_${key}`);
        } catch (error) {
            console.warn(`Failed to remove ${key} from storage:`, error);
        }
    }

    // URL helpers
    static getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    static setQueryParam(param, value) {
        const url = new URL(window.location);
        url.searchParams.set(param, value);
        window.history.replaceState({}, '', url);
    }

    // Event helpers
    static addEventListener(elementOrId, event, handler) {
        const element = typeof elementOrId === 'string' ? this.$(elementOrId) : elementOrId;
        if (element) {
            element.addEventListener(event, handler);
        }
    }

    static removeEventListener(elementOrId, event, handler) {
        const element = typeof elementOrId === 'string' ? this.$(elementOrId) : elementOrId;
        if (element) {
            element.removeEventListener(event, handler);
        }
    }

    // Array helpers
    static unique(array) {
        return [...new Set(array)];
    }

    static groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(item);
            return groups;
        }, {});
    }

    // Modal helpers
    static createModal(title, content, actions = []) {
        const modal = this.createElement('div', 'modal');
        
        const modalContent = this.createElement('div', 'modal-content');
        modalContent.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #e9ecef; padding-bottom: 15px;">
                <h3 style="margin: 0; color: #2c3e50;">${title}</h3>
                <button onclick="this.closest('.modal').remove()" style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 8px 12px; cursor: pointer; font-size: 14px;">✕ Close</button>
            </div>
            <div>${content}</div>
        `;
        
        if (actions.length > 0) {
            const actionsDiv = this.createElement('div', 'form-actions');
            actions.forEach(action => {
                const button = this.createElement('button', `btn ${action.class || ''}`, action.text);
                button.onclick = action.handler;
                actionsDiv.appendChild(button);
            });
            modalContent.appendChild(actionsDiv);
        }
        
        modal.appendChild(modalContent);
        
        // Close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        document.body.appendChild(modal);
        return modal;
    }

    static closeModal(modal) {
        if (modal && modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
    }
}

// Export for use in components - create a wrapper instance that delegates to static methods
class UtilsWrapper {
    $(id) { return Utils.$(id); }
    $$(selector) { return Utils.$$(selector); }
    createElement(tag, className, innerHTML) { return Utils.createElement(tag, className, innerHTML); }
    show(elementOrId) { return Utils.show(elementOrId); }
    hide(elementOrId) { return Utils.hide(elementOrId); }
    toggle(elementOrId) { return Utils.toggle(elementOrId); }
    showError(message, container) { return Utils.showError(message, container); }
    showSuccess(message, container) { return Utils.showSuccess(message, container); }
    showMessage(message, type, container) { return Utils.showMessage(message, type, container); }
    showLoading(container, message) { return Utils.showLoading(container, message); }
    hideLoading() { return Utils.hideLoading(); }
    formatDate(dateString) { return Utils.formatDate(dateString); }
    formatBytes(bytes) { return Utils.formatBytes(bytes); }
    formatDuration(ms) { return Utils.formatDuration(ms); }
    debounce(func, wait) { return Utils.debounce(func, wait); }
    throttle(func, limit) { return Utils.throttle(func, limit); }
    saveToStorage(key, data) { return Utils.saveToStorage(key, data); }
    loadFromStorage(key) { return Utils.loadFromStorage(key); }
    removeFromStorage(key) { return Utils.removeFromStorage(key); }
    deepClone(obj) { return Utils.deepClone(obj); }
    createModal(title, content, options) { return Utils.createModal(title, content, options); }
    closeModal(modal) { return Utils.closeModal(modal); }
}

// Export both static Utils and instance wrapper
window.Utils = Utils;
window.UtilsWrapper = UtilsWrapper;
