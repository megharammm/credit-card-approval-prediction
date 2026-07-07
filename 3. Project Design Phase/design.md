---
version: 1.0.0
name: Aura Ambient Minimalism
description: A dark-themed system utilizing high-blur surfaces, 3D ambient backgrounds, and monochrome accents.
colors:
  background: "#000000"
  foreground: "#ffffff"
  muted: "#d1d5db"
  subtle-border: "rgba(255, 255, 255, 0.1)"
  glass-bg: "rgba(255, 255, 255, 0.05)"
  neutral-300: "#d4d4d4"
  accent-glow: "rgba(255, 255, 255, 0.05)"
typography:
  display:
    family: "Inter"
    weight: 500
    letterSpacing: "-0.05em"
  body:
    family: "Inter"
    weight: 400
    size: "1rem"
  label:
    family: "Inter"
    weight: 500
    size: "0.75rem"
spacing:
  xs: "6px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  section: "80px"
rounded:
  none: "0px"
  sm: "4px"
  md: "8px"
  lg: "12px"
  full: "999px"
components:
  navbar:
    type: "floating-glass"
    blur: "12px"
    border: "1px solid rgba(255,255,255,0.1)"
  button-primary:
    bg: "#ffffff"
    text: "#000000"
    radius: "999px"
  button-ghost:
    bg: "rgba(255,255,255,0.1)"
    border: "1px solid rgba(255,255,255,0.2)"
    blur: "4px"
  preview-panel:
    bg: "rgba(0,0,0,0.4)"
    blur: "12px"
    border: "1px solid rgba(255,255,255,0.1)"
motion:
  speed: "300ms"
  curve: "cubic-bezier(0.4, 0, 0.2, 1)"
---
## Overview
Aura Ambient Minimalism is designed for immersive digital experiences. It prioritizes a "dark ambient" aesthetic where the UI floats over a deep, 3D-simulated space. The system relies on high contrast between pure black backgrounds and white typography, softened by layers of glassmorphism.

## Colors
The palette is strictly monochrome. Use pure black (#000000) for the base layer to maximize the depth of 3D backgrounds. White (#ffffff) is used for primary text and high-action components. Transparency (Alpha) is a core color variable, used at 5%, 10%, and 20% to create depth without introducing new hues.

## Typography
Typography is centered around the Inter font family. High-order headings (h1) should use a tracking-tighter value to appear architectural. Body text should use neutral-300 to reduce visual fatigue on dark backgrounds. Labels and chips utilize uppercase or medium-weight 12px sizing for clarity.

## Spacing
A strict 4px/8px grid system is employed. Navbars use specific internal padding (12px top/bottom, 16px left/right). Section spacing is generous (80px to 160px) to maintain a minimalist, premium feel.

## Layout
Layouts are structured in three primary layers:
1. **Background Layer**: Fixed position, containing 3D scenes (Spline) or large blurred radial gradients.
2. **Midground Layer**: The main scrollable content container containing text and media.
3. **Foreground Layer**: Sticky or fixed elements like the glass navbar, occupying z-index 50.

## Elevation & Depth
Depth is achieved through `backdrop-filter: blur()`. Instead of traditional drop shadows, use thin white borders with low opacity (0.1) and internal glows. A large, central radial gradient (blur 100px, 5% opacity) is used behind text to lift it off the 3D background.

## Shapes
Use ultra-rounded corners (full/999px) for interactive elements like buttons, chips, and navbars to convey a friendly, modern tech feel. Use soft-rectangles (8px to 12px) for complex containers such as app previews or cards.

## Components
- **Glass Navbar**: A floating capsule containing brand and navigation. Must use a white border with 10% opacity and a medium blur.
- **Hero Section**: Centered stack featuring a small chip (Design Studio), a heavy tracking h1, and dual-action buttons.
- **App Preview**: A container mimicking a browser or application window with 3-dot window controls and internal structural skeletons using glass-bg tokens.
- **Action Chips**: Small, pill-shaped indicators for labels or categories.

## Motion
Interactions should be subtle and smooth. Use a 300ms transition for hover states. Buttons should scale slightly or shift in opacity rather than changing color dramatically.

## Do's and Don'ts
- **Do** use large amounts of negative space between sections.
- **Do** use white borders with low opacity to define edges instead of solid gray lines.
- **Don't** use solid gray backgrounds; use black with opacity-based overlays.
- **Don't** use sharp corners for interactive elements.

## Accessibility
Maintain a 4.5:1 contrast ratio for all secondary text against the dark background. Since glassmorphism can reduce readability, ensure the `backdrop-blur` is at least 8px to separate text from background movement.