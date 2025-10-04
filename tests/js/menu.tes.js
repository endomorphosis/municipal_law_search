
/**
 * Tests for the menu.js functionality
 * This test suite verifies the dropdown menu behavior
 */

describe('Menu Dropdown Component', () => {
  // Setup DOM elements for testing
  beforeEach(() => {
    document.body.innerHTML = `
      <button id="menuToggleBtn" aria-label="Menu">
        <i class="fas fa-bars"></i>
      </button>
      <div id="menuDropdown" class="menu-dropdown hidden">
        <button>Item 1</button>
        <button>Item 2</button>
        <button>Item 3</button>
      </div>
    `;
  });
  
  // Clean up after each test
  afterEach(() => {
    document.body.innerHTML = '';
  });
  
  test('Menu toggle button shows dropdown when clicked', () => {
    // Trigger DOMContentLoaded to initialize the menu
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const menuToggleBtn = document.getElementById('menuToggleBtn');
    const menuDropdown = document.getElementById('menuDropdown');
    
    // Verify initial state - menu is hidden
    expect(menuDropdown.classList).toContain('hidden');
    
    // Click menu button
    menuToggleBtn.click();
    
    // Check if hidden class was removed
    expect(menuDropdown.classList).not.toContain('hidden');
    
    // Click again to hide
    menuToggleBtn.click();
    
    // Check if hidden class was added back
    expect(menuDropdown.classList).toContain('hidden');
  });
  
  test('Dropdown is hidden when clicking outside of menu', () => {
    // Trigger DOMContentLoaded to initialize the menu
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const menuToggleBtn = document.getElementById('menuToggleBtn');
    const menuDropdown = document.getElementById('menuDropdown');
    
    // Show dropdown
    menuToggleBtn.click();
    expect(menuDropdown.classList).not.toContain('hidden');
    
    // Click elsewhere in the document (outside menu)
    document.dispatchEvent(new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    }));
    
    // Check if dropdown is hidden again
    expect(menuDropdown.classList).toContain('hidden');
  });
  
  test('Clicking on a menu item hides the dropdown', () => {
    // Trigger DOMContentLoaded to initialize the menu
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Get references to elements
    const menuToggleBtn = document.getElementById('menuToggleBtn');
    const menuDropdown = document.getElementById('menuDropdown');
    const menuItems = document.querySelectorAll('#menuDropdown button');
    
    // Show dropdown
    menuToggleBtn.click();
    expect(menuDropdown.classList).not.toContain('hidden');
    
    // Click on first menu item
    menuItems[0].click();
    
    // Check if dropdown is hidden
    expect(menuDropdown.classList).toContain('hidden');
  });
  
  test('Event propagation is stopped when clicking menu button', () => {
    // Trigger DOMContentLoaded to initialize the menu
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Set up document click handler to check propagation
    const documentClickHandler = jest.fn();
    document.addEventListener('click', documentClickHandler);
    
    // Get reference to menu button
    const menuToggleBtn = document.getElementById('menuToggleBtn');
    
    // Create a click event with bubbling enabled
    const clickEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    // Stop propagation spy
    const stopPropagationSpy = jest.spyOn(clickEvent, 'stopPropagation');
    
    // Dispatch click event on menu button
    menuToggleBtn.dispatchEvent(clickEvent);
    
    // Verify stopPropagation was called
    expect(stopPropagationSpy).toHaveBeenCalled();
    
    // Clean up
    document.removeEventListener('click', documentClickHandler);
    stopPropagationSpy.mockRestore();
  });
});