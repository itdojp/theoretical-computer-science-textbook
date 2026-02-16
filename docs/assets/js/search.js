/**
 * Search functionality
 */

(function() {
    'use strict';
    
    let searchInput;
    let searchResults;
    let searchIndex = [];
    let currentResults = [];
    let activeIndex = -1;
    let searchTimeout;
    
    // Initialize elements
    function initElements() {
        searchInput = document.getElementById('search-input');
        searchResults = document.getElementById('search-results');
    }

    function getSiteBasePath() {
        // Prefer deriving baseurl from the script tag src (works for GitHub Pages project sites).
        // Example: /<repo>/assets/js/search.js -> baseurl: /<repo>
        try {
            const suffix = '/assets/js/search.js';
            const scripts = document.getElementsByTagName('script');
            for (let i = 0; i < scripts.length; i++) {
                const src = scripts[i].getAttribute('src') || '';
                if (!src) continue;
                if (!src.endsWith(suffix)) continue;
                const u = new URL(src, window.location.href);
                const p = u.pathname || '';
                if (p.endsWith(suffix)) {
                    return p.slice(0, -suffix.length);
                }
            }
        } catch (_) {}

        // Fallback: first path segment (best-effort).
        try {
            const seg = window.location.pathname.split('/').filter(Boolean)[0];
            return seg ? '/' + seg : '';
        } catch (_) {
            return '';
        }
    }

    async function loadSearchData() {
        const base = getSiteBasePath();
        const url = `${base}/assets/search-data.json`;
        const res = await fetch(url, { credentials: 'same-origin' });
        if (!res.ok) {
            throw new Error(`failed to fetch search-data.json: ${res.status}`);
        }
        const data = await res.json();
        if (!data || !Array.isArray(data.items)) {
            throw new Error('invalid search-data.json schema');
        }

        // Page-level index (title + excerpt).
        searchIndex = data.items
            .map((item, idx) => {
                const title = String(item.title || '').trim();
                const content = String(item.excerpt || '').trim();
                const pageUrl = String(item.url || '').trim();
                return {
                    id: `search-page-${idx}`,
                    title,
                    content,
                    url: pageUrl,
                    type: 'page'
                };
            })
            .filter(it => it.title && it.url);
    }
    
    // Build search index from page content
    function buildSearchIndex() {
        searchIndex = [];
        // In a real implementation, this would be generated at build time
        // For now, we'll create a simple index from current page
        const content = document.querySelector('.page-content');
        if (!content) return;
        
        // Get all headings and paragraphs
        const elements = content.querySelectorAll('h1, h2, h3, h4, h5, h6, p');
        
        elements.forEach((el, index) => {
            const text = el.textContent.trim();
            if (text) {
                searchIndex.push({
                    id: `search-result-${index}`,
                    title: el.tagName.startsWith('H') ? text : text.substring(0, 50) + '...',
                    content: text,
                    element: el,
                    type: el.tagName.toLowerCase()
                });
            }
        });
    }
    
    // Perform search
    function performSearch(query) {
        if (!query || query.length < 2) {
            hideResults();
            return;
        }
        
        const results = searchIndex.filter(item => {
            const searchText = `${item.title} ${item.content}`.toLowerCase();
            return searchText.includes(query.toLowerCase());
        });
        
        displayResults(results, query);
    }
    
    // Display search results
    function displayResults(results, query) {
        if (!searchResults) return;

        currentResults = results.slice(0, 10);
        activeIndex = -1;
        if (searchInput) {
            searchInput.removeAttribute('aria-activedescendant');
        }
        
        if (results.length === 0) {
            searchResults.innerHTML = `
                <div class="search-no-results">
                    <p>「${escapeHtml(query)}」に一致する結果が見つかりませんでした。</p>
                </div>
            `;
        } else {
            const resultsHtml = currentResults.map((result, idx) => {
                const highlightedTitle = highlightText(result.title, query);
                const snippet = getSnippet(result.content, query);
                const highlightedSnippet = highlightText(snippet, query);
                
                return `
                    <div class="search-result-item" id="${result.id}" role="option" tabindex="-1" aria-selected="false" data-id="${result.id}" data-index="${idx}">
                        <div class="search-result-title">${highlightedTitle}</div>
                        <div class="search-result-snippet">${highlightedSnippet}</div>
                    </div>
                `;
            }).join('');
            
            searchResults.innerHTML = `
                <div class="search-results-list" id="search-results-listbox" role="listbox" aria-label="Search results">
                    ${resultsHtml}
                </div>
                ${results.length > 10 ? `<div class="search-more">他 ${results.length - 10} 件の結果</div>` : ''}
            `;
        }
        
        showResults();
    }

    function setActiveIndex(next) {
        if (!searchResults) return;
        const items = searchResults.querySelectorAll('.search-result-item');
        if (!items || items.length === 0) return;

        // Normalize index
        if (next < 0) next = items.length - 1;
        if (next >= items.length) next = 0;

        if (activeIndex >= 0 && activeIndex < items.length) {
            items[activeIndex].classList.remove('active');
            items[activeIndex].setAttribute('aria-selected', 'false');
        }

        activeIndex = next;
        const el = items[activeIndex];
        el.classList.add('active');
        el.setAttribute('aria-selected', 'true');
        if (searchInput && el.id) {
            searchInput.setAttribute('aria-activedescendant', el.id);
        }
        // Keep the active option visible in the scrollable list.
        try { el.scrollIntoView({ block: 'nearest' }); } catch (_) {}
    }

    function selectResultById(id) {
        const result = searchIndex.find(item => item.id === id);
        if (!result) return;

        hideResults();
        if (searchInput) {
            searchInput.value = '';
        }

        if (result.url) {
            window.location.href = result.url;
            return;
        }

        if (!result.element) return;
        result.element.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Highlight the element temporarily
        result.element.classList.add('search-highlight');
        setTimeout(() => {
            result.element.classList.remove('search-highlight');
        }, 2000);
    }
    
    // Get snippet around query
    function getSnippet(text, query) {
        const index = text.toLowerCase().indexOf(query.toLowerCase());
        if (index === -1) return text.substring(0, 150) + '...';
        
        const start = Math.max(0, index - 50);
        const end = Math.min(text.length, index + query.length + 100);
        
        let snippet = text.substring(start, end);
        if (start > 0) snippet = '...' + snippet;
        if (end < text.length) snippet = snippet + '...';
        
        return snippet;
    }
    
    // Highlight search term in text
    function highlightText(text, query) {
        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    // Show search results
    function showResults() {
        if (searchResults) {
            searchResults.classList.add('active');
        }
        if (searchInput) {
            searchInput.setAttribute('aria-expanded', 'true');
        }
    }
    
    // Hide search results
    function hideResults() {
        if (searchResults) {
            searchResults.classList.remove('active');
        }
        activeIndex = -1;
        if (searchInput) {
            searchInput.setAttribute('aria-expanded', 'false');
            searchInput.removeAttribute('aria-activedescendant');
        }
    }
    
    // Handle search result click
    function handleResultClick(e) {
        const resultItem = e.target.closest('.search-result-item');
        if (!resultItem) return;
        
        const id = resultItem.dataset.id;
        selectResultById(id);
    }
    
    // Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Escape regex
    function escapeRegex(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    // Initialize search
    function initSearch() {
        initElements();
        
        if (!searchInput || !searchResults) return;

        // Basic combobox/listbox ARIA wiring for keyboard + screen reader users.
        searchInput.setAttribute('role', 'combobox');
        searchInput.setAttribute('aria-autocomplete', 'list');
        searchInput.setAttribute('aria-haspopup', 'listbox');
        searchInput.setAttribute('aria-controls', 'search-results-listbox');
        searchInput.setAttribute('aria-expanded', 'false');
        
        // Build initial search index
        buildSearchIndex();

        // Prefer a build-time generated index (whole site). Fallback to in-page index.
        // This keeps the search usable even if fetch fails (offline, 404, etc.).
        loadSearchData()
            .then(() => {
                const q = searchInput.value.trim();
                if (q && q.length >= 2) performSearch(q);
            })
            .catch(() => {});
        
        // Search input handler
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(e.target.value.trim());
            }, 300);
        });
        
        // Focus/blur handlers
        searchInput.addEventListener('focus', () => {
            if (searchInput.value.trim()) {
                showResults();
            }
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                hideResults();
            }
        });
        
        // Handle result clicks
        searchResults.addEventListener('click', handleResultClick);
        
        // Handle escape key
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                hideResults();
                searchInput.blur();
                return;
            }

            if (!searchResults || !searchResults.classList.contains('active')) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setActiveIndex(activeIndex + 1);
                return;
            }

            if (e.key === 'ArrowUp') {
                e.preventDefault();
                setActiveIndex(activeIndex - 1);
                return;
            }

            if (e.key === 'Enter') {
                if (activeIndex < 0) return;
                const items = searchResults.querySelectorAll('.search-result-item');
                if (!items || !items.length || activeIndex >= items.length) return;
                const id = items[activeIndex].dataset.id;
                if (id) {
                    e.preventDefault();
                    selectResultById(id);
                }
            }
        });
    }
    
    // Add styles
    const styles = `
        <style>
        .search-results-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .search-result-item {
            padding: 0.75rem 1rem;
            cursor: pointer;
            border-bottom: 1px solid var(--border-color);
            transition: var(--transition);
        }
        
        .search-result-item:hover {
            background: var(--bg-secondary);
        }

        .search-result-item.active {
            background: var(--bg-tertiary);
        }
        
        .search-result-item:last-child {
            border-bottom: none;
        }
        
        .search-result-title {
            font-weight: 500;
            margin-bottom: 0.25rem;
            color: var(--text-primary);
        }
        
        .search-result-snippet {
            font-size: 0.875rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }
        
        .search-no-results {
            padding: 2rem;
            text-align: center;
            color: var(--text-secondary);
        }
        
        .search-more {
            padding: 0.75rem 1rem;
            text-align: center;
            font-size: 0.875rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
        }
        
        mark {
            background: rgba(255, 235, 59, 0.4);
            color: inherit;
            padding: 0.125rem 0;
            border-radius: 2px;
        }
        
        [data-theme="dark"] mark {
            background: rgba(255, 235, 59, 0.2);
        }
        
        .search-highlight {
            animation: highlight 2s ease;
        }
        
        @keyframes highlight {
            0% { background: rgba(255, 235, 59, 0.4); }
            100% { background: transparent; }
        }
        </style>
    `;
    
    // Inject styles
    document.head.insertAdjacentHTML('beforeend', styles);
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSearch);
    } else {
        initSearch();
    }
})();
