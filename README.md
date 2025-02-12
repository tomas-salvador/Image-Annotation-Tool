# Image Annotation Tool

A **PyQt5-based** desktop application for annotating images with **bounding boxes**. Each bounding box can be labeled with a text tag, drawn in a **distinct color**, and displayed **outside** (above-left corner) of the bounding box.

This tool supports:
- Opening **multiple images** at once.
- Navigating through images using **Space** or **Right Arrow** (next) and **Left Arrow** (previous).
- **Drawing** rectangular annotations with the left mouse button.
- **Resizing** each bounding box by dragging its edges or corners.
- Assigning a **color** to each annotation from a palette of 10 colors (repeating if necessary).
- Zooming **around the mouse position** using **Ctrl** or **Shift** + scroll wheel.
- Storing bounding boxes in a TXT file per image with a format reminiscent of COCO-like notation but simplified (`[label x_center y_center width height]` in normalized coordinates).
- Persisting the **last used label** across images (so if you label something "Ball" in one image, the next new annotation in any image uses "Ball" by default).

## Features

1. **Multiple Image Support**  
   Select multiple images in the file dialog. Once opened, the first image loads automatically. Use **Space** / **Right Arrow** to move forward, and **Left Arrow** to move backward.

2. **Annotation Flow**  
   - **Create an annotation** by left-clicking and dragging on the image.  
   - **Resize** an annotation by grabbing its edges/corners.  
   - **Label** an annotation by double-clicking it in the list, or using the “Assign label to selected” button.  
   - **Delete** an annotation by selecting it in the list and clicking the "Eliminar anotación" button.

3. **Last-Used Label**  
   The application always remembers the last label you typed or assigned. Switching images does not discard it. Therefore, if your last label was "Ball", drawing a new bounding box on a different image automatically starts with "Ball".

4. **TXT Format**  
   Each image has a corresponding `.txt` file using lines in the form:
   ```txt
   <label> <x_center_normalized> <y_center_normalized> <width_normalized> <height_normalized>
Where:

- **label**: Your annotation text (e.g., "Ball").
- **x_center_normalized**, **y_center_normalized**: Coordinates of the bounding box center, in `[0..1]`.
- **width_normalized**, **height_normalized**: Size of the bounding box, also in `[0..1]`.

This is loosely inspired by **COCO** / **YOLO**-like bounding-box formats, but simplified to a TXT file rather than JSON.

## Color Palette

A set of **10 predefined colors** is used for bounding boxes. Once the 10th color is assigned, it loops back to the first. The same color is used as the **background** of the annotation item in the right-hand list.

## Zoom

- **Ctrl** or **Shift** + mouse wheel zooms around the **mouse position**.  
- If you only scroll without Ctrl or Shift, it will not zoom (default behavior).

## Tested Platforms

- **Ubuntu**: Verified to work on Python 3.x with PyQt5 installed.
- Likely works on **Windows** and **macOS** as well, but not extensively tested.

## Installation and Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/<repository-name>.git
   cd <repository-name>
Install dependencies:

```bash
pip install pyqt5
Or use an environment of your choice (e.g., Conda).

### Run the tool:

```bash
python main.py
(Replace `main.py` with your actual script name if different.)

### Usage:

- Click **"Abrir imagen(es)"** to open one or more images.
- Select or create bounding boxes in the left pane.
- The right-hand list displays annotations; double-click or use the buttons to label or delete.
- Press **Space** or **Right Arrow** to go to the next image, **Left Arrow** to go back.
- Zoom with **Ctrl** or **Shift** + scroll wheel.

---

## Contributing

Feel free to open Issues or submit Pull Requests if you want to improve or extend the functionality.

---

## License

Distributed under the [MIT License](LICENSE).
