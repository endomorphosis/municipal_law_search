// Global variables
let currentPage = 1;
let currentQuery = '';
let totalPages = 1;
let hasSearched = false; // Track if a search has been performed

// DOM elements
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const resultsDiv = document.getElementById('results');
    const paginationDiv = document.getElementById('pagination');
    const modal = document.getElementById('lawModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    const closeModalBtn = document.getElementById('closeModal');
    const loader = document.getElementById('loader');
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');

    // Show/hide loading indicator
    function setLoading(isLoading) {
        loader.style.display = isLoading ? 'block' : 'none';
    }
    
    // Show toast notification
    function showToast(message, type = 'error') {
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

    async function searchLaws(query, page = 1) {
        // Set hasSearched flag to true
        hasSearched = true;
        
        currentQuery = query;
        currentPage = page;
        
        setLoading(true);
        resultsDiv.innerHTML = '';
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&page=${page}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Show the results and pagination containers
            document.getElementById('results').style.display = 'block';
            document.getElementById('pagination').style.display = 'flex';
            
            displayResults(data.results);
            displayPagination(data.total_pages);
            
            if (data.results.length === 0 && query) {
                showToast('No results found. Try different keywords.', 'error');
            } else if (query) {
                showToast(`Found ${data.total} results`, 'success');
            }
        } catch (error) {
            console.error('Error searching laws:', error);
            showToast('An error occurred while searching. Please try again.', 'error');
        } finally {
            setLoading(false);
        }
    }

    function displayResults(results) {
        resultsDiv.innerHTML = '';
        
        if (results.length === 0) {
            resultsDiv.innerHTML = `
                <div class="neu-card result-card text-center opacity-0">
                    <p class="text-gray-600">No results found. Try different keywords.</p>
                </div>
            `;
            
            // Animate the single "no results" card
            setTimeout(() => {
                const card = resultsDiv.querySelector('.neu-card');
                card.classList.remove('opacity-0');
                card.classList.add('fade-in');
            }, 100);
            
            return;
        }
        
        // Create all cards but make them initially invisible
        results.forEach((law, index) => {
            const lawCard = document.createElement('div');
            lawCard.className = 'neu-card result-card opacity-0';
            lawCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            lawCard.style.transform = 'translateY(20px)';
            
            lawCard.innerHTML = `
                <h3 class="result-title">${law.title}</h3>
                <div class="result-meta">
                    <span class="font-medium">${law.place_name}, ${law.state_name}</span> • 
                    <span>${law.chapter}</span> • 
                    <span>${law.date}</span>
                </div>
                <p class="result-content">${law.content}</p>
                <div class="result-footer">
                    <span class="text-text-light">${law.bluebook_citation}</span>
                    <button class="view-law-btn btn btn-primary" data-id="${law.id}">
                        View Full Text <i class="fas fa-arrow-right ml-1"></i>
                    </button>
                </div>
            `;
            
            resultsDiv.appendChild(lawCard);
            
            // Add event listener to the button
            const viewBtn = lawCard.querySelector('.view-law-btn');
            viewBtn.addEventListener('click', () => viewLaw(law.id));
            
            // Staggered animation for each card
            setTimeout(() => {
                lawCard.classList.remove('opacity-0');
                lawCard.style.opacity = '1';
                lawCard.style.transform = 'translateY(0)';
            }, 100 + (index * 150)); // 150ms delay between each card animation
        });
    }

    function displayPagination(total) {
        totalPages = total;
        paginationDiv.innerHTML = '';
        
        if (total <= 1) return;
        
        // Previous button
        if (currentPage > 1) {
            const prevButton = createPaginationButton('Previous', currentPage - 1);
            paginationDiv.appendChild(prevButton);
        }
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(total, startPage + 4);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageButton = createPaginationButton(i.toString(), i, i === currentPage);
            paginationDiv.appendChild(pageButton);
        }
        
        // Next button
        if (currentPage < total) {
            const nextButton = createPaginationButton('Next', currentPage + 1);
            paginationDiv.appendChild(nextButton);
        }
    }

    function createPaginationButton(text, page, isActive = false) {
        const button = document.createElement('button');
        button.className = `page-btn ${isActive ? 'active' : ''}`;
        button.textContent = text;
        button.setAttribute('aria-label', `Page ${text}`);
        
        button.addEventListener('click', () => searchLaws(currentQuery, page));
        return button;
    }

    async function viewLaw(lawId) {
        try {
            setLoading(true);
            const response = await fetch(`/api/law/${lawId}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const law = await response.json();
            
            modalTitle.textContent = law.title;
            modalContent.innerHTML = `
                <div class="mb-4">
                    <div class="text-sm text-gray-600">
                        <span class="font-medium">${law.place_name}, ${law.state_name}</span> • 
                        <span>${law.chapter}</span> • 
                        <span>${law.date}</span>
                    </div>
                    <div class="text-sm text-gray-500 mt-1">${law.bluebook_citation}</div>
                </div>
                <div class="prose max-w-none">
                    ${law.content.split('\n').map(para => `<p class="mb-4">${para}</p>`).join('')}
                </div>
            `;
            
            // Show modal with animation
            modal.classList.add('active');
            
            // Add accessibility focus
            closeModalBtn.focus();
            
            // Add keyboard support
            document.addEventListener('keydown', handleEscapeKey);
        } catch (error) {
            console.error('Error fetching law details:', error);
            showToast('An error occurred while loading the law details.', 'error');
        } finally {
            setLoading(false);
        }
    }
    
    function closeModal() {
        modal.classList.remove('active');
        document.removeEventListener('keydown', handleEscapeKey);
    }
    
    function handleEscapeKey(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    }

    // Event Listeners
    searchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        searchLaws(query);
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = e.target.value.trim();
            searchLaws(query);
        }
    });

    closeModalBtn.addEventListener('click', closeModal);
    
    // Click outside modal to close
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Hide results container initially
    document.getElementById('results').style.display = 'none';
    document.getElementById('pagination').style.display = 'none';
});