// Search History Management
document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const historyBtn = document.getElementById('historyBtn');
    const historyModal = document.getElementById('historyModal');
    const historyClose = document.querySelector('.history-close');
    const historyList = document.getElementById('historyList');
    const historyPagination = document.getElementById('historyPagination');
    const historyClearBtn = document.getElementById('historyClearBtn');
    
    // State
    let currentHistoryPage = 1;
    let totalHistoryPages = 1;
    
    // Event listeners
    if (historyBtn) {
        historyBtn.addEventListener('click', () => {
            openHistoryModal();
        });
    }
    
    if (historyClose) {
        historyClose.addEventListener('click', () => {
            closeHistoryModal();
        });
    }
    
    if (historyModal) {
        historyModal.addEventListener('click', (e) => {
            if (e.target === historyModal) {
                closeHistoryModal();
            }
        });
    }
    
    if (historyClearBtn) {
        historyClearBtn.addEventListener('click', () => {
            confirmClearHistory();
        });
    }
    
    // Handle escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && historyModal && historyModal.classList.contains('active')) {
            closeHistoryModal();
        }
    });
    
    // Functions
    function openHistoryModal() {
        if (historyModal) {
            loadSearchHistory(1);
            historyModal.classList.add('active');
        }
    }
    
    function closeHistoryModal() {
        if (historyModal) {
            historyModal.classList.remove('active');
        }
    }
    
    async function loadSearchHistory(page = 1, perPage = 10) {
        if (!historyList) return;
        
        try {
            // Show loading state
            historyList.innerHTML = '<div class="text-center p-4"><i class="fas fa-spinner fa-spin"></i> Loading search history...</div>';
            
            // Fetch search history
            const response = await fetch(`/api/search-history?page=${page}&per_page=${perPage}`);
            
            if (!response.ok) {
                throw new Error('Failed to load search history');
            }
            
            const data = await response.json();
            
            // Update state
            currentHistoryPage = data.page;
            totalHistoryPages = data.total_pages;
            
            // Render search history
            renderSearchHistory(data);
            renderHistoryPagination();
            
        } catch (error) {
            console.error('Error loading search history:', error);
            historyList.innerHTML = `
                <div class="history-empty">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading search history. Please try again.</p>
                </div>
            `;
        }
    }
    
    function renderSearchHistory(data) {
        if (!historyList) return;
        
        if (data.entries.length === 0) {
            historyList.innerHTML = `
                <div class="history-empty">
                    <i class="fas fa-history"></i>
                    <p>No search history found.</p>
                </div>
            `;
            return;
        }
        
        historyList.innerHTML = '';
        
        // Sort entries by timestamp (newest first)
        const sortedEntries = [...data.entries].sort((a, b) => {
            return new Date(b.timestamp) - new Date(a.timestamp);
        });
        
        // Create elements for each history item
        sortedEntries.forEach((entry, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.style.setProperty('--order', index);
            
            // Format date
            const timestamp = new Date(entry.timestamp);
            const formattedDate = timestamp.toLocaleDateString() + ' ' + timestamp.toLocaleTimeString();
            
            historyItem.innerHTML = `
                <div class="history-query">${escapeHtml(entry.search_query)}</div>
                <div class="history-meta">
                    <span class="history-time">
                        <i class="fas fa-clock"></i> ${formattedDate}
                    </span>
                    <span class="history-results">
                        <i class="fas fa-file-alt"></i> ${entry.result_count} results
                    </span>
                </div>
                <div class="history-actions">
                    <button class="history-search-btn" data-query="${escapeHtml(entry.search_query)}">
                        <i class="fas fa-search"></i> Search Again
                    </button>
                    <button class="history-delete-btn" data-id="${entry.search_id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            `;
            
            historyList.appendChild(historyItem);
            
            // Add event listeners to buttons
            const searchAgainBtn = historyItem.querySelector('.history-search-btn');
            const deleteBtn = historyItem.querySelector('.history-delete-btn');
            
            if (searchAgainBtn) {
                searchAgainBtn.addEventListener('click', () => {
                    searchAgain(entry.search_query);
                });
            }
            
            if (deleteBtn) {
                deleteBtn.addEventListener('click', () => {
                    deleteHistoryEntry(entry.search_id);
                });
            }
        });
    }
    
    function renderHistoryPagination() {
        if (!historyPagination || totalHistoryPages <= 1) {
            if (historyPagination) {
                historyPagination.innerHTML = '';
            }
            return;
        }
        
        historyPagination.innerHTML = '';
        
        // Previous button
        if (currentHistoryPage > 1) {
            const prevButton = createPaginationButton('Previous', currentHistoryPage - 1);
            historyPagination.appendChild(prevButton);
        }
        
        // Page numbers
        const startPage = Math.max(1, currentHistoryPage - 2);
        const endPage = Math.min(totalHistoryPages, startPage + 4);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageButton = createPaginationButton(i.toString(), i, i === currentHistoryPage);
            historyPagination.appendChild(pageButton);
        }
        
        // Next button
        if (currentHistoryPage < totalHistoryPages) {
            const nextButton = createPaginationButton('Next', currentHistoryPage + 1);
            historyPagination.appendChild(nextButton);
        }
    }
    
    function createPaginationButton(text, page, isActive = false) {
        const button = document.createElement('button');
        button.className = `history-pagination-btn ${isActive ? 'active' : ''}`;
        button.textContent = text;
        
        button.addEventListener('click', () => {
            loadSearchHistory(page);
        });
        
        return button;
    }
    
    function searchAgain(query) {
        if (!query) return;
        
        // Set the search input value
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = query;
        }
        
        // Close the history modal
        closeHistoryModal();
        
        // Trigger the search
        const searchButton = document.getElementById('searchButton');
        if (searchButton) {
            searchButton.click();
        }
    }
    
    async function deleteHistoryEntry(searchId) {
        if (!searchId) return;
        
        try {
            const response = await fetch(`/api/search-history/${searchId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete history entry');
            }
            
            // Reload the current page of history
            loadSearchHistory(currentHistoryPage);
            
            // Show success toast
            showToast('History entry deleted successfully', 'success');
            
        } catch (error) {
            console.error('Error deleting history entry:', error);
            showToast('Error deleting history entry', 'error');
        }
    }
    
    function confirmClearHistory() {
        if (confirm('Are you sure you want to clear all search history? This action cannot be undone.')) {
            clearAllHistory();
        }
    }
    
    async function clearAllHistory() {
        try {
            const response = await fetch('/api/search-history', {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to clear history');
            }
            
            // Reload the first page of history (which should be empty now)
            loadSearchHistory(1);
            
            // Show success toast
            showToast('Search history cleared successfully', 'success');
            
        } catch (error) {
            console.error('Error clearing history:', error);
            showToast('Error clearing search history', 'error');
        }
    }
    
    // Helper functions
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    function showToast(message, type = 'error') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        const toastIcon = document.getElementById('toastIcon');
        
        if (!toast || !toastMessage || !toastIcon) return;
        
        toastMessage.textContent = message;
        
        if (type === 'error') {
            toast.className = 'toast toast-error active';
            toastIcon.className = 'fas fa-exclamation-circle text-red-500';
        } else {
            toast.className = 'toast toast-success active';
            toastIcon.className = 'fas fa-check-circle text-green-500';
        }
        
        setTimeout(() => {
            toast.classList.remove('active');
        }, 3000);
    }
});