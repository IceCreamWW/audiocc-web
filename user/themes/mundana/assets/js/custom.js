/* Custom js code for theme */


$(document).ready(function() {
    function adjustBannerHeight() {
        // if match media lg
        if (window.matchMedia('(min-width: 992px)').matches)
            var ref = $('#intro'); // Replace with your image element's ID
        else
            var ref = $('#carouselIntroIndicators'); // Replace with your image element's ID
        var banner = $('#homeBanner'); // Replace with your background element's ID

        if (ref.length && banner.length) {
            var refBottom = ref.offset().top + ref.outerHeight();
            banner.height(refBottom);
        }
    }

    // Adjust the height initially
    adjustBannerHeight();

    // Adjust the height on window resize
    $(window).resize(adjustBannerHeight);
});

