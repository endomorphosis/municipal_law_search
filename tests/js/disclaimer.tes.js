/**
 * Tests for the disclaimer.js functionality
 * This test suite verifies the disclaimer modal behavior
 */

describe('Disclaimer Modal Component', () => {
  // Setup DOM elements for testing
  beforeEach(() => {
    document.body.innerHTML = `
      <button id="disclaimerBtn">Disclaimer</button>
      <div id="disclaimerModal" style="display: none;" class="modal">
        <div class="modal-content">
          <span class="disclaimer-close">&times;</span>
          <h2>Disclaimer</h2>
          <div class="disclaimer-content">
            <p>This is the disclaimer content.</p>
          </div>
        </div>
      </div>
    `;
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
  });
  
  test('Disclaimer modal is displayed when disclaimer button is clicked', () => {
    // Trigger DOMContentLoaded to initialize the disclaimer modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const disclaimerBtn = document.getElementById('disclaimerBtn');
    const disclaimerModal = document.getElementById('disclaimerModal');
    
    // Verify initial state - modal is hidden
    expect(disclaimerModal.style.display).toBe('none');
    
    // Click disclaimer button
    disclaimerBtn.click();
    
    // Check if modal is displayed
    expect(disclaimerModal.style.display).toBe('block');
  });
  
  test('Disclaimer modal is hidden when close button is clicked', () => {
    // Trigger DOMContentLoaded to initialize the disclaimer modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const disclaimerBtn = document.getElementById('disclaimerBtn');
    const disclaimerModal = document.getElementById('disclaimerModal');
    const disclaimerClose = document.querySelector('.disclaimer-close');
    
    // Show the modal first
    disclaimerBtn.click();
    expect(disclaimerModal.style.display).toBe('block');
    
    // Click the close button
    disclaimerClose.click();
    
    // Check if modal is hidden
    expect(disclaimerModal.style.display).toBe('none');
  });
  
  test('Disclaimer modal is hidden when clicking outside of it', () => {
    // Trigger DOMContentLoaded to initialize the disclaimer modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const disclaimerBtn = document.getElementById('disclaimerBtn');
    const disclaimerModal = document.getElementById('disclaimerModal');
    
    // Show the modal first
    disclaimerBtn.click();
    expect(disclaimerModal.style.display).toBe('block');
    
    // Create and dispatch window click event targeting the modal background
    const clickEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    // Set the event target to the modal (outside of content)
    Object.defineProperty(clickEvent, 'target', {
      value: disclaimerModal,
      enumerable: true
    });
    
    // Dispatch the event
    window.dispatchEvent(clickEvent);
    
    // Check if modal is hidden
    expect(disclaimerModal.style.display).toBe('none');
  });
  
  test('Disclaimer modal remains visible when clicking inside modal content', () => {
    // Trigger DOMContentLoaded to initialize the disclaimer modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const disclaimerBtn = document.getElementById('disclaimerBtn');
    const disclaimerModal = document.getElementById('disclaimerModal');
    const modalContent = document.querySelector('.modal-content');
    
    // Show the modal first
    disclaimerBtn.click();
    expect(disclaimerModal.style.display).toBe('block');
    
    // Create and dispatch window click event targeting the modal content
    const clickEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    // Set the event target to the modal content
    Object.defineProperty(clickEvent, 'target', {
      value: modalContent,
      enumerable: true
    });
    
    // Dispatch the event
    window.dispatchEvent(clickEvent);
    
    // Check if modal is still displayed
    expect(disclaimerModal.style.display).toBe('block');
  });
});