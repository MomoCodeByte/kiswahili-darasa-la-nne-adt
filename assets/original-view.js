(() => {
  const pageMatch = document.querySelector('meta[name="title-id"]')?.content.match(/^pg(\d{3})_/);
  if (!pageMatch || document.querySelector('#original-view-link')) return;

  const pageNumber = Number(pageMatch[1]);
  const originalLayer = document.createElement('section');
  originalLayer.id = 'original-page-layer';
  originalLayer.setAttribute('aria-label', `Ukurasa wa ${pageNumber} kama ulivyo kwenye PDF asili`);
  originalLayer.hidden = true;
  Object.assign(originalLayer.style, {
    position: 'fixed', inset: '0 0 4.5rem 0', zIndex: '40', overflow: 'auto',
    padding: '1rem', background: '#e5e7eb', textAlign: 'center'
  });

  const pageImage = document.createElement('img');
  pageImage.src = `images/original-pages/pg${pageMatch[1]}.jpg`;
  pageImage.alt = `Ukurasa wa ${pageNumber} wa kitabu asili`;
  Object.assign(pageImage.style, {
    display: 'block', width: 'min(100%, 760px)', height: 'auto', margin: '0 auto',
    background: '#fff', boxShadow: '0 8px 30px #0003'
  });
  originalLayer.appendChild(pageImage);
  document.body.appendChild(originalLayer);

  const link = document.createElement('a');
  link.id = 'original-view-link';
  link.href = `original-book.html#page=${pageNumber}`;
  link.textContent = 'Tazama ukurasa wa PDF asili';
  link.setAttribute('aria-label', `Tazama ukurasa wa ${pageNumber} kama ulivyo kwenye PDF asili ndani ya ADT`);
  Object.assign(link.style, {
    position: 'fixed', right: '1rem', top: '1rem', zIndex: '60',
    padding: '.6rem .85rem', borderRadius: '.65rem', background: '#172554',
    color: '#fff', fontFamily: 'Atkinson Hyperlegible, Arial, sans-serif',
    fontWeight: '700', textDecoration: 'none', boxShadow: '0 3px 12px #0004'
  });
  link.addEventListener('click', (event) => {
    event.preventDefault();
    const showingOriginal = originalLayer.hidden;
    originalLayer.hidden = !showingOriginal;
    link.textContent = showingOriginal ? 'Rudi toleo shirikishi' : 'Tazama ukurasa wa PDF asili';
    link.setAttribute('aria-pressed', String(showingOriginal));
    document.documentElement.style.overflow = showingOriginal ? 'hidden' : '';
    if (showingOriginal) originalLayer.scrollTop = 0;
  });
  document.body.appendChild(link);
})();
