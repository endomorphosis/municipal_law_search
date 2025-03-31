// Contact Modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const contactBtn = document.getElementById('contactBtn');
    const contactModal = document.getElementById('contactModal');
    const contactClose = document.querySelector('.contact-close');
    
    console.log('Contact modal initialization', contactBtn, contactModal, contactClose); // Debug log
    
    // Open modal when contact button is clicked
    if (contactBtn && contactModal) {
        contactBtn.addEventListener('click', function() {
            console.log('Contact button clicked');
            contactModal.style.display = 'block';
        });
        
        // Close modal when X is clicked
        if (contactClose) {
            contactClose.addEventListener('click', function() {
                console.log('Contact close clicked');
                contactModal.style.display = 'none';
            });
        } else {
            console.error('Contact close button not found');
        }
        
        // Close modal when clicking outside of it
        window.addEventListener('click', function(event) {
            if (event.target === contactModal) {
                console.log('Contact modal outside click');
                contactModal.style.display = 'none';
            }
        });
    } else {
        console.error('Contact elements not found', { contactBtn, contactModal });
    }
});

// Log when the script is loaded
console.log('Contact script loaded');
