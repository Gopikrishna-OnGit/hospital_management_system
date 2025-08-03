// Initialize AOS animations
AOS.init({
    duration: 1000,
    easing: 'ease-in-out',
    once: true,
    mirror: false
  });
  
  // Smooth scroll for anchor links
  document.addEventListener("DOMContentLoaded", function () {
      const links = document.querySelectorAll('a[href^="#"]');
      for (const link of links) {
          link.addEventListener("click", function (e) {
              e.preventDefault();
              document.querySelector(this.getAttribute("href")).scrollIntoView({
                  behavior: "smooth"
              });
          });
      }
  });
  
  // Simple alert fade out after 3 seconds
  setTimeout(function() {
      let alerts = document.querySelectorAll('.alert-success, .alert-error');
      alerts.forEach(alert => {
          alert.style.opacity = "0";
          setTimeout(() => { alert.remove(); }, 1000);
      });
  }, 3000);
  