/* ==========================================================
   PHOTOGRAPH FALLBACK
   ==========================================================
   Every photograph on the site is offered as <picture> with a WebP <source>
   and a JPEG in the <img>. That is how a browser gets the smaller file.

   The catch: a <source> the browser accepts is a commitment. If that WebP
   then fails to arrive — blocked, missing, a proxy that mangles it — the
   browser does NOT fall back to the <img src>. It draws nothing, and the
   perfectly good JPEG sits there unused. And because every photograph is
   offered the same way, whatever stops one tends to stop all of them: the
   page loses its photography, not one frame.

   So: on failure, drop the sources and take the JPEG.

   Loaded by the main site and by both investor pages.
   ========================================================== */
(function () {
  function fallBackToJpeg(img) {
    var pic = img.parentElement;
    if (!pic || pic.tagName !== 'PICTURE' || img.getAttribute('data-jpeg-fallback')) return;
    img.setAttribute('data-jpeg-fallback', '1');
    var sources = pic.querySelectorAll('source');
    for (var i = 0; i < sources.length; i++) sources[i].parentNode.removeChild(sources[i]);
    img.removeAttribute('srcset');
    img.src = img.getAttribute('src');   /* re-runs the choice, now JPEG only */
  }

  /* Capture: an image's error event does not bubble. */
  document.addEventListener('error', function (e) {
    if (e.target && e.target.tagName === 'IMG') fallBackToJpeg(e.target);
  }, true);

  /* This file is deferred, so anything that already failed during parsing
     never reached the listener above. Sweep those up. */
  function rescue() {
    var imgs = document.querySelectorAll('picture > img');
    for (var i = 0; i < imgs.length; i++) {
      if (imgs[i].complete && imgs[i].naturalWidth === 0) fallBackToJpeg(imgs[i]);
    }
  }
  if (document.readyState === 'complete') rescue();
  else window.addEventListener('load', rescue);
})();
