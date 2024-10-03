<script>
  // Function to handle scroll events
  function handleScroll() {
    const topnav = document.querySelector('.topnav');
    const hero = document.querySelector('.hero');
    const heroHeight = hero.offsetHeight;

    // Check if scrolled past the hero section
    if (window.scrollY > heroHeight) {
      topnav.classList.add('black-background');
    } else {
      topnav.classList.remove('black-background');
    }
  }

  // Add event listener for scroll events
  window.addEventListener('scroll', handleScroll);
</script>