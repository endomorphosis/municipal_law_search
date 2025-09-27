
/**
 * Tests for the history.js functionality
 * This test suite verifies the search history management functionality
 */

describe('Search History Component', () => {
  // Setup DOM elements for testing
  beforeEach(() => {
    document.body.innerHTML = `
      <button id="historyBtn">History</button>
      <div id="historyModal" class="modal">
        <div class="modal-content">
          <span class="history-close">&times;</span>
          <h2>Search History</h2>
          <div class="history-container">
            <div id="historyList" class="history-list"></div>
            <div id="historyPagination" class="history-pagination"></div>
            <button id="historyClearBtn" class="btn btn-danger">Clear History</button>
          </div>
        </div>
      </div>
      <div class="search-container">
        <input id="searchInput" type="text" />
        <button id="searchButton">Search</button>
      </div>
      <div id="toast" class="toast">
        <div class="toast-icon">
          <i id="toastIcon" class="fas fa-exclamation-circle"></i>
        </div>
        <div id="toastMessage" class="toast-message"></div>
      </div>
    `;
    
    // Mock fetch for API calls
    global.fetch = jest.fn();
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
  });
  
  test('History modal is displayed when history button is clicked', () => {
    // Mock fetch response for loadSearchHistory
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({
        entries: [],
        page: 1,
        total_pages: 0
      })
    });
    
    // Trigger DOMContentLoaded to initialize the history modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const historyBtn = document.getElementById('historyBtn');
    const historyModal = document.getElementById('historyModal');
    
    // Verify initial state - modal has no active class
    expect(historyModal.classList).not.toContain('active');
    
    // Click history button
    historyBtn.click();
    
    // Check if modal is displayed
    expect(historyModal.classList).toContain('active');
    
    // Check if loadSearchHistory was called
    expect(fetch).toHaveBeenCalledWith('/api/search-history?page=1&per_page=10');
  });
  
  test('History modal is hidden when close button is clicked', () => {
    // Mock fetch response
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({
        entries: [],
        page: 1,
        total_pages: 0
      })
    });
    
    // Trigger DOMContentLoaded to initialize the history modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const historyBtn = document.getElementById('historyBtn');
    const historyModal = document.getElementById('historyModal');
    const closeBtn = document.querySelector('.history-close');
    
    // Show modal
    historyBtn.click();
    expect(historyModal.classList).toContain('active');
    
    // Click close button
    closeBtn.click();
    
    // Check if modal is hidden
    expect(historyModal.classList).not.toContain('active');
  });
  
  test('History modal is hidden when escape key is pressed', () => {
    // Mock fetch response
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({
        entries: [],
        page: 1,
        total_pages: 0
      })
    });
    
    // Trigger DOMContentLoaded to initialize the history modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const historyBtn = document.getElementById('historyBtn');
    const historyModal = document.getElementById('historyModal');
    
    // Show modal
    historyBtn.click();
    expect(historyModal.classList).toContain('active');
    
    // Press Escape key
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    
    // Check if modal is hidden
    expect(historyModal.classList).not.toContain('active');
  });
  
  test('loadSearchHistory properly renders search history items', async () => {
    // Sample history entries
    const mockHistoryData = {
      entries: [
        {
          search_id: '123',
          search_query: 'test query 1',
          timestamp: new Date().toISOString(),
          result_count: 5
        },
        {
          search_id: '456',
          search_query: 'test query 2',
          timestamp: new Date().toISOString(),
          result_count: 10
        }
      ],
      page: 1,
      total_pages: 1
    };
    
    // Mock fetch response
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockHistoryData)
    });
    
    // Trigger DOMContentLoaded to initialize the history modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get reference to history button and click it
    const historyBtn = document.getElementById('historyBtn');
    historyBtn.click();
    
    // Wait for the fetch to complete
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // Check if history items are rendered
    const historyList = document.getElementById('historyList');
    const historyItems = historyList.querySelectorAll('.history-item');
    
    expect(historyItems.length).toBe(2);
    expect(historyList.innerHTML).toContain('test query 1');
    expect(historyList.innerHTML).toContain('test query 2');
    
    // Check if the buttons were created
    const searchAgainBtns = historyList.querySelectorAll('.history-search-btn');
    const deleteBtns = historyList.querySelectorAll('.history-delete-btn');
    
    expect(searchAgainBtns.length).toBe(2);
    expect(deleteBtns.length).toBe(2);
  });
  
  test('Empty history shows appropriate message', async () => {
    // Mock empty history response
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({
        entries: [],
        page: 1,
        total_pages: 0
      })
    });
    
    // Trigger DOMContentLoaded to initialize the history modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get reference to history button and click it
    const historyBtn = document.getElementById('historyBtn');
    historyBtn.click();
    
    // Wait for the fetch to complete
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // Check if empty history message is shown
    const historyList = document.getElementById('historyList');
    expect(historyList.innerHTML).toContain('No search history found');
  });
  
  test('Search again button sets input value and triggers search', async () => {
    // Mock history data with one entry
    const mockHistoryData = {
      entries: [
        {
          search_id: '123',
          search_query: 'test query',
          timestamp: new Date().toISOString(),
          result_count: 5
        }
      ],
      page: 1,
      total_pages: 1
    };
    
    // Mock fetch response
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockHistoryData)
    });
    
    // Trigger DOMContentLoaded to initialize the history modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const historyBtn = document.getElementById('historyBtn');
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    
    // Spy on search button click
    const searchButtonSpy = jest.spyOn(searchButton, 'click');
    
    // Show history modal
    historyBtn.click();
    
    // Wait for the fetch to complete
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // Get the search again button and click it
    const searchAgainBtn = document.querySelector('.history-search-btn');
    searchAgainBtn.click();
    
    // Check if input was set and search button was clicked
    expect(searchInput.value).toBe('test query');
    expect(searchButtonSpy).toHaveBeenCalled();
  });
});