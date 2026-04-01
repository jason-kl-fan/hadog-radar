async function initSearch() {
  const input = document.getElementById('site-search');
  const results = document.getElementById('results');
  if (!input || !results) return;

  const original = results.innerHTML;
  let index = [];

  try {
    const res = await fetch('search-index.json');
    index = await res.json();
  } catch (e) {
    console.error('search index load failed', e);
    return;
  }

  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if (!q) {
      results.innerHTML = original;
      return;
    }

    const matched = index.filter(item =>
      item.title.toLowerCase().includes(q) ||
      item.text.toLowerCase().includes(q) ||
      item.date.toLowerCase().includes(q)
    );

    if (!matched.length) {
      results.innerHTML = '<div class="empty-state">找不到符合的新聞日期或內容。</div>';
      return;
    }

    results.innerHTML = matched.map(item => `
      <article class="archive-card">
        <div>
          <div class="archive-date">${item.date}</div>
          <h2><a href="${item.href}">${item.title}</a></h2>
          <p>${item.text.slice(0, 180)}...</p>
        </div>
        <a class="archive-link" href="${item.href}">閱讀當日新聞</a>
      </article>
    `).join('');
  });
}

initSearch();
