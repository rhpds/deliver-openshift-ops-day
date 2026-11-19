(function () {
  'use strict';
  var HINT = 'console-openshift-console';
  var MARKER = './console-reload.marker';
  var FAVICON = '/static/assets/public/imgs/openshift-favicon.png';
  var SETTLE_MS = 8000;
  var PROBE_TIMEOUT_MS = 8000;
  var RETRY_DELAY_MS = 10000;
  var MAX_ATTEMPTS = 6;
  var COUNTDOWN_SEC = 15;

  var lastMarker = null;
  var initialized = false;
  var recovering = false;
  var toast = null;
  var countdownTimer = null;

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

  function dismissToast() {
    if (toast) { toast.remove(); toast = null; }
    if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null; }
  }

  function showToast(onConfirm, onCancel) {
    dismissToast();
    toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:2147483647;background:#151515;color:#fff;padding:16px 20px;border-radius:8px;font-family:RedHatText,sans-serif;font-size:14px;box-shadow:0 4px 16px rgba(0,0,0,.4);max-width:340px';
    var text = document.createElement('div');
    text.style.cssText = 'margin-bottom:12px;line-height:1.4';
    text.textContent = 'The OpenShift console restarted. Refreshing the console tab in ' + COUNTDOWN_SEC + 's so it reconnects cleanly.';
    var btnRow = document.createElement('div');
    btnRow.style.cssText = 'display:flex;gap:8px';
    function mkBtn(label, primary, cb) {
      var b = document.createElement('button');
      b.textContent = label;
      b.style.cssText = (primary ? 'background:#ee0000;' : 'background:#383838;') +
        'color:#fff;border:none;border-radius:4px;padding:6px 12px;font-size:13px;cursor:pointer';
      b.onclick = cb;
      return b;
    }
    btnRow.appendChild(mkBtn('Refresh now', true, function () { dismissToast(); onConfirm(); }));
    btnRow.appendChild(mkBtn("Don't refresh", false, function () { dismissToast(); onCancel(); }));
    toast.appendChild(text);
    toast.appendChild(btnRow);
    document.body.appendChild(toast);

    var left = COUNTDOWN_SEC;
    countdownTimer = setInterval(function () {
      left--;
      if (left <= 0) { dismissToast(); onConfirm(); return; }
      text.textContent = 'The OpenShift console restarted. Refreshing the console tab in ' + left + 's so it reconnects cleanly.';
    }, 1000);
  }

  function attemptRecovery(attempt) {
    var f = findConsoleIframe();
    if (!f) { recovering = false; return; }
    var origin = consoleOrigin(f);
    if (!origin) { recovering = false; return; }

    probeConsole(origin, function (up) {
      if (!up) {
        if (attempt < MAX_ATTEMPTS) {
          log('console backend not serving yet (attempt ' + attempt + '), retrying');
          setTimeout(function () { attemptRecovery(attempt + 1); }, RETRY_DELAY_MS);
        } else {
          recovering = false;
          log('console did not recover, leaving tab as-is');
        }
        return;
      }
      showToast(
        function () { reloadFrame(f); recovering = false; log('console tab refreshed'); },
        function () { recovering = false; log('console refresh cancelled by user'); }
      );
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
