// Instant search for the ShezMath homepage. Filters tool cards as you type.
// Matches title, description and keywords, case-insensitive.
// Data lives in search-index.js (SHEZMATH_TOOLS). The cards on the page are
// the source of truth for what is shown; this script only hides/shows them.
(function () {
  var input = document.getElementById('tool-search');
  var noResults = document.getElementById('no-tools-found');
  if (!input || !noResults || typeof SHEZMATH_TOOLS === 'undefined') return;

  // Map each card to its searchable text: the card's own title and description,
  // plus the index entry's keywords when the card is a tool.
  var cards = [];
  var cardEls = document.querySelectorAll('.grid .card');
  for (var i = 0; i < cardEls.length; i++) {
    var link = cardEls[i].querySelector('a');
    if (!link) continue;
    var url = link.getAttribute('href');
    var entry = null;
    for (var j = 0; j < SHEZMATH_TOOLS.length; j++) {
      if (SHEZMATH_TOOLS[j].url === url) { entry = SHEZMATH_TOOLS[j]; break; }
    }
    var hay = cardEls[i].textContent.toLowerCase();
    if (entry) hay += ' ' + entry.keywords.toLowerCase();
    cards.push({ el: cardEls[i], hay: hay });
  }

  // Section headings + their grids hide when none of their cards match.
  function syncSections() {
    var headings = document.querySelectorAll('main h2');
    for (var h = 0; h < headings.length; h++) {
      var grid = headings[h].nextElementSibling;
      if (!grid || !grid.classList.contains('grid')) continue;
      var anyVisible = false;
      var cs = grid.querySelectorAll('.card');
      for (var c = 0; c < cs.length; c++) {
        if (cs[c].style.display !== 'none') { anyVisible = true; break; }
      }
      headings[h].style.display = anyVisible ? '' : 'none';
      grid.style.display = anyVisible ? '' : 'none';
    }
  }

  function filter() {
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    for (var i = 0; i < cards.length; i++) {
      var match = q === '' || cards[i].hay.indexOf(q) !== -1;
      cards[i].el.style.display = match ? '' : 'none';
      if (match) shown++;
    }
    noResults.style.display = shown === 0 ? 'block' : 'none';
    syncSections();
  }

  input.addEventListener('input', filter);
})();
