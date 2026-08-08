(() => {
  document.documentElement.lang = document.documentElement.lang || 'sw-TZ';

  const main = document.querySelector('main');
  const content = document.querySelector('#content');
  if (main && !main.id) main.id = 'main-content';
  if (content && !content.hasAttribute('tabindex')) content.setAttribute('tabindex', '-1');

  if (main && !document.querySelector('#skip-to-content')) {
    const skip = document.createElement('a');
    skip.id = 'skip-to-content';
    skip.href = '#main-content';
    skip.textContent = 'Ruka hadi maudhui makuu';
    skip.addEventListener('click', () => {
      window.setTimeout(() => content?.focus(), 0);
    });
    Object.assign(skip.style, {
      position: 'fixed', left: '1rem', top: '-5rem', zIndex: '100',
      padding: '.75rem 1rem', borderRadius: '.5rem', background: '#111827',
      color: '#fff', fontWeight: '700', textDecoration: 'none'
    });
    skip.addEventListener('focus', () => { skip.style.top = '1rem'; });
    skip.addEventListener('blur', () => { skip.style.top = '-5rem'; });
    document.body.prepend(skip);
  }

  const pageHeading = document.querySelector('#page-heading, h1[id], h1');
  if (pageHeading && !pageHeading.id) pageHeading.id = 'page-heading';

  for (const section of document.querySelectorAll('section')) {
    const type = section.dataset.sectionType || '';
    const currentRole = section.getAttribute('role');
    if (!currentRole || currentRole === 'activity') {
      const hasControls = Boolean(section.querySelector('input, textarea, select, button'));
      section.setAttribute('role', hasControls || type.startsWith('activity_') ? 'form' : 'article');
    }
    if (!section.hasAttribute('aria-label') && !section.hasAttribute('aria-labelledby') && pageHeading) {
      section.setAttribute('aria-labelledby', pageHeading.id);
    }
  }

  const improveControlNames = (root = document) => {
    const controls = [];
    if (root.matches?.('input, textarea, select')) controls.push(root);
    controls.push(...(root.querySelectorAll?.('input, textarea, select') || []));
    for (const control of controls) {
      const label = (control.getAttribute('aria-label') || '').trim();
      const blank = label.match(/^Blank\s+(\d+)(?:\s+of\s+(\d+))?$/i);
      if (blank) {
        const total = blank[2] ? ` kati ya ${blank[2]}` : '';
        control.setAttribute('aria-label', `Jaza jibu katika nafasi ya ${blank[1]}${total}`);
      }
      if (/\soption\s+\d+$/i.test(label)) {
        control.setAttribute('aria-label', label.replace(/\soption\s+(\d+)$/i, ', chaguo la $1'));
      }
    }
  };
  improveControlNames();

  const observer = new MutationObserver((records) => {
    for (const record of records) {
      if (record.type === 'attributes') {
        improveControlNames(record.target.parentElement || document);
        continue;
      }
      for (const node of record.addedNodes) {
        if (node.nodeType !== Node.ELEMENT_NODE) continue;
        improveControlNames(node);
        for (const section of node.matches?.('section') ? [node] : node.querySelectorAll?.('section') || []) {
          if (!section.getAttribute('role') || section.getAttribute('role') === 'activity') {
            section.setAttribute('role', section.querySelector('input, textarea, select, button') ? 'form' : 'article');
          }
          if (!section.hasAttribute('aria-label') && !section.hasAttribute('aria-labelledby') && pageHeading) {
            section.setAttribute('aria-labelledby', pageHeading.id);
          }
        }
      }
    }
  });
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['aria-label']
  });

  const style = document.createElement('style');
  style.id = 'adt-accessibility-focus-styles';
  style.textContent = `
    :where(a, button, input, textarea, select, [tabindex]):focus-visible {
      outline: 4px solid #f59e0b !important;
      outline-offset: 3px !important;
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        scroll-behavior: auto !important;
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
      }
    }
  `;
  document.head.appendChild(style);
})();
