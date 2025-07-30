# GFAB – Gemini Flask App Builder

**GFAB (Gemini Flask App Builder)** is a command-line tool that helps developers generate customizable Flask applications using interactive prompts and AI assistance. It is designed to speed up the process of bootstrapping a Flask project with modern best practices.

> **Note:** This repository contains the scaffolding logic only. The core project generation logic is kept private for licensing and intellectual property reasons.

---

## Features

- Interactive setup using terminal-based prompts
- AI-assisted configuration using Gemini
- Optional components include:
  - RESTful API scaffolding
  - Jinja2 template engine
  - Authentication and role-based access control
  - Static files setup
  - Environment configuration
  - Migrations and database setup
  - Admin dashboard (optional)
  - Internationalization (i18n), logging, and more

---

## Installation

### From Source

```bash
pip install .
```

---

## License & Usage Terms

Copyright (c) 2025  
**Swarup Baral**

All rights reserved. This software and all associated source code, configurations, and files are private intellectual property of the author, Swarup Baral.

You are **not permitted** to:

- Share, distribute, or host this code publicly or privately.
- Modify or reuse the code without explicit written permission.
- Reverse engineer or analyze the code structure for derivative purposes.

However, the accompanying **documentation** (such as README, changelog, and usage guides) may be **viewed and shared** for informational or educational purposes.

> The software is provided "as is", without warranty of any kind. The author assumes no liability for any use, misuse, or outcomes resulting from this project.

**Contact:** swarupbaral102@gmail.com

---

## Changelog

All notable changes to this project are documented below.

This project follows [Semantic Versioning](https://semver.org/) and the format is inspired by [Keep a Changelog](https://keepachangelog.com/).

---

### [0.1.1] – 2025-06-28

#### Added

- Automatic execution of setup wizard when running `gfab` command post-installation.
- New prompt for `user_type` to enhance project scaffolding customization.

#### Changed

- Refactored internal structure to avoid circular imports by separating question logic.
- Made the destination folder dynamic in `helper.py` to prevent `KeyError` on missing `destination`.

#### Fixed

- Resolved `ImportError` caused by self-referencing `ask_questions.py`.
- Fixed `KeyError: 'destination'` during project generation.
- Corrected entry point path to ensure the installed CLI tool launches correctly.

---

### [0.1.0] – 2025-06-26

#### Added

- Initial release of GFAB – Gemini Flask App Builder.
- Interactive setup wizard using `questionary` for guided project generation.
- Gemini API key integration via `gemini_helper.py`.
- Support for common project options like:
  - RESTful API routes
  - Jinja2 templating
  - Login/authentication system
  - Role-based access control
  - Database support
  - Static files, blueprints, test setup, PDF export, etc.
- Optional feature selection including WebSocket, Celery, Prometheus, admin dashboard, and others.
