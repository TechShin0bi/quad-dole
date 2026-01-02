// Product Detail Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Function to change the main product image when a thumbnail is clicked
    function changeMainImage(src, alt) {
        const mainImg = document.getElementById('main-image');
        if (mainImg) {
            // Add fade out effect
            mainImg.style.opacity = '0';
            
            // Change image after fade out
            setTimeout(() => {
                mainImg.src = src;
                mainImg.alt = alt;
                // Fade back in
                mainImg.style.opacity = '1';
            }, 150);
        }
    }

    // Make the function available globally
    window.changeMainImage = changeMainImage;

    // Initialize any other product detail related JavaScript here
});
