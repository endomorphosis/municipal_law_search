/**
 * Tests for the ourteam.js functionality
 * This test suite verifies the Our Team modal behavior
 */

describe('Our Team Modal Component', () => {
  // Setup DOM elements for testing
  beforeEach(() => {
    document.body.innerHTML = `
      <button id="ourTeamBtn">Our Team</button>
      <div id="ourTeamModal" style="display: none;" class="modal">
        <div class="modal-content">
          <span class="ourteam-close">&times;</span>
          <h2>Our Team</h2>
          <div class="ourteam-content">
            <p>This is the Our Team content.</p>
          </div>
        </div>
      </div>
    `;
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
  });
  
  test('Our Team modal is displayed when Our Team button is clicked', () => {
    // Trigger DOMContentLoaded to initialize the Our Team modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const ourTeamBtn = document.getElementById('ourTeamBtn');
    const ourTeamModal = document.getElementById('ourTeamModal');
    
    // Verify initial state - modal is hidden
    expect(ourTeamModal.style.display).toBe('none');
    
    // Click Our Team button
    ourTeamBtn.click();
    
    // Check if modal is displayed
    expect(ourTeamModal.style.display).toBe('block');
  });
  
  test('Our Team modal is hidden when close button is clicked', () => {
    // Trigger DOMContentLoaded to initialize the Our Team modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const ourTeamBtn = document.getElementById('ourTeamBtn');
    const ourTeamModal = document.getElementById('ourTeamModal');
    const ourTeamClose = document.querySelector('.ourteam-close');
    
    // Show the modal first
    ourTeamBtn.click();
    expect(ourTeamModal.style.display).toBe('block');
    
    // Click the close button
    ourTeamClose.click();
    
    // Check if modal is hidden
    expect(ourTeamModal.style.display).toBe('none');
  });
  
  test('Our Team modal is hidden when clicking outside of it', () => {
    // Trigger DOMContentLoaded to initialize the Our Team modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const ourTeamBtn = document.getElementById('ourTeamBtn');
    const ourTeamModal = document.getElementById('ourTeamModal');
    
    // Show the modal first
    ourTeamBtn.click();
    expect(ourTeamModal.style.display).toBe('block');
    
    // Create and dispatch window click event targeting the modal background
    const clickEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    // Set the event target to the modal (outside of content)
    Object.defineProperty(clickEvent, 'target', {
      value: ourTeamModal,
      enumerable: true
    });
    
    // Dispatch the event
    window.dispatchEvent(clickEvent);
    
    // Check if modal is hidden
    expect(ourTeamModal.style.display).toBe('none');
  });
  
  test('Our Team modal remains visible when clicking inside modal content', () => {
    // Trigger DOMContentLoaded to initialize the Our Team modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const ourTeamBtn = document.getElementById('ourTeamBtn');
    const ourTeamModal = document.getElementById('ourTeamModal');
    const modalContent = document.querySelector('.modal-content');
    
    // Show the modal first
    ourTeamBtn.click();
    expect(ourTeamModal.style.display).toBe('block');
    
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
    expect(ourTeamModal.style.display).toBe('block');
  });
  
  test('Modal events have correct behavior when elements are properly set up', () => {
    // Mock the global window object methods
    const originalAddEventListener = window.addEventListener;
    window.addEventListener = jest.fn(originalAddEventListener);
    
    // Trigger DOMContentLoaded to initialize the Our Team modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Verify window event listener for clicks was added
    expect(window.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
    
    // Restore the original window method
    window.addEventListener = originalAddEventListener;
  });
  
  test('Modal responds to window click events correctly', () => {
    // Trigger DOMContentLoaded to initialize the Our Team modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const ourTeamBtn = document.getElementById('ourTeamBtn');
    const ourTeamModal = document.getElementById('ourTeamModal');
    
    // Show the modal first
    ourTeamBtn.click();
    expect(ourTeamModal.style.display).toBe('block');
    
    // Create window click event mocks for different targets
    const outsideClickEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    Object.defineProperty(outsideClickEvent, 'target', {
      value: document.body, // Click somewhere else in the document
      enumerable: true
    });
    
    // Dispatch the outside click event
    window.dispatchEvent(outsideClickEvent);
    
    // Check if modal is hidden
    expect(ourTeamModal.style.display).toBe('none');
  });
});