
/**
 * Tests for the index.js functionality
 * This test suite verifies the search functionality and result display
 */

describe('American Law Search Index Page', () => {
  // Setup DOM elements for testing
  beforeEach(() => {
    document.body.innerHTML = `
      <div class="search-container">
        <input id="searchInput" type="text" placeholder="Search American law..." />
        <button id="searchButton" type="button">Search</button>
      </div>
      <div id="resultsContainer">
        <div id="results"></div>
        <div id="pagination"></div>
      </div>
      <div id="lawModal" class="modal">
        <div class="modal-content">
          <span id="closeModal" class="close">&times;</span>
          <h2 id="modalTitle"></h2>
          <div id="modalContent"></div>
        </div>
      </div>
      <div id="loader" style="display: none;"></div>
      <div id="toast" class="toast">
        <div class="toast-icon">
          <i id="toastIcon" class="fas fa-exclamation-circle"></i>
        </div>
        <div id="toastMessage" class="toast-message"></div>
      </div>
      <div id="stallingContainer" style="display: none;">
        <p id="stallingMessage"></p>
      </div>
    `;
    
    // Mock EventSource since it's not available in JSDOM
    global.EventSource = jest.fn().mockImplementation(() => ({
      addEventListener: jest.fn(),
      close: jest.fn()
    }));
    
    // Mock fetch
    global.fetch = jest.fn();
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
  });
  
  test('searchLawsSSE starts stalling messages and sets up EventSource', () => {
    // Import the functions
    const indexModule = require('../../frontend/static/js/index/index');
    
    // Get references to the mocked functions
    const startStallingMessages = jest.fn();
    const searchLawsSSE = indexModule.searchLawsSSE;
    
    // Create a spy on startStallingMessages
    indexModule.startStallingMessages = startStallingMessages;
    
    // Call the search function
    searchLawsSSE('test query');
    
    // Check if startStallingMessages was called
    expect(startStallingMessages).toHaveBeenCalled();
    
    // Check if EventSource was created with the correct URL
    expect(EventSource).toHaveBeenCalledWith(
      expect.stringContaining('/api/search/sse?q=test%20query')
    );
  });
  
  test('displayResults shows no results message when results array is empty', () => {
    // Import the function
    const { displayResults } = require('../../frontend/static/js/index/index');
    
    // Call displayResults with empty array
    displayResults([]);
    
    // Check if the no results message is displayed
    const resultsDiv = document.getElementById('results');
    expect(resultsDiv.innerHTML).toContain('No results found');
  });
  
  test('displayResults creates result cards for each law', () => {
    // Import the function
    const { displayResults } = require('../../frontend/static/js/index/index');
    
    // Sample results
    const mockResults = [
      {
        cid: '123',
        title: 'Test Law 1',
        place_name: 'Test Place',
        state_name: 'Test State',
        chapter: 'Chapter 1',
        html: '<p>Test content</p>',
        bluebook_citation: 'Test Citation 1'
      },
      {
        cid: '456',
        title: 'Test Law 2',
        place_name: 'Test Place',
        state_name: 'Test State',
        chapter: 'Chapter 2',
        html: '<p>More test content</p>',
        bluebook_citation: 'Test Citation 2'
      }
    ];
    
    // Call displayResults with mock data
    displayResults(mockResults);
    
    // Check if result cards are created
    const resultsDiv = document.getElementById('results');
    const resultCards = resultsDiv.querySelectorAll('.result-card');
    
    expect(resultCards.length).toBe(2);
    expect(resultsDiv.innerHTML).toContain('Test Law 1');
    expect(resultsDiv.innerHTML).toContain('Test Law 2');
  });
  
  test('viewLaw fetches and displays law details in modal', async () => {
    // Mock fetch response
    const mockLaw = {
      title: 'Test Law',
      place_name: 'Test Place',
      state_name: 'Test State',
      chapter: 'Test Chapter',
      html: 'Test content',
      bluebook_citation: 'Test Citation'
    };
    
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockLaw)
    });
    
    // Import the function
    const { viewLaw } = require('../../frontend/static/js/index/index');
    
    // Call viewLaw with a mock ID
    await viewLaw('test-id');
    
    // Check if fetch was called with the correct URL
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/law/test-id'));
    
    // Check if modal content was updated
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    const modal = document.getElementById('lawModal');
    
    expect(modalTitle.textContent).toBe('Test Law');
    expect(modalContent.innerHTML).toContain('Test content');
    expect(modal.classList).toContain('active');
  });
  
  test('closeModal removes active class from modal', () => {
    // Setup modal with active class
    const modal = document.getElementById('lawModal');
    modal.classList.add('active');
    
    // Import the function
    const { closeModal } = require('../../frontend/static/js/index/index');
    
    // Call closeModal
    closeModal();
    
    // Check if active class was removed
    expect(modal.classList).not.toContain('active');
  });
});