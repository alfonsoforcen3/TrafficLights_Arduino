# Private Clawdy website preview

This is the proposed replacement for the existing QR landing page. It is kept
in the private implementation repository; no publishing workflow is enabled.
Do not move the printed QR URL or publish the customer installer implicitly.

Preview from the project root with `python3 -m http.server 4393 --bind 127.0.0.1
--directory site`. The page has no server/API dependencies and includes no CAD
or supplier assets. The hero is a transparent render of the actual 45 mm model;
see assets/SOURCE.txt for its geometry references and limitations.

The public site is hosted separately in `alfonsoforcen3/alfonsoforcen3.github.io`
under `clawd-mascot-3d/`. On a later owner-authorized publication, copy only
index.html, style.css, app.js and assets/clawdy-hero.png to that path. Keep the
existing printed QR URL stable and verify its redirect, page and assets afterward.
No public download or checkout may be invented before approved artifacts exist.
