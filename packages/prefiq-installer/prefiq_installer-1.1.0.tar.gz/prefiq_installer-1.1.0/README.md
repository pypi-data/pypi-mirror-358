<p align="center">
  <img src="images/logo.png" alt="Prefiq Logo" width="200"/>
</p>

<h1 align="center">Prefiq CLI</h1>

<p align="center">
  Modern Full-Stack App Scaffolding Tool<br>
  Build, manage, and scale modular Python projects with ease.
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/PREFIQ/prefiq-py-cli" alt="Latest Release">
  <img src="https://img.shields.io/pypi/dm/prefiq" alt="Downloads">
  <img src="https://img.shields.io/github/license/PREFIQ/prefiq-py-cli" alt="License">
  <img src="https://img.shields.io/github/actions/workflow/status/PREFIQ/prefiq-py-cli/ci.yml" alt="Build Status">
</p>

---

### 1. Install Prefiq

```bash
pip install prefiq
````

Or use the installer script:

```bash
python install_prefiq.py
```

### 2. Create a New Project

```bash
prefiq install sundar
```

This sets up the `sundar/` project folder with:

* ✅ Python virtual environment (`venv/`)
* ✅ Standard files: `requirements.txt`, `README.md`, `LICENSE`, `.gitignore`
* ✅ Base framework folder: `prefentity/`

---

## 📁 Create Apps Using Templates

Inside your project folder:

```bash
cd sundar
```

### ▶️ Full App Scaffold

```bash
prefiq new-app crm
```

Creates a full app at `apps/crm/` with:

```
apps/
└── crm/
    ├── app.py
    ├── config.py
    ├── assets/
    ├── templates/
    ├── routes/
    ├── logic/
    ├── database/
    └── ...
```

### ⚡ Base (Minimal) App Scaffold

```bash
prefiq new-app auth --base
```

Generates only the essential app folders and files.

### ♻️ Force Overwrite an Existing App

```bash
prefiq new-app blog --force
```

This will overwrite the existing `apps/blog` folder.

---

## 🧩 Manage Apps

### List Registered Apps

```bash
prefiq list-apps
```

### Remove an App

```bash
prefiq remove-app blog
```

This will remove the folder and update `prefentity/manifest.json`.

---

## 🛠️ Features

* Modular app structure
* Plug-and-play scaffold templates
* Configurable base (`--base`) or full app generation
* Virtual environment setup
* Standardized project bootstrapping
* JSON-based app registry (`manifest.json`)

---

## 📈 Project Stats

* **Latest Version**: `v0.1.0`
* **PyPI Downloads**: `10,000+` (placeholder)
* **GitHub Stars**: `⭐ 500+` (placeholder)

---

## 🤝 Contributing

We welcome contributions! To get started:

1. Fork this repository
2. Create a feature branch
3. Submit a pull request

Make sure your code passes all existing tests and includes new ones as necessary.

### Run Locally

```bash
git clone https://github.com/PREFIQ/prefiq-py-cli.git
cd prefiq-py-cli
pip install -e .
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🔐 Security Policy

If you discover a vulnerability, please submit an issue or contact us directly. See [SECURITY.md](SECURITY.md) for guidelines.

---

## 📬 Contact

For support or questions, reach out via GitHub issues or email us at `support@prefiq.dev`.

---

> Built with passion by the **Prefiq** engineering team.

```