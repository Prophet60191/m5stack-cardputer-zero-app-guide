# Reusable carousel position indicator

Use this when a home carousel has multiple positions that wrap around. This
is a progress cue, not a control. It does not own selection, navigate, or
reset any app state. The selected slot is a wider accent pill so its state
does not depend on color alone.

![Tick and Bell simulator with the second carousel position selected](../../../docs/images/tick-bell-carousel-position.png)

Desktop simulator capture, not a hardware photo. The simulated 100% is the official Template’s desktop sample value.

- Keep one centered, stable slot per menu item. Inactive dots are 4×3 px,
  the active pill is 8×3 px, and the pitch is 9 px.
- Use NFC Tools’ placement on the 320×170 reference screen: start the menu name at y=82 and the dots at y=138. The blank space after the label is intentional; do not push the label down toward the dots when the app has no subtitle.
  Keep it separate from the sliding/fading content. Do not add a footer just
  to hold the dots or replace a submenu's separate overflow marker with them.
- Update it from the same selected index that drives the icon and label.
  Wraparound moves the active pill to the other end immediately. A theme
  change recolors it without changing item identity or animating selection.
- Hide it for zero or one item. This implementation is bounded at 24 slots;
  use another presentation if the slots no longer fit in the available width.

## Why this is a separate pattern

The official Template supplies a UI framework, not this particular visual position cue. The Mesh carousel already controls movement and animation; the dots answer a different question: which item is selected when left/right wraps. NFC Tools proved the visual idea with six fixed slots. The extracted header centers any supported item count so each app can reuse it without hard-coded coordinates, adopting the NFC UI, or adding another keyboard handler.

## Use the component

The [MIT header](carousel_position.h) expects LVGL 9 and your app's palette.
Create it after the carousel content so it draws on top of the background:

```cpp
auto position = cp0_ui::CarouselPosition::create(root, item_count, 138);
position.update(selected_index, accent_rgb, muted_rgb);
```

Keep the handle only for as long as the same LVGL parent lives. Drop it before
cleaning that screen, and recreate it if the menu count changes. The app still
owns navigation and must supply a valid zero-based selected index. The slots
never take keyboard focus.

## Source and status

The design comes from NFC Tools' `App::home()` implementation at the locally
reviewed working-tree snapshot (base `8e4c884`; source SHA-256
`f2bada65bcadf2f82ce6772e38fbca1413aa25dc275b640196cb0846bde82e4a`).
That source uses fixed coordinates for six entries. Tick & Bell now also matches NFC Tools’ vertical title and dot positions. The component preserves the visual proportions but calculates centered positions for the app’s menu count. NFC Tools remains the design reference, not a runtime dependency.

Tick & Bell is the first integration of this shared header. Desktop event-path checks showed movement across all three slots, wrap from first to last, and theme recoloring without changing selection. The 0.1.2 simulator captures verified the revised spacing and wrap; physical input and display on a handheld remain separate checks. NFC Tools retains
its own existing indicator. No migration of Mesh, NFC Tools, or other apps is
implied. Verify home on a device in both themes, forward/back wrap, labels
clear of the bar, and unchanged submenu navigation before adopting it elsewhere.

[UI preferences](../../../docs/ui-preferences.md) · [UI and polish](../../../docs/04-ui-and-polish.md)
