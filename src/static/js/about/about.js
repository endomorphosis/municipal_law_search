// About Modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const aboutBtn = document.getElementById('aboutBtn');
    const aboutModal = document.getElementById('aboutModal');
    const aboutClose = document.querySelector('.about-close');

    // Open modal when about button is clicked
    aboutBtn.addEventListener('click', function() {
        aboutModal.style.display = 'block';
    });
    
    // Close modal when X is clicked
    if (aboutClose) {
        aboutClose.addEventListener('click', function() {
            aboutModal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === aboutModal) {
            aboutModal.style.display = 'none';
        }
    });
});
