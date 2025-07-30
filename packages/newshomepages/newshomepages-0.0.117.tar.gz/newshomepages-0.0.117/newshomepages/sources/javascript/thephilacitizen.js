// Loop through all elements in the document
// and remove any with a z-index over 9999
document.querySelectorAll('*').forEach(el => {
  if (window.getComputedStyle(el).zIndex > 9999) {
    el.remove()
  }
})
