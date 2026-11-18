(function () {
  'use strict';
  var HINT = 'console-openshift-console';
  var MARKER = './console-reload.marker';
  var FAVICON = '/static/assets/public/imgs/openshift-favicon.png';
  var SETTLE_MS = 8000;
  var PROBE_TIMEOUT_MS = 8000;
  var RETRY_DELAY_MS = 10000;
  var MAX_ATTEMPTS = 6;

  var lastMarker = null;
  var initialized = false;
  var recovering = false;

  function log(msg) {
    try { console.info('[showroom] ' + msg); } catch (e) {}
  }

  function findConsoleIframe() {
    var frames = document.querySelectorAll('iframe');
    for (var i = 0; i < frames.length; i++) {
      if ((frames[i].src || '').indexOf(HINT) !== -1) return frames[i];
    }
    return null;
  }

  function consoleOrigin(f) {
    try { return new URL(f.src).origin; } catch (e) { return null; }
  }

  // Only a real console serves the favicon as an actual image.
  // The router's 503 error page is HTML and fires onerror.
  function probeConsole(origin, cb) {
    var img = new Image();
    var done = false;
    var finish = function (ok) {
      if (done) return;
      done = true;
      clearTimeout(timer);
      cb(ok);
    };
    var timer = setTimeout(function () { finish(false); }, PROBE_TIMEOUT_MS);
    img.onload = function () { finish(true); };
    img.onerror = function () { finish(false); };
    img.src = origin + FAVICON + '?t=' + Date.now();
  }

  function reloadFrame(f) {
    var u = f.src;
    f.src = 'about:blank';
    setTimeout(function () { f.src = u; }, 200);
  }

  function attemptRecovery(attempt) {
    var f = findConsoleIframe();
    if (!f) { recovering = false; return; }
    var origin = consoleOrigin(f);
    if (!origin) { recovering = false; return; }

    probeConsole(origin, function (up) {
      if (!up) {
        if (attempt < MAX_ATTEMPTS) {
          log('console backend not serving yet (attempt ' + attempt + '), retrying in ' + (RETRY_DELAY_MS / 1000) + 's');
          setTimeout(function () { attemptRecovery(attempt + 1); }, RETRY_DELAY_MS);
        } else {
          recovering = false;
          log('console did not recover after ' + MAX_ATTEMPTS + ' attempts, leaving tab as-is');
        }
        return;
      }
      log('console backend healthy, reloading console tab (attempt ' + attempt + ')');
      reloadFrame(f);
      // after the reload, confirm the tab settled by probing again
      setTimeout(function () {
        probeConsole(origin, function (stillUp) {
          recovering = false;
          if (stillUp) {
            log('console tab recovered (attempt ' + attempt + ')');
          } else {
            log('console backend dropped during reload; will re-arm on next marker');
          }
        });
      }, 5000);
    });
  }

  function tick() {
    fetch(MARKER + '?t=' + Date.now(), { cache: 'no-store' })
      .then(function (r) {
        if (!r.ok) return null;
        return r.text();
      })
      .then(function (t) {
        if (t == null) { lastMarker = null; return; }
        t = t.trim();
        if (!initialized) {
          initialized = true;
          lastMarker = t;
          return;
        }
        if (t !== lastMarker && !recovering) {
          recovering = true;
          log('console restart signalled, waiting for settle');
          setTimeout(function () { attemptRecovery(1); }, SETTLE_MS);
        }
        lastMarker = t;
      })
      .catch(function () {});
  }

  setInterval(tick, 5000);
  tick();
})();
