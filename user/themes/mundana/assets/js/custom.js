/* Custom js code for theme */

$(document).ready(function() {

    function adjustMainTop() {
        if (window.matchMedia("(min-width: 1280px)").matches) return;
        var navHeight = $('#MagicMenu').outerHeight() + 10;
        $('main').css('margin-top', navHeight);
    }
    adjustMainTop();

    // Params
    let mainSliderSelector = '.main-slider',
        navSliderSelector = '.nav-slider',
        interleaveOffset = 0.5;

    // Main Slider
    let mainSliderOptions = {
          loop: true,
          speed:1000,
          autoplay:{
            delay:3000
          },
          loopAdditionalSlides: 10,
          grabCursor: true,
          watchSlidesProgress: false,
          navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
          },
          on: {
            beforeSlideChangeStart: function(){
                // get view height
                var img = $('.main-slider').find('img')[this.activeIndex]
                var slideHeight = img.height * .8;
                if (img.width > $(window).width()) {
                    slideHeight = img.height * $(window).width() * .95 / img.width;
                    var slideWidth = $(window).width() * .95;
                    $('.swiper-container').css('width', slideWidth);
                    $('.swiper-wrapper').css('width', slideWidth);
                }
                $('.swiper-container').css('height', slideHeight);
                $('.swiper-wrapper').css('height', slideHeight);

            },
            init: function(){
              this.autoplay.stop();
            },
            imagesReady: function(){
              this.el.classList.remove('loading');
              this.autoplay.start();
            },
            touchStart: function() {
              let swiper = this;
              for (let i = 0; i < swiper.slides.length; i++) {
                swiper.slides[i].style.transition = "";
              }
            },
            setTransition: function(speed) {
              let swiper = this;
              for (let i = 0; i < swiper.slides.length; i++) {
                swiper.slides[i].style.transition = speed + "ms";
                swiper.slides[i].querySelector(".slide-bgimg").style.transition =
                  speed + "ms";
              }
            }
          }
        };
    let mainSlider = new Swiper(mainSliderSelector, mainSliderOptions);

    // Navigation Slider
    let navSliderOptions = {
          loop: true,
          loopAdditionalSlides: 10,
          speed:1000,
          spaceBetween: 5,
          slidesPerView: 5,
          centeredSlides : true,
          touchRatio: 0.2,
          slideToClickedSlide: true,
          direction: 'vertical',
          on: {
            imagesReady: function(){
              this.el.classList.remove('loading');
            },
            click: function(){
              mainSlider.autoplay.stop();
            }
          }
        };
    let navSlider = new Swiper(navSliderSelector, navSliderOptions);

    // Matching sliders
    mainSlider.controller.control = navSlider;
    navSlider.controller.control = mainSlider;

});

