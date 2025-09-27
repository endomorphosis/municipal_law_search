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

// Contact Form submission handling. Backend function is in app.py under async def contact()
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the default form submission
            
            const submitBtn = document.getElementById('submit-btn');
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData.entries());

            // Disable button to prevent multiple submissions
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';

            fetch('/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(result => {
                console.log('Success:', result);
                alert('Message sent successfully!');
                document.getElementById('contactModal').style.display = 'none'; // Close modal on success
                contactForm.reset(); // Reset form fields
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to send message. Please try again.');
            })
            .finally(() => {
                // Re-enable button
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit';
            });
        });
    } else {
        console.error('Contact form not found');
    }
});


// Log when the script is loaded
console.log('Contact script loaded');
