
/**
 * Tests for the about.js functionality
 * This test suite verifies the about modal behavior
 */

describe('About Modal Component', () => {
  // Setup DOM elements for testing
  beforeEach(() => {
    document.body.innerHTML = `
      <button id="aboutBtn">About</button>
      <div id="aboutModal" style="display: none;" class="modal">
        <div class="modal-content">
          <span class="about-close">&times;</span>
          <h2>About American Law Search</h2>
          <div class="about-content">
            <p>This is the about content.</p>
          </div>
        </div>
      </div>
    `;
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
  });
  
  test('About modal is displayed when about button is clicked', () => {
    // Trigger DOMContentLoaded to initialize the about modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const aboutBtn = document.getElementById('aboutBtn');
    const aboutModal = document.getElementById('aboutModal');
    
    // Verify initial state - modal is hidden
    expect(aboutModal.style.display).toBe('none');
    
    // Click about button
    aboutBtn.click();
    
    // Check if modal is displayed
    expect(aboutModal.style.display).toBe('block');
  });
  
  test('About modal is hidden when close button is clicked', () => {
    // Trigger DOMContentLoaded to initialize the about modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const aboutBtn = document.getElementById('aboutBtn');
    const aboutModal = document.getElementById('aboutModal');
    const closeBtn = document.querySelector('.about-close');
    
    // Show modal
    aboutBtn.click();
    expect(aboutModal.style.display).toBe('block');
    
    // Click close button
    closeBtn.click();
    
    // Check if modal is hidden
    expect(aboutModal.style.display).toBe('none');
  });
  
  test('About modal is hidden when clicking outside of it', () => {
    // Trigger DOMContentLoaded to initialize the about modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const aboutBtn = document.getElementById('aboutBtn');
    const aboutModal = document.getElementById('aboutModal');
    
    // Show modal
    aboutBtn.click();
    expect(aboutModal.style.display).toBe('block');
    
    // Click on the modal background (outside of modal content)
    aboutModal.dispatchEvent(new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    }));
    
    // Check if modal is hidden
    expect(aboutModal.style.display).toBe('none');
  });
  
  test('Modal stays open when clicking inside the modal content', () => {
    // Trigger DOMContentLoaded to initialize the about modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const aboutBtn = document.getElementById('aboutBtn');
    const aboutModal = document.getElementById('aboutModal');
    const modalContent = aboutModal.querySelector('.modal-content');
    
    // Show modal
    aboutBtn.click();
    expect(aboutModal.style.display).toBe('block');
    
    // Click inside modal content
    modalContent.dispatchEvent(new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    }));
    
    // Check if modal is still displayed
    expect(aboutModal.style.display).toBe('block');
  });
  
  test('Modal handles missing close button gracefully', () => {
    // Remove the close button
    document.querySelector('.about-close').remove();
    
    // Trigger DOMContentLoaded to initialize the about modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const aboutBtn = document.getElementById('aboutBtn');
    const aboutModal = document.getElementById('aboutModal');
    
    // Show modal
    aboutBtn.click();
    expect(aboutModal.style.display).toBe('block');
    
    // Without error - just checking that initialization completes
    expect(true).toBe(true);
  });
});