const firstDiv = document.querySelector('div');
if (firstDiv.innerHTML === '') {
  firstDiv.remove();
}

document.querySelectorAll(
  '.v-adv,.voc-container-fw,.voc-container--bg-color'
).forEach(el => el.remove())
