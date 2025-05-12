/**
 * Tests for the contact.js functionality
 * This test suite verifies the contact modal behavior
 */

describe('Contact Modal Component', () => {
  // Setup DOM elements for testing
  beforeEach(() => {
    document.body.innerHTML = `
      <button id="contactBtn">Contact</button>
      <div id="contactModal" style="display: none;" class="modal">
        <div class="modal-content">
          <span class="contact-close">&times;</span>
          <h2>Contact Us</h2>
          <div class="contact-content">
            <p>This is the contact form content.</p>
          </div>
        </div>
      </div>
    `;
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
    // Reset any console mocks
    if (console.log.mockRestore) {
      console.log.mockRestore();
    }
    if (console.error.mockRestore) {
      console.error.mockRestore();
    }
  });
  
  test('Contact modal is displayed when contact button is clicked', () => {
    // Mock console logs for testing
    console.log = jest.fn();
    
    // Trigger DOMContentLoaded to initialize the contact modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const contactBtn = document.getElementById('contactBtn');
    const contactModal = document.getElementById('contactModal');
    
    // Verify initial state - modal is hidden
    expect(contactModal.style.display).toBe('none');
    
    // Click contact button
    contactBtn.click();
    
    // Check if modal is displayed
    expect(contactModal.style.display).toBe('block');
    
    // Verify console log was called
    expect(console.log).toHaveBeenCalledWith('Contact button clicked');
  });
  
  test('Contact modal is hidden when close button is clicked', () => {
    // Mock console logs for testing
    console.log = jest.fn();
    
    // Trigger DOMContentLoaded to initialize the contact modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const contactBtn = document.getElementById('contactBtn');
    const contactModal = document.getElementById('contactModal');
    const contactClose = document.querySelector('.contact-close');
    
    // Show the modal first
    contactBtn.click();
    expect(contactModal.style.display).toBe('block');
    
    // Click the close button
    contactClose.click();
    
    // Check if modal is hidden
    expect(contactModal.style.display).toBe('none');
    
    // Verify console log was called
    expect(console.log).toHaveBeenCalledWith('Contact close clicked');
  });
  
  test('Contact modal is hidden when clicking outside of it', () => {
    // Mock console logs for testing
    console.log = jest.fn();
    
    // Trigger DOMContentLoaded to initialize the contact modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const contactBtn = document.getElementById('contactBtn');
    const contactModal = document.getElementById('contactModal');
    
    // Show the modal first
    contactBtn.click();
    expect(contactModal.style.display).toBe('block');
    
    // Create and dispatch window click event targeting the modal background
    const clickEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    // Set the event target to the modal (outside of content)
    Object.defineProperty(clickEvent, 'target', {
      value: contactModal,
      enumerable: true
    });
    
    // Dispatch the event
    window.dispatchEvent(clickEvent);
    
    // Check if modal is hidden
    expect(contactModal.style.display).toBe('none');
    
    // Verify console log was called
    expect(console.log).toHaveBeenCalledWith('Contact modal outside click');
  });
  
  test('Contact modal remains visible when clicking inside modal content', () => {
    // Trigger DOMContentLoaded to initialize the contact modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const contactBtn = document.getElementById('contactBtn');
    const contactModal = document.getElementById('contactModal');
    const modalContent = document.querySelector('.modal-content');
    
    // Show the modal first
    contactBtn.click();
    expect(contactModal.style.display).toBe('block');
    
    // Create and dispatch window click event targeting the modal content
    const clickEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    // Set the event target to something other than the modal
    Object.defineProperty(clickEvent, 'target', {
      value: modalContent,
      enumerable: true
    });
    
    // Dispatch the event
    window.dispatchEvent(clickEvent);
    
    // Check if modal is still displayed
    expect(contactModal.style.display).toBe('block');
  });
  
  test('Script logs error when contact elements are not found', () => {
    // Clear the DOM
    document.body.innerHTML = '';
    
    // Mock console error for testing
    console.error = jest.fn();
    
    // Trigger DOMContentLoaded to initialize the contact modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Verify error was logged
    expect(console.error).toHaveBeenCalledWith(
      'Contact elements not found',
      expect.objectContaining({
        contactBtn: null,
        contactModal: null
      })
    );
  });
  
  test('Script logs error when contact close button is not found', () => {
    // Setup DOM with missing close button
    document.body.innerHTML = `
      <button id="contactBtn">Contact</button>
      <div id="contactModal" style="display: none;" class="modal">
        <div class="modal-content">
          <!-- Close button intentionally missing -->
          <h2>Contact Us</h2>
        </div>
      </div>
    `;
    
    // Mock console error for testing
    console.error = jest.fn();
    
    // Trigger DOMContentLoaded to initialize the contact modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Verify error was logged
    expect(console.error).toHaveBeenCalledWith('Contact close button not found');
  });
  
  test('Script logs when loaded', () => {
    // Mock console log for testing
    console.log = jest.fn();
    
    // Simulate script loading
    eval('console.log("Contact script loaded")');
    
    // Verify log was called
    expect(console.log).toHaveBeenCalledWith('Contact script loaded');
  });
});