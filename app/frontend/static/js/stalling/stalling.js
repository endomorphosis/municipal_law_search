/**
 * Stalling Chatbot Frontend Integration
 * This script connects to the server-sent events endpoint
 * to display stalling messages while waiting for search results.
 */

// DOM Elements
const searchForm = document.getElementById('search-form');
const searchResults = document.getElementById('search-results');
const loadingContainer = document.getElementById('loading-container');
const stallingMessage = document.getElementById('stalling-message');

// Track current SSE connection
let eventSource = null;

// Connect to SSE endpoint to receive stalling messages
function connectToStallingMessages(requestId) {
  // Create loading container if it doesn't exist
  if (!loadingContainer) {
    const container = document.createElement('div');
    container.id = 'loading-container';
    container.className = 'loading-container';
    
    const messageElement = document.createElement('p');
    messageElement.id = 'stalling-message';
    messageElement.className = 'stalling-message';
    messageElement.textContent = 'Processing your request...';
    
    container.appendChild(messageElement);
    searchResults.parentNode.insertBefore(container, searchResults);
  } else {
    loadingContainer.style.display = 'block';
  }
  
  // Close existing connection if there is one
  if (eventSource) {
    eventSource.close();
  }
  
  // Connect to the stalling endpoint
  eventSource = new EventSource(`/api/stalling/${requestId}`);
  
  // Handle incoming messages
  eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'stalling') {
      // Update the stalling message
      document.getElementById('stalling-message').textContent = data.message;
    } else if (data.type === 'completion') {
      // Close the connection when the search is complete
      eventSource.close();
      eventSource = null;
      
      // Hide the loading container
      loadingContainer.style.display = 'none';
    }
  };
  
  // Handle errors
  eventSource.onerror = function() {
    eventSource.close();
    eventSource = null;
    loadingContainer.style.display = 'none';
  };
}

// Modified search function
async function performSearch(query, page = 1, perPage = 20) {
  // Show loading immediately
  if (loadingContainer) {
    loadingContainer.style.display = 'block';
    stallingMessage.textContent = 'Alright, let me get to work on this.';
  }
  
  try {
    // Generate a temporary request ID until we get the real one
    const tempRequestId = Date.now().toString();
    connectToStallingMessages(tempRequestId);
    
    // Make the search request
    const response = await fetch(`/api/search/sse?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`);
    const data = await response.json();
    
    // Use the real request ID from the response
    if (data.request_id && eventSource) {
      eventSource.close();
      connectToStallingMessages(data.request_id);
    }
    
    // Update the UI with search results
    displaySearchResults(data);
    
    return data;
  } catch (error) {
    console.error('Search error:', error);
    
    // Hide loading on error
    if (loadingContainer) {
      loadingContainer.style.display = 'none';
    }
    
    // Close the SSE connection
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    
    throw error;
  }
}

// Update your existing search form submit handler to use this function
if (searchForm) {
  searchForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const query = document.getElementById('search-input').value;
    if (query.trim()) {
      await performSearch(query);
    }
  });
}

// Add this function to your existing JavaScript
// or update your existing function that displays search results
function displaySearchResults(data) {
  // Hide loading when results are displayed
  if (loadingContainer) {
    loadingContainer.style.display = 'none';
  }
  
  // Close the SSE connection
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  
  // Your existing code to display search results...
}