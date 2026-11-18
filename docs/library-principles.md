# Personal reusable-library principles

Agreed 2026-11-18. The [component inventory](library-inventory.md) applies these
principles to existing app code and proposes the first implementation scope.

Our library captures how we prefer to build applications for CardputerZero:
their appearance, interaction and internal design. It preserves tested work and
lessons so future apps can be more consistent and easier to build and maintain.
These principles describe our choices; the general app guide continues to
distinguish platform requirements from optional approaches and personal preferences.

## Build on the official foundation

Use suitable official firmware, components, tools and documentation as the
starting point. The library complements that foundation. Reuse and adapt what
works well, preserve attribution and licenses, and add pieces that serve our apps.
Its purpose is not to replace official firmware or official app-building guides.

Before designating any piece as reusable or designing its extraction, first
inspect the relevant current official guidance, implementation and examples.
Record the reviewed versions, what they provide and how they fit our needs.
Then decide whether to use the official approach as provided, adapt it or
deliberately take a different approach. Document the reasons, tradeoffs and
compatibility implications. Existing shared code in our apps is a candidate,
not an automatic decision to maintain our own implementation. Apply this order
to visual components, input, application logic and backend patterns alike.

## Preserve our preferences and deliberate design choices

Reusable work can include layouts, colors, spacing, menus, highlighting, keyboard
behavior and navigation. It can also include specific application logic,
persistence, background work and backend organization.

A component does not need to correct an official defect to belong in our library.
It may express a preference or a deliberate architectural choice. Mesh's modular
UI/backend design is one example: we chose separation to suit its responsibilities
and make parts easier to maintain and test, accepting additional communication
and coordination. Record why a pattern was chosen, its benefits and costs, and
when it fits. Each new app should use the pieces appropriate to its needs;
modularity does not require every app to have Mesh's supervisor architecture.

## Investigate differences fairly

We may intentionally choose a different approach from the official developers.
Before calling it a fix or improvement, inspect the relevant official design and
version, check whether the concern has already been addressed, and consider
whether the difference reflects an intentional choice or different requirements.

When claiming a better approach, identify the use case and demonstrate the
benefit. Test the behavior, document tradeoffs and compatibility, and separate
what has been verified from what remains uncertain. Official origin alone does
not establish that an approach is best for every app; our preference alone does
not establish a general improvement.

## Decide together what to keep or share

Discuss meaningful departures and decide what they represent:

| Kind of contribution | How we treat it |
|---|---|
| Personal preference | Keep it as part of how we build our apps. |
| Useful alternative | Document its reasons, tradeoffs and situations where it fits. |
| Demonstrated improvement or fix | Consider sharing the evidence and implementation with the official developers. |

These categories can overlap. A difference does not automatically require an
upstream proposal, and a personal choice may still be useful to others. Decide
case by case whether to keep it within our library, document an optional approach
or share it with M5Stack. Recording or preparing work does not make that sharing
decision for us.

## Keep reuse practical

Prefer focused, tested components and understandable patterns. Preserve useful
lessons, supported-version information and ownership expectations as pieces are
reused. Extract shared code when actual use supports it, while continuing to use
official components that fit. A shared library should reduce repeated work and
support reliability without forcing unrelated apps into one design.

[Component decisions](components.md) · [Architecture choices](03-architecture.md)
· [Guide index](../README.md)
