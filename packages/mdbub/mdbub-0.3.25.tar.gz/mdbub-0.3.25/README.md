
# 🧠 mdbub

> A mindmap tool for your terminal.
> Fast. Fluid. Keyboard-native. Built for thinkers who live in the CLI.

---

## 🚀 What is `mdbub`?

`mdbub` lets you build and manage mindmaps directly in your terminal. It's designed for speed-of-thought capture, with two streamlined modes: one for lightning-fast inline edits, and one for full-screen TUI visual editing.

Unlike plain Markdown, `mdbub` lets you *structure* your ideas—navigate, fold, tag, and rework them instantly, using only your keyboard.

---

## 🧨 Killer Features

- **Quick Mode**: Instant mini-editor for rapid note capture.
- **Edit Mode**: Full-screen terminal interface for folding, searching, tagging.
- **Keyboard-native UX**: Everything is hotkey driven. Customize to your liking.
- **Pipe Mode (coming soon)**: Interoperable with the rest of your CLI stack.
- **Zero-mouse flow**: It's not just fast. It feels *alive* under your fingertips.

---

## 💡 Example

```bash
mdbub tech_idea.mdbub
```

It looks like this:

```
【AI-Driven Co...】 > 【Core Concept】 > 【Voice Intera...】
● Voice Interaction should be two-way
└─ No children
```
Just start typing to edit the label on a node; or hit **enter** to add a sibling; or hit **tab** to add a child.

If you add an id in the text, like this: `[id:design/api]`, you can comeback later directly to that node with a deeplink: `mdbub tech_idea.mdbub#design/api`

While you work:
- Add inline `#tags` to make them easier to find or filter
- Add inline `@key:value` maps to track metadata of nodes
- Add inline `[id:something]` ids to later link

## 🛠 Installation

### Quick Install (coming soon)
```bash
# PyPI (all platforms)
pip install mdbub
# or
pipx install mdbub

# Homebrew (macOS)
brew install mdbub  # (when available in Homebrew Core)

# Chocolatey (Windows)
choco install mdbub  # (when available)
```

### Early Access
While we work on getting into the main package repositories, you can install via:

```bash
# Development version
pip install git+https://github.com/collabinator/mdbubbles.git
```
---

## 🤝 Contribute

Want to help shape the future of CLI-based structured thinking?

- [Open issues](https://github.com/collabinator/mdbubbles/issues)
- [Start a discussion](https://github.com/collabinator/mdbubbles/discussions)
- [Follow the roadmap](https://github.com/collabinator/mdbubbles/projects)

---

## 🧠 Built for Thinkers

`mdbub` is for people who think in trees.
Who sketch in lists.
Who live in the terminal.
And who know that a good idea starts fast—and needs space to grow.



## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.
