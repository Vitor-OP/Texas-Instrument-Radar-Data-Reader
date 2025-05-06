# Radar Recording Parser and Serializer

This Python project is designed to **parse, process, visualize, and serialize radar recordings** (.dat) generated from TI mmWave devices (e.g., AWR2944) configured via SDK configuration files (.cfg). It outputs structured `.mat` files for further data analysis and machine learning applications.

---

## 📁 Project Structure

```
├── main.py
├── classes/
│   ├── class_packet_parser.py
│   ├── class_tlv_parser.py
│   ├── class_configuration_parser.py
│   └── class_recording_serializer.py
```

---

## ⚙️ How It Works

1. **`main.py`**  
   Finds radar `.dat` recordings and their corresponding `.cfg` configuration files, then orchestrates the parsing and serialization.

2. **`PacketParser`**
   - Parses raw binary `.dat` files.
   - Extracts TLV messages (Detected points, Stats, etc.)
   - Generates plots of range, velocity, azimuth, and elevation per frame.

3. **`TLVParser`**
   - Decodes TLV messages based on the mmWave SDK documentation.

4. **`ConfigurationParser`**
   - Parses `.cfg` radar configuration files.
   - Computes physical radar parameters like max range, velocity resolution, etc.

5. **`RecordingSerializer`**
   - Combines parsed data and metrics into a structured dictionary.
   - Saves results as `.mat` files compatible with MATLAB or Python (via `scipy.io.loadmat`).

---

## 🚀 Usage

---

## 🧪 Setting Up a Virtual Environment

To keep your dependencies isolated, it's recommended to use a virtual environment.

### Step-by-step:

1. **Create the virtual environment**

```bash
python -m venv venv
```

2. **Activate the virtual environment**

- On **Linux/macOS**:

```bash
source venv/bin/activate
```

- On **Windows**:

```bash
venv\Scripts\activate
```

3. **Install the dependencies**

Make sure you have a `requirements.txt` file in the root folder, then run:

```bash
pip install -r requirements.txt
```

4. (Optional) **Deactivate the environment when you're done**

```bash
deactivate
```

---

> 💡 Tip: You can generate a `requirements.txt` file with your current environment using:

```bash
pip freeze > requirements.txt
```

### 🧪 Command Line Interface

```bash
python main.py <path_to_test_folder> [--no_plot]
```

- `path_to_test_folder`: A directory containing one or more subfolders, each holding a `.cfg` and recordings in `.dat` format.
- `--no_plot`: (Optional) Disable generation of `.png` timeline plots.

### 📂 Folder Structure Example

```
test_folder/
└── Config_01/
    ├── config.cfg
    └── Scene_01/
        └── recording.dat
```

> Each config folder must contain **one** `.cfg` file and any number of recording folders (each with **one** `.dat` file).

---

## 📦 Output

For each `.dat` file:
- A `.mat` file is generated in the same directory, with keys matching the radar interface ISO format.
- A `.png` plot showing detection timelines is also saved unless `--no_plot` is set.

---

## 🧰 Dependencies

Make sure to install the following Python packages:

```bash
pip install numpy matplotlib scipy
```

---

## ✍️ Notes

- Tested with mmWave SDK version `04.07.00.01`.
- Ensure `.cfg` files conform to TI's formatting; newer SDKs may require changes in parsing logic.
- You can explore individual classes for advanced usage or data inspection (e.g., `PacketParser.plot_detections_timeline()`).

---

## 📬 Contact

For questions or feedback, feel free to open an issue or contact the author directly.
