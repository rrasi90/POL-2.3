---
name: doory-template-import
description: Comprehensive verified guide and toolset for importing JSON design templates into Doory via Django management commands and direct ORM injection.
license: MIT
metadata:
  version: 1.0.0
  category: design-tooling
  domain: doory
  tags: [doory, template, import, django, fabricjs, json]
---

# Doory Template Import Skill (`doory-template-import`)

This skill documents the exact, verified facts, constraints, and commands for importing design templates and projects into local Doory (`C:\Star\Nima instagram\doory`).

## 1. Verified Architecture & Ingestion Paths

Doory supports two primary ingestion mechanisms:

### Method A: Gallery Template Ingestion (Public / Reusable)
- **Engine:** `apps.gallery.management.commands.import_template`
- **Execution:**
  ```powershell
  & "C:\Star\Nima instagram\doory\backend\.venv\Scripts\python.exe" manage.py import_template <path_to_template.json> --publish --create-categories
  ```
- **Schema:**
  ```json
  {
    "title": "عنوان قالب",
    "slug": "template-slug",
    "category": "mobile-app",
    "preset": "mobile-app",
    "tags": ["فارسی", "پل", "اپلیکیشن"],
    "description": "توضیحات قالب",
    "is_published": true,
    "document": {
      "schemaVersion": 1,
      "width": 390,
      "height": 844,
      "unit": "px",
      "pages": [
        {
          "id": "uuid-v4",
          "name": "عنوان صفحه",
          "background": { "type": "solid", "color": "#F5F7FA" },
          "objects": []
        }
      ]
    }
  }
  ```

### Method B: Direct User Design Project Creation (Editable in Editor)
- **Target URL:** `http://localhost:5173/design/<hyphenated-uuid>`
- **Database Model:** `apps.designs.models.Design`
- **Owner Requirement:** Must be linked to an authenticated `accounts_user` (e.g. `pol.test@local.dev`).
- **UUID Format Requirement:** Frontend router strictly expects 36-char hyphenated UUID (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
- **Objects Hierarchy:**
  - `textbox`: `"direction": "rtl"`, `"fontFamily": "\"Vazirmatn\", sans-serif"`, `"charSpacing": 0`, `"textAlign": "right"` or `"center"`.
  - `rect`: `"rx": 12`, `"ry": 12`, `"fill": "#246BFD"`.
  - `image`: `"type": "image"`, `"src": "data:image/..."` or valid static URL.
