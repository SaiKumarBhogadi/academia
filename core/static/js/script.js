document.addEventListener('DOMContentLoaded', function() {
    const wrapper = document.querySelector('.is-testimonials-wrapper');
    const cards = document.querySelectorAll('.is-testimonial-card');
    const dotsContainer = document.querySelector('.is-testimonials-dots');
    let currentIndex = 0;
    const totalCards = cards.length;

    // Function to calculate cards per view based on screen size
    function getCardsPerView() {
        return window.innerWidth <= 768 ? 1 : 2; // 1 card on mobile, 2 on larger screens
    }

    let cardsPerView = getCardsPerView();
    let totalSlides = Math.ceil(totalCards / cardsPerView);

    // Dynamically generate dots based on the number of slides
    function generateDots() {
        dotsContainer.innerHTML = ''; // Clear existing dots
        totalSlides = Math.ceil(totalCards / cardsPerView);
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('span');
            dot.classList.add('is-testimonial-dot');
            if (i === 0) dot.classList.add('active');
            dotsContainer.appendChild(dot);
        }
    }

    // Initial dot generation
    generateDots();

    function showSlide(index) {
        // Ensure the index stays within bounds
        if (index >= totalSlides) {
            currentIndex = 0;
        } else if (index < 0) {
            currentIndex = totalSlides - 1;
        } else {
            currentIndex = index;
        }

        // Calculate the transform percentage based on cards per view
        const translateX = -(currentIndex * (100 / cardsPerView));
        wrapper.style.transform = `translateX(${translateX}%)`;

        // Update active dot
        const dots = document.querySelectorAll('.is-testimonial-dot');
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === currentIndex);
        });
    }

    // Event listeners for dots
    function setupDotListeners() {
        const dots = document.querySelectorAll('.is-testimonial-dot');
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                showSlide(index);
            });
        });
    }

    // Initial setup
    setupDotListeners();

    // Auto-slide every 5 seconds
    setInterval(() => {
        showSlide(currentIndex + 1);
    }, 5000);

    // Handle window resize to adjust cards per view
    window.addEventListener('resize', () => {
        const newCardsPerView = getCardsPerView();
        if (newCardsPerView !== cardsPerView) {
            cardsPerView = newCardsPerView;
            generateDots(); // Regenerate dots based on new cards per view
            setupDotListeners(); // Reattach event listeners
            showSlide(currentIndex); // Recalculate slide position on resize
        }
    });
});