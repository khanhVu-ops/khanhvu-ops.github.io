/* Only an explicit language choice is stored. No device-language inference, tracking or external requests. */
(() => {
  'use strict';
  const preferenceKey = 'kvapps.language';
  const choices = ['en', 'vi'];
  const requested = new URL(location.href).searchParams.get('lang');
  let saved;
  try { saved = localStorage.getItem(preferenceKey); } catch { /* Private/restricted browsing still works. */ }
  const initial = choices.includes(requested) ? requested : choices.includes(saved) ? saved : 'en';
  const switcher = document.querySelector('[data-language-switch]');
  const walker = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      return node.textContent.trim() && !node.parentElement.closest('script, style, [data-language-switch]')
        ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    }
  });
  const textNodes = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    textNodes.push({ node, original: node.textContent, key: node.textContent.trim() });
  }
  const attributes = [];
  document.querySelectorAll('[alt], [aria-label], meta[name="description"]').forEach(element => {
    if (element.closest('[data-language-switch]')) return;
    ['alt', 'aria-label', 'content'].forEach(name => {
      if (element.hasAttribute(name)) attributes.push({ element, name, original: element.getAttribute(name) });
    });
  });
  const page = (location.pathname.split('/').pop() || 'index.html').replace(/\.html$/, '');
  let dictionaryPromise;
  let revision = 0;
  function translations() {
    dictionaryPromise ??= fetch(`assets/i18n/${page}.json`).then(response => {
      if (!response.ok) throw new Error('Language resource unavailable');
      return response.json();
    }).catch(error => { dictionaryPromise = undefined; throw error; });
    return dictionaryPromise;
  }
  async function apply(language, persist = false) {
    const request = ++revision;
    if (persist) {
      try { localStorage.setItem(preferenceKey, language); } catch { /* Selection works without storage. */ }
    }
    // Carry the preference through navigation even when localStorage is blocked.
    document.querySelectorAll('a[href]').forEach(link => {
      if (link.closest('[data-language-switch]')) return;
      const url = new URL(link.href, location.href);
      if (url.origin === location.origin && (url.pathname.endsWith('.html') || url.pathname === '/')) {
        url.searchParams.set('lang', language); link.href = url.pathname + url.search + url.hash;
      }
    });
    try {
      const dictionary = language === 'vi' ? await translations() : {};
      if (request !== revision) return;
      textNodes.forEach(({ node, original, key }) => {
        const translated = dictionary[key];
        node.textContent = language === 'vi' && typeof translated === 'string'
          ? original.slice(0, original.indexOf(key)) + translated + original.slice(original.indexOf(key) + key.length)
          : original;
      });
      attributes.forEach(({ element, name, original }) => element.setAttribute(name, dictionary[original] ?? original));
      document.documentElement.lang = language;
      switcher.querySelectorAll('[data-language]').forEach(link => {
        if (link.dataset.language === language) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
        // Retain the section anchor when switching.
        const url = new URL(location.href); url.searchParams.set('lang', link.dataset.language);
        link.href = url.pathname + url.search + url.hash;
      });
      // Translation changes paragraph heights; restore a deep link after that layout change.
      if (location.hash) requestAnimationFrame(() => document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView());
    } catch {
      // Keep usable English content, with a visible retry message instead of silently losing the choice.
      let status = switcher.querySelector('[role="status"]');
      if (!status) { status = document.createElement('span'); status.setAttribute('role', 'status'); switcher.append(status); }
      status.textContent = 'Could not load Tiếng Việt. Please try again.';
    }
  }
  switcher.querySelectorAll('[data-language]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    switcher.querySelector('[role="status"]')?.remove();
    const language = link.dataset.language;
    const url = new URL(location.href); url.searchParams.set('lang', language);
    history.replaceState(null, '', url.pathname + url.search + url.hash);
    apply(language, true);
  }));
  apply(initial, choices.includes(requested));
})();
