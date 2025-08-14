const img = document.getElementById('pokeImg');
const btnSprite  = document.getElementById('btnSprite');
const btnArtwork = document.getElementById('btnArtwork');

if (img && btnSprite && btnArtwork) {
  function setActive(btn, active){ btn.classList.toggle('active', active); }

  function showSprite(){
    const src = img.dataset.sprite;
    if (!src) return;
    img.src = src;
    img.classList.add('pixelated');
    setActive(btnSprite, true);
    setActive(btnArtwork, false);
  }

  function showArtwork(){
    const src = img.dataset.artwork || img.dataset.sprite || '';
    if (!src) return;
    img.src = src;
    img.classList.remove('pixelated');
    setActive(btnSprite, false);
    setActive(btnArtwork, true);
  }

  // Estado inicial
  if (img.dataset.sprite) { showSprite(); } else { showArtwork(); }

  btnSprite.addEventListener('click', showSprite);
  btnArtwork.addEventListener('click', showArtwork);
}
