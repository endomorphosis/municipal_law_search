
// Disclaimer Modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const ourTeamBtn = document.getElementById('ourTeamBtn');
    const ourTeamModal = document.getElementById('ourTeamModal');
    const ourTeamClose = document.querySelector('.ourteam-close');
    
    // Open modal when disclaimer button is clicked
    ourTeamBtn.addEventListener('click', function() {
        ourTeamModal.style.display = 'block';
    });
    
    // Close modal when X is clicked
    ourTeamClose.addEventListener('click', function() {
        ourTeamModal.style.display = 'none';
    });
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === ourTeamModal) {
            ourTeamModal.style.display = 'none';
        }
    });
});
