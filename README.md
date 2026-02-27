# 📦 OPEN KITBASH for 3ds Max +2026

Developed by: Iman Shirani

[![Donate ❤️](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4)

**OPEN KITBASH** is a powerful, smart, and highly responsive kitbashing and asset management tool built with Python (PySide6) for Autodesk 3ds Max. It streamlines the hard-surface modeling, environment design, and concept art workflow by allowing artists to instantly browse, insert, and manipulate 3D assets with zero friction.

![Open Kitbash UI](screenshot/screenshot.jpg) *(Note: Add a screenshot of your beautiful UI here)*

---

## ✨ Key Features

### 🚀 Smart Asset Browser
* **Multi-Format Support:** Instantly import `.max`, `.obj`, and `.fbx` files.
* **Responsive Grid:** The UI automatically calculates columns and resizes the grid based on your window size.
* **Async Image Loading:** Thumbnails load in the background (Lazy Loading) to prevent 3ds Max from freezing, even with folders containing hundreds of assets.
* **Library Management:** Create folders, rename assets, delete files, and update thumbnails directly from the UI with Right-Click context menus.
* **Favorites System:** Bookmark your most-used assets for quick access.

### 🎛️ Live Transformation System
* **Draggable Spinboxes:** Seamlessly move, rotate, and scale assets by dragging the values in the UI.
* **Independent Axis Memory:** Rotate on the X-axis, switch to Z, and keep your X rotation perfectly intact. The tool remembers every axis value independently.
* **Live Placement:** Assets are merged directly to the center of your selected target (or world origin) and can be offset live before committing.
* **Quick Mirror & Reset:** 1-click mirroring on any axis and a master reset button for all transforms.

### 🛠️ Quick Modifiers (Optimized for Max 2026)
1-click access to the most essential kitbashing modifiers with smart default settings:
* **🔗 Conform:** Instantly wrap your kitbash pieces onto the surface of a target object.
* **✂️ Boolean:** Add the new Boolean Explorer modifier for rapid cutting.
* **💠 Array:** Create complex radial or grid patterns instantly.
* **🦋 Symmetry:** Live mirroring for weapon and vehicle design.
* **✨ Chamfer:** Smooth out sharp boolean cuts with smart weighted chamfers.
* **📦 FFD 3x3x3 & ↪ Bend:** Deform and bend hard-surface parts to fit organic shapes.

### 📸 Auto-Thumbnail Generation
Save any selected objects in your scene directly into your library! The tool automatically frames the object, takes a viewport snapshot, clears memory, and saves it alongside your new `.max` file.

---

## ⚙️ Requirements
* **Autodesk 3ds Max:** 2026 recommended (relies on newer modifiers like Boolean Explorer and Conform), but core features work on 2024+.
* **Python Environment:** Uses the native `pymxs` and `PySide6` included with modern 3ds Max installations.

---

## 📥 Installation

1. **Download the Repository:**
   Click `Code > Download ZIP` or clone the repository to your local machine.
2. **Extract:** Extract the `OPEN_KITBASH` folder to your 3ds Max scripts directory (e.g., `C:\Users\YourName\AppData\Local\Autodesk\3dsMax\2026 - 64bit\ENU\scripts`).
3. **Run in 3ds Max:**
   * Open 3ds Max.
   * Go to `Scripting > Run Script...`
   * Navigate to the extracted folder and run the `launcher.py`file.
   

---

## 📖 How to Use

### 1. Setting Up Your Library
* Click the **⚙ Settings** button in the top right corner.
* Select the root folder where you want to keep your 3D assets.
* OPEN KITBASH will instantly scan the folder and build your library tree.

### 2. Inserting Assets
* Browse your folders or use the **Search Bar** to find an asset.
* Click the **INSERT** button on any asset card.
* If you have an object selected in your scene, the asset will snap to it. Otherwise, it spawns at `[0,0,0]`.

### 3. Live Transforming & Committing
* Use the **Live Transformation** section to adjust the Position Offset, Rotation, and Scale.
* Click any modifier button (e.g., **Chamfer** or **Symmetry**) to apply them dynamically.
* Once you are happy with the placement, click the green **✅ APPLY & COMMIT** button to collapse the history and finalize the asset.

### 4. Adding Your Own Assets
* Select any geometry in your 3ds Max viewport.
* Click **➕ Add Selection to Library**.
* Choose a category folder and name your asset. The tool will handle the rest (saving the `.max` file and generating the thumbnail).

---

## 👨‍💻 Author
**Iman Shirani** *3D Artist & Tools Developer*

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
