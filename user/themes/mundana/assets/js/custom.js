/* Custom js code for theme */

$(document).ready(function() {
    function adjustBannerHeight() {
        // if match media lg
        var ref = $('.banner-ref');
        if (ref.length === 0) {
            ref = $('#MagicMenu');
        }

        var banner = $('.banner');

        if (ref.length && banner.length) {
            var refBottom = ref.offset().top + ref.outerHeight();
            banner.height(refBottom);
        }
    }

    if ($('.banner').length) {
        // Adjust the height initially
        adjustBannerHeight();
        $('.banner').removeClass('d-none');
        // Adjust the height on window resize
        $(window).resize(adjustBannerHeight);
    }
});

