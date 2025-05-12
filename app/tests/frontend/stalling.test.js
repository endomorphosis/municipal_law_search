
/**
 * Tests for the stalling.js functionality
 * This test suite verifies the stalling messages component behavior
 */

describe('Stalling Message Component', () => {
  // Setup DOM elements for testing
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="search-form"></div>
      <div id="search-results"></div>
      <div id="loading-container" style="display: none;">
        <p id="stalling-message">Processing your request...</p>
      </div>
    `;
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
    if (window.eventSource) {
      window.eventSource.close();
      window.eventSource = null;
    }
  });
  
  // Mock EventSource since it's not available in JSDOM
  class MockEventSource {
    constructor(url) {
      this.url = url;
      this.onmessage = null;
      this.onerror = null;
      this.close = jest.fn();
    }
    
    // Simulate receiving a message
    simulateMessage(data) {
      if (this.onmessage) {
        this.onmessage({ data: JSON.stringify(data) });
      }
    }
    
    // Simulate an error
    simulateError() {
      if (this.onerror) {
        this.onerror();
      }
    }
  }
  
  // Mock global EventSource
  global.EventSource = MockEventSource;
  
  test('connectToStallingMessages creates loading container if it does not exist', () => {
    // Remove the loading container to test creation
    document.getElementById('loading-container').remove();
    
    // Import the function to make it available
    const { connectToStallingMessages } = require('../../frontend/static/js/stalling/stalling');
    
    connectToStallingMessages('test-request-id');
    
    const loadingContainer = document.getElementById('loading-container');
    expect(loadingContainer).not.toBeNull();
    expect(loadingContainer.style.display).toBe('block');
    
    const messageElement = document.getElementById('stalling-message');
    expect(messageElement).not.toBeNull();
    expect(messageElement.textContent).toBe('Processing your request...');
  });
  
  test('connectToStallingMessages shows existing container if it exists', () => {
    // Import the function to make it available
    const { connectToStallingMessages } = require('../../frontend/static/js/stalling/stalling');
    
    connectToStallingMessages('test-request-id');
    
    const loadingContainer = document.getElementById('loading-container');
    expect(loadingContainer.style.display).toBe('block');
  });
  
  test('connectToStallingMessages creates and configures EventSource correctly', () => {
    // Import the function to make it available
    const { connectToStallingMessages } = require('../../frontend/static/js/stalling/stalling');
    
    connectToStallingMessages('test-request-id');
    
    // Check if EventSource was created with correct URL
    expect(window.eventSource).not.toBeNull();
    expect(window.eventSource.url).toBe('/api/stalling/test-request-id');
  });
  
  test('EventSource handles stalling message updates correctly', () => {
    // Import the function to make it available
    const { connectToStallingMessages } = require('../../frontend/static/js/stalling/stalling');
    
    connectToStallingMessages('test-request-id');
    
    // Simulate receiving a stalling message
    window.eventSource.simulateMessage({
      type: 'stalling',
      message: 'New stalling message'
    });
    
    const messageElement = document.getElementById('stalling-message');
    expect(messageElement.textContent).toBe('New stalling message');
  });
  
  test('EventSource handles completion message correctly', () => {
    // Import the function to make it available
    const { connectToStallingMessages } = require('../../frontend/static/js/stalling/stalling');
    
    connectToStallingMessages('test-request-id');
    
    // Simulate receiving a completion message
    window.eventSource.simulateMessage({
      type: 'completion'
    });
    
    const loadingContainer = document.getElementById('loading-container');
    expect(loadingContainer.style.display).toBe('none');
    expect(window.eventSource).toBeNull();
  });
  
  test('EventSource handles errors correctly', () => {
    // Import the function to make it available
    const { connectToStallingMessages } = require('../../frontend/static/js/stalling/stalling');
    
    connectToStallingMessages('test-request-id');
    
    // Simulate an error
    window.eventSource.simulateError();
    
    const loadingContainer = document.getElementById('loading-container');
    expect(loadingContainer.style.display).toBe('none');
    expect(window.eventSource).toBeNull();
  });
  
  test('performSearch shows loading immediately', async () => {
    // Mock fetch for performSearch
    global.fetch = jest.fn().mockResolvedValue({
      json: jest.fn().mockResolvedValue({ request_id: 'server-request-id' })
    });
    
    // Import the function to make it available
    const { performSearch } = require('../../frontend/static/js/stalling/stalling');
    
    await performSearch('test query');
    
    const loadingContainer = document.getElementById('loading-container');
    expect(loadingContainer.style.display).toBe('block');
    
    const messageElement = document.getElementById('stalling-message');
    expect(messageElement.textContent).toBe('Alright, let me get to work on this.');
    
    // Clean up mock
    global.fetch.mockRestore();
  });
});