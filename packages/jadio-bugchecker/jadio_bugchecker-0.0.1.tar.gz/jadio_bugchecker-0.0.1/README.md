# jadio-publisher

Jadio-compatible extension package that adds the `jpub` CLI command.  
`jpub` provides a professional, npm-style publishing workflow for Jadio-based Python packages.

---

## 📦 What is Jadio Publisher?

`jpub` is a modular CLI extension for the [Jadio framework](https://pypi.org/project/jadio/).  

It gives you a full *semantic versioning*, *build*, *publish*, and *Git integration* experience, designed to mimic modern tools like npm and poetry.

✅ Automate version bumping  
✅ Ensure clean builds  
✅ Enforce one-version-per-publish  
✅ Upload to PyPI with Twine  
✅ One-click "release" flow  
✅ Integrated Git commands

---

## ⚡️ Features

- **jpub init** – Initialize jpubconfig in your project
- **jpub bump** – Interactively bump your version
- **jpub show** – View current and last built versions
- **jpub build** – Clean and build your dist/
- **jpub pypi** – Upload dist/* to PyPI via Twine
- **jpub go** – Full release (bump ➜ build ➜ publish)
- **jpub git** – Git helpers (add, commit, push, pull, status, log, repo)

---

## 🚀 Installation

First, install the Jadio framework itself:

```bash
pip install jadio
```

Then install this package:

```bash
pip install jadio-publisher
```

✅ This will register the `jpub` CLI command.

---

## 💻 Quick Start

### 1️⃣ Initialize once per project
Creates `jadio_config/jpubconfig.json` to track builds.

```bash
jpub init
```

---

### 2️⃣ Bump your version
Prompted to choose a new version:

```bash
jpub bump
```

---

### 3️⃣ Build your package
Cleans old dist/ and ensures version is bumped:

```bash
jpub build
```

---

### 4️⃣ Upload to PyPI
Uploads dist/* to PyPI via Twine:

```bash
jpub pypi
```

---

### ⚡️ Or do it all in one step:

```bash
jpub go
```

This runs:

✅ bump ➜ ✅ build ➜ ✅ pypi

---

## 🔗 Git Helpers

Manage git without leaving your CLI:

```bash
jpub git -add
jpub git -commit "message"
jpub git -push
jpub git -pull
jpub git -status
jpub git -log
jpub git -repo
```

---

## 📂 Project Structure Example

After `jpub init`, you'll have:

```
your-project/
├── src/
│   └── your_package/
│       └── __init__.py
└── jadio_config/
    └── jpubconfig.json
```

✅ jpubconfig.json tracks last built version to prevent duplicate publishes.

---

## 🛠️ Requirements

- Python 3.8+
- [Twine](https://pypi.org/project/twine/) installed (`pip install twine`)
- [Build](https://pypi.org/project/build/) installed (`pip install build`)
- Git installed and initialized in your project

---

## ✅ License

MIT License

---

## 🤝 Contributing

Pull requests and feedback welcome!

---

## ✨ Part of the Jadio Modular CLI System

Jadio is a Node.js-style package manager for Python projects.  

✅ Main Framework: [`jadio`](https://pypi.org/project/jadio/)  
✅ Extension: `jadio-publisher` ➜ adds `jpub` command
