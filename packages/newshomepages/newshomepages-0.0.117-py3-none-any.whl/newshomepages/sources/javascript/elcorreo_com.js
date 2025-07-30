const firstDiv = document.querySelector('div');
if (firstDiv.innerHTML === '') {
  firstDiv.remove();
}

document.querySelectorAll(
  '.v-adv'
).forEach(el => el.remove())
