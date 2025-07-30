document.querySelectorAll(
    '#ac-Overlay,#ac-notice,.privacy-cp-wall,.bck-adblock,.tp-modal'
).forEach(el => el.remove())

// Remove the has--adblock class from the html tag element
document.querySelector('html').classList.remove('has--adblock')
