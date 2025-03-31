// Disclaimer Modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const disclaimerBtn = document.getElementById('disclaimerBtn');
    const disclaimerModal = document.getElementById('disclaimerModal');
    const disclaimerClose = document.querySelector('.disclaimer-close');
    
    // Open modal when disclaimer button is clicked
    disclaimerBtn.addEventListener('click', function() {
        disclaimerModal.style.display = 'block';
    });
    
    // Close modal when X is clicked
    disclaimerClose.addEventListener('click', function() {
        disclaimerModal.style.display = 'none';
    });
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === disclaimerModal) {
            disclaimerModal.style.display = 'none';
        }
    });
});
