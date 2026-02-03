/**
 * Theme management for light/dark mode
 */

(function() {
    'use strict';
    
    // Constants
    const THEME_KEY = 'book-theme';
    const THEME_LIGHT = 'light';
    const THEME_DARK = 'dark';
    
    function safeGetItem(key) {
        try {
            return localStorage.getItem(key);
        } catch (_) {
            return null;
        }
    }

    function safeSetItem(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (_) {}
    }
    
    // Get system preference
    function getSystemTheme() {
        if (typeof window.matchMedia !== 'function') {
            return THEME_LIGHT;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? THEME_DARK : THEME_LIGHT;
    }
    
    // Get saved theme or system preference
    function getSavedTheme() {
        return safeGetItem(THEME_KEY) || getSystemTheme();
    }
    
    // Apply theme to document
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        safeSetItem(THEME_KEY, theme);
    }
    
    // Toggle theme
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
        applyTheme(newTheme);
    }
    
    // Initialize theme
    function initTheme() {
        // Apply saved theme
        const savedTheme = getSavedTheme();
        applyTheme(savedTheme);
        
        // Add event listener to theme toggle button
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
        }
        
        // Listen for system theme changes
        if (typeof window.matchMedia === 'function') {
            const mq = window.matchMedia('(prefers-color-scheme: dark)');
            const handler = (e) => {
                if (!safeGetItem(THEME_KEY)) {
                    applyTheme(e.matches ? THEME_DARK : THEME_LIGHT);
                }
            };
            if (mq.addEventListener) {
                mq.addEventListener('change', handler);
            } else if (mq.addListener) {
                mq.addListener(handler);
            }
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
})();
