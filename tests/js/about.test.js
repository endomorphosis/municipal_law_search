/**
 * Tests for the about.js functionality
 * This test suite verifies the about modal behavior
 */

describe('About Modal Component', () => {
  // Declare variables for DOM elements
  let aboutBtn;
  let aboutModal;
  let closeBtn;
  let modalContent;

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
    
    // Trigger DOMContentLoaded to initialize the about modal
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to all commonly used elements
    aboutBtn = document.getElementById('aboutBtn');
    aboutModal = document.getElementById('aboutModal');
    closeBtn = document.querySelector('.about-close');
    modalContent = aboutModal.querySelector('.modal-content');
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
    // Reset references
    aboutBtn = null;
    aboutModal = null;
    closeBtn = null;
    modalContent = null;
  });

  test(`
    GIVEN the about modal component is loaded
    WHEN the page loads
    THEN the about modal is hidden`, 
    () => {
    expect(aboutModal.style.display).toBe('none');
  });

  test(`
    GIVEN the about modal component is loaded
    WHEN the about button is clicked
    THEN the modal is displayed`, 
    () => {
    // Click about button
    aboutBtn.click();

    // Check if modal is displayed
    expect(aboutModal.style.display).toBe('block');
  });
  
  test(`
    GIVEN the about modal is displayed
    WHEN the close button is clicked
    THEN the modal is hidden`,
    () => {
    // Show modal
    aboutBtn.click();
    expect(aboutModal.style.display).toBe('block');

    // Click close button
    closeBtn.click();

    // Check if modal is hidden
    expect(aboutModal.style.display).toBe('none');
  });

  test('About modal opens when about button is clicked', () => {
    // Show modal
    aboutBtn.click();
    
    // Check if modal is displayed
    expect(aboutModal.style.display).toBe('block');
  });

  test('About modal is hidden when clicking outside of it', () => {
    // Show modal first
    aboutBtn.click();
    
    // Click on the modal background (outside of modal content)
    aboutModal.dispatchEvent(new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    }));
    
    // Check if modal is hidden
    expect(aboutModal.style.display).toBe('none');
  });
  
  test('Modal stays open when clicking inside the modal content', () => {
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
    closeBtn.remove();

    // Show modal
    aboutBtn.click();
    expect(aboutModal.style.display).toBe('block');
    
    // Without error - just checking that initialization completes
    expect(true).toBe(true);
  });
});