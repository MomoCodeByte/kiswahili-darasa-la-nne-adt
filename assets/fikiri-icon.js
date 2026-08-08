(() => {
  const fikiriPages = new Map([
    ['pg007_n0030', 7], ['pg015_n0013', 15], ['pg028_n0029', 28],
    ['pg038_n0012', 38], ['pg047_n0014', 47], ['pg059_n0015', 59],
    ['pg067_n0011', 67], ['pg073_n0010', 73], ['pg082_n0044', 82],
    ['pg100_n0012', 100], ['pg110_n0028', 110], ['pg118_n0011', 118],
    ['pg128_n0009', 128]
  ]);

  for (const [id, page] of fikiriPages) {
    const label = document.querySelector(`[data-id="${id}"]`);
    if (!label || label.dataset.fikiriIconApplied === 'true') continue;
    label.dataset.fikiriIconApplied = 'true';

    const imagePath = `images/fikiri/pg${String(page).padStart(3, '0')}_fikiri.png?v=3`;

    if (label.classList.contains('sr-only')) {
      const originalLabel = document.createElement('img');
      originalLabel.src = imagePath;
      originalLabel.alt = '';
      originalLabel.setAttribute('aria-hidden', 'true');
      Object.assign(originalLabel.style, {
        display: 'block', width: 'auto', height: '45px', marginBottom: '.5rem'
      });
      label.insertAdjacentElement('afterend', originalLabel);
      continue;
    }

    const parent = label.parentElement;
    if (parent && parent.textContent.trim() === 'Fikiri') {
      Object.assign(parent.style, {
        background: 'transparent', border: '0', boxShadow: 'none',
        padding: '0', width: 'fit-content', minHeight: '0'
      });
    }

    label.style.backgroundImage = `url("${imagePath}")`;
    label.style.backgroundRepeat = 'no-repeat';
    label.style.backgroundPosition = 'left top';
    label.style.backgroundSize = 'auto 45px';
    label.style.backgroundColor = 'transparent';
    label.style.color = 'transparent';
    label.style.fontSize = '0';
    label.style.lineHeight = '0';
    label.style.padding = '0';
    label.style.margin = '0';
    label.style.border = '0';
    label.style.borderRadius = '0';
    label.style.boxShadow = 'none';
    label.style.width = '110px';
    label.style.height = '45px';
    label.style.minHeight = '45px';
    label.style.display = 'block';
    label.style.position = 'relative';
    label.style.left = 'auto';
    label.style.top = 'auto';
  }
})();
