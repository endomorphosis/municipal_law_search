// Menu dropdown functionality
document.addEventListener('DOMContentLoaded', function() {
    const menuToggleBtn = document.getElementById('menuToggleBtn');
    const menuDropdown = document.getElementById('menuDropdown');
    
    console.log('Menu initialization', menuToggleBtn, menuDropdown); // Debug log

    // Toggle dropdown when menu button is clicked
    if (menuToggleBtn && menuDropdown) {
        menuToggleBtn.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent event bubbling
            menuDropdown.classList.toggle('hidden');
            console.log('Menu clicked, toggle hidden class');
        });
        
        // Close dropdown when clicking outside of it
        document.addEventListener('click', function(event) {
            if (!menuToggleBtn.contains(event.target) && !menuDropdown.contains(event.target)) {
                menuDropdown.classList.add('hidden');
            }
        });
        
        // Close dropdown when clicking on menu items
        const menuItems = document.querySelectorAll('#menuDropdown button');
        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                menuDropdown.classList.add('hidden');
            });
        });
    } else {
        console.error('Menu elements not found!');
    }
});