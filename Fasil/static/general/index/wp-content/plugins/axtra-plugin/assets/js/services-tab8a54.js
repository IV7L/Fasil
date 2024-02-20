(function($) {
	
	"use strict";
	var testimonial_slider_js = function($scope, $) {
		let device_width = window.innerWidth;
		if (device_width > 1200) {
			gsap.to(".service__list-6", {
			  scrollTrigger: {
				trigger: ".service__area-6",
				pin: ".service__list-6",
				pinSpacing: true,
				start: "top top",
				end: "bottom bottom"
			  }
			})
		
			gsap.to(".service__image-wrap", {
			  scrollTrigger: {
				trigger: ".service__area-6",
				pin: ".mid-content",
				pinSpacing: true,
				start: "top top",
				end: "bottom bottom",
				markers: false
			  }
			})
		
			let service_images = gsap.utils.toArray(".service__image")
			let service_imagess = gsap.utils.toArray(".service__image img")
			let service_items = gsap.utils.toArray(".service__item-6")
		
			if (service_items) {
			  service_items.forEach((image, i) => {
				console.log(service_images[i].img)
				let tl = gsap.timeline({
				  scrollTrigger: {
					trigger: image,
					scrub: 1,
					start: "top top-=600",
					markers: false,
				  }
				});
				tl.to(service_images[i], {
				  zIndex: "1",
				})
				tl.to(service_imagess[i], {
				  opacity: 0,
				  duration: 1,
				  scale: 1.2,
				  ease: "power4.out"
				}, "-=1")
			  })
			}
		
			let navItems = gsap.utils.toArray(".service__list-6 li a")
			if (navItems) {
			  navItems.forEach((nav) => {
				nav.addEventListener("click", (e) => {
				  e.preventDefault();
				  const ids = nav.getAttribute("href")
				  gsap.to(window, { duration: 0.5, scrollTo: ids, ease: "power4.out" });
				})
			  })
			}
		
			// Active Nav
			$(document).on('scroll', function () {
			  $('.service__item-6').each(function () {
				if ($(this).position().top <= $(document).scrollTop() && ($(this).position().top + $(this).outerHeight()) > $(document).scrollTop()) {
				  var sec_id = $(this).data('secid');
		
				  $('.service__list-6 li:nth-child(' + sec_id + ')').addClass('active').siblings().removeClass('active');
				}
			  });
			});
		  }
		
	};
	$(window).on('elementor/frontend/init', function () {
            elementorFrontend.hooks.addAction('frontend/element_ready/axtra_service_tabs.default', testimonial_slider_js);
    });	

})(window.jQuery);