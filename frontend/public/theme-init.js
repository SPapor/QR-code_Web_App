// Runs synchronously in <head> (external file: CSP forbids inline scripts) so the
// chosen theme/palette are applied before first paint — no light/dark flash.
(function () {
  var theme = localStorage.getItem('theme');
  var dark = theme === 'dark' || (theme !== 'light' && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  var palette = localStorage.getItem('palette');
  if (palette && palette !== 'terracotta') document.documentElement.dataset.palette = palette;
})();
