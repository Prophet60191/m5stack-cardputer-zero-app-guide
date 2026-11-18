# Official UI and app-shell evaluation

Reviewed 2026-11-18 under the [library principles](library-principles.md).

**Decision: reuse the official foundation appropriate to the app, adapt its
presentation to our preferences, and defer a separate app-shell framework.**
Colors, menus and layouts can be personal choices while lifecycle, input,
resource ownership and backend authority remain intact. If a visual request
also changes behavior, evaluate that behavior explicitly rather than assuming
it is cosmetic. No application implementation is changed by this evaluation.

## Current official sources

Default-branch heads were checked live. Source hashes and selected checks are in
the [evidence manifest](official-ui-evaluation-evidence.json).

| Source | Revision | Reviewed entry points |
|---|---|---|
| [CMake Template](https://github.com/CardputerZero/Template/tree/477fa6d217b683e3084c361a757f03dc8ca9f753) | `477fa6d217b683e3084c361a757f03dc8ca9f753` | ScreenManager, BaseScreen/BaseWidgets, subjects/bindings, theme, assets, title/navigation bars, Help/Toast, app loop and screenshot service |
| [Shared page API](https://github.com/CardputerZero/launcher/blob/13d2f26b103e5c9292be7287bc640df9adf6faeb/ext_components/cp0_lvgl/include/ui_app_page.hpp) | launcher `13d2f26b103e5c9292be7287bc640df9adf6faeb` | AppPageRoot, AppPage, optional bar regions/components, runner and helper contracts |
| [Runtime and launcher flow](https://github.com/CardputerZero/launcher/blob/13d2f26b103e5c9292be7287bc640df9adf6faeb/docs/launcher-project-guide/02-runtime-framework-and-boot-flow.md) | same launcher revision | Setup/teardown, internal pages, external process handoff and return |
| [HelloWorld example](https://github.com/CardputerZero/launcher/blob/13d2f26b103e5c9292be7287bc640df9adf6faeb/projects/HelloWorld/main/src/main.cpp) | same launcher revision | Shared runner with an app-owned page and custom content/navigation |
| [Official key/UI guidance](https://github.com/CardputerZero/cardputerzero.github.io/blob/eeb3c9f61afc33cc1ceb33f3ed0b81fd95491c0b/docs/en/CP0_keys.md) | `eeb3c9f61afc33cc1ceb33f3ed0b81fd95491c0b` | Action hints, alternative keys, Fn actions and navigation recommendations |

The source review also includes APPLaunch's carousel view/layout, settings
roller/component examples and lifecycle tests. These sources are not proof that
the same revision or services are installed on a particular device.

## Two meanings of shell

**The device launcher** discovers/launches applications and coordinates display,
input and timers while handing control to an external process and returning.
An app's theme should not replace that process policy or duplicate its global
controls. Internal launcher pages and independent packaged apps are different
integration paths.

**The app's own UI foundation** owns its screen, focus group, content regions,
widgets and callbacks. The Template supplies a CMake/MVVM path; the shared cp0
runtime supplies a SCons/Kconfig runner/page path. Choose a coherent path for an
app. Neither path requires copying the launcher's whole home screen, settings
tree or hardware service selection into every application.

## What the official code already supports

- Template ScreenManager defers page requests with LVGL asynchronous work,
  cancels pending work and removes its observer during destruction. BaseScreen
  owns the screen and its title/navigation widgets. These mechanisms already
  provide useful ownership; custom menu styling does not require a new manager.
- Template theme roles separate surfaces, text, buttons and semantic status
  colors. Theme bindings observe changes through object-associated observers.
  This is a suitable foundation for app palette variants and styled widgets.
- Shared AppPage is the standard content/top-bar page. AppPageRoot explicitly
  supports a blank/custom page, and the API supplies optional bottom-bar layout
  and separately owned title/time/network/battery components. Custom content
  is an intended use, not inherently a departure from the official architecture.
- Shared runner hooks separate setup, quitting and teardown from the app's
  page content. The HelloWorld example uses that runner while owning its own
  controls and palette state.
- Official APPLaunch has carousel and settings selector implementations. They
  are examples with launcher-specific dependencies, not evidence that every
  native app must use that exact presentation or can import it unchanged.

## Use, adapt or depart

| Area | Decision | Our freedom and the compatibility boundary |
|---|---|---|
| App loop, screen ownership and teardown | **Use the selected official foundation** | Retain one coherent initialization/input/render/cleanup path. Do not add a second runner to obtain a different appearance. Existing apps need no migration solely for visual uniformity. |
| Screen transitions and Back | **Adapt app navigation above that foundation** | Page names, menu order and navigation depth belong to the app. Preserve safe deferred destruction, pending-work cancellation and focus restoration. |
| Colors and selection | **Adapt palette/styles** | Burgundy, amber, rounded rows, left rails and bubble outlines can differ by app and state. Keep focus distinguishable and errors understandable without relying on color alone. No source-level need to retain the demo accent was found. |
| Fonts, spacing and geometry | **Adapt within measured content bounds** | Template uses 30 px title/footer constants; shared page API has a 20 px standard top bar. Those are implementation defaults, not one universal visual mandate. Derive usable content size from the selected layout and verify full font height, long text and selected-row visibility at 320×170. |
| Top/status bar | **Reuse/adapt supplied components** | Customize title and placement using the chosen page API. A blank page or disabled bar is supported by the shared API; if status is shown, its source and meaning must stay truthful. Detach subscriptions/timers before destroying associated objects. |
| Footers and actions | **Adapt with documented key choices** | Official guidance recommends aligned 4–8 action hints and also permits other keys with explanations. Our contextual actions and reduced navigation hints are preferences to review, not automatically incompatible. Keep actual shortcuts and displayed actions consistent, and preserve Help access. |
| Carousel | **Use official examples as references; adapt presentation** | APPLaunch's five-slot geometry, images, slider and registry are launcher-specific. We can keep our lightweight app carousel style without transplanting the entire launcher. A later reusable widget needs item/callback and ownership boundaries plus lifecycle tests. |
| Lists and settings menus | **Evaluate/adapt existing examples** | APPLaunch already has a settings roller with centered selection, long-text scrolling and focus changes. Its settings-tree/font/component dependencies differ from a simple app list. Compare those dependencies before extracting another list implementation. Row style does not justify importing global setting actions. |
| Help, toast and progress | **Reuse/adapt Template widgets where suitable** | Supply app content, dimensions and font choices; keep timer/observer cleanup. Help must own input while open. Keep transient/persistent messages distinct and show real operation state rather than optimistic success. |
| Screenshots and overlays | **Adapt capture integration if needed** | Template parents Help/Toast to the top layer while its screenshot service snapshots the active screen. An overlay screenshot therefore needs an explicit capture/parenting decision. This is an integration concern, not a demonstrated firmware defect. |
| App settings and backend state | **Preserve authority; adapt only presentation** | Theme or menu changes must not implicitly toggle device-wide services, change radio settings, write tags or alter privacy. Global Settings views are not harmless style components. Keep app preferences separate from backend-confirmed state. |
| Background work and modularity | **Keep the app-appropriate architecture** | A custom palette does not require changing Mesh's supervisor, Surveyor's worker or NFC's helper. Respect the chosen LVGL thread/locking boundary; return background results through the app's established UI handoff. |
| A replacement app-shell SDK | **Defer** | Both official foundations already accommodate custom presentation. Reuse the foundation first; justify any additional component by a specific need and compatible integration. |

## How visual preferences will be recorded

For each preference, record the desired appearance, applicable states, official
component used, styling/layout adaptation and behavior that must remain intact.
Examples include an accent palette, selected-row rail, readable supporting text
or an action-oriented footer. These can become theme data, layout parameters,
focused widgets or documented patterns; they do not all require new classes.

Changes that hide essential feedback, make an action ambiguous, break focus,
trigger commands twice or change consent/save behavior require a behavior review.
Discuss any resulting tradeoff with the owner. Existing app differences are
inputs to that discussion, not silently approved universal defaults. In particular,
the inventory's footer and type-size choices remain open.

## Checks performed and limits

- Reviewed current official sources and examples at the revisions above; retained
  hashes in the evidence manifest. No claim is made that all SDK services or all
  official apps were reviewed.
- Four unmodified official helper-contract tests pass on macOS arm64 with
  ASAN/UBSAN and warnings as errors: screen-component detach, screen-delete
  cleanup, status-resource readiness and runner lifetime/concurrent claims.
  Leak detection was disabled. These test helper behavior, not rendered screens,
  physical keys, complete teardown under every fault or a race-free runtime.
- No new app build, full SDK suite, pixel/layout rendering, device qualification,
  live backend operation, extraction, migration or upstream submission occurred.
  Downloaded source and test binaries/logs remain in ignored build storage.
- Source/license notices remain applicable to later copying. This report does
  not establish that every launcher-local example is a stable public component.

## Next step

Record the owner's visual and interaction preferences against this boundary
matrix, then prepare a small style specification with representative screens and
states. Resolve footer/type/selection choices before enforcing consistency.
After that, identify the smallest theme or widget adapters needed on top of the
official foundation. Implementation and app migrations remain separate work.

[Inventory](library-inventory.md) · [Principles](library-principles.md)
· [Keyboard decision](official-input-evaluation.md) · [UI chapter](04-ui-and-polish.md)
