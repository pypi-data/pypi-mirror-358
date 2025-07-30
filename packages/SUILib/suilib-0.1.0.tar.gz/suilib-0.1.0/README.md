# SUILib
_✨ A simple lightweight UI library for Pygame ✨_

![PyPI - License](https://img.shields.io/pypi/l/suilib?style=flat-square)
![Python Version](https://img.shields.io/pypi/pyversions/suilib?style=flat-square)
![Pygame](https://img.shields.io/badge/Pygame-Compatible-brightgreen?logo=pygame&logoColor=white&style=flat-square)

SUILib is a simple, flexible UI library for [Pygame](https://www.pygame.org/).  
Easily build interactive applications or games with multiple views, rich UI elements, and customizable stylesheets.  
Switch between light and dark themes, or define your own look!

## 🔍 Preview

> Light theme  
<img src="./preview/img1.png" width="48%"> <img src="./preview/img2.png" width="48%">

> Dark theme  
<img src="./preview/img3.png" width="48%">

## ✨ Features & Elements

**Main Components**
- ` Application `  ` View `  ` StyleManager `

**Layouts**
- ` RelativeLayout `  ` AbsoluteLayout `

**UI Elements**
- ` Label `  ` Panel `  ` Button `  ` ToggleButton `  ` TextInput `  ` CheckBox `  
- ` RadioButton `  ` RadioButtonGroup `  ` ComboBox `  ` TabPanel `  ` Tab `  
- ` ListPanel `  ` Table `  ` Canvas `  ` Image `  ` Graph `  
- ` HorizontalScrollbar `  ` VerticalScrollbar `  ` Slider `  

**Graphics**
- ` Vertex `  ` Edge `  ` Wireframe `

**Utils**
- ` colorChange `  ` colorAdd `  ` colorInvert `  ` createColor `  
- ` overrides `  ` inRect `  ` generateSignal `  ` loadImage `  ` drawGraph `  
- ` loadConfig `  ` getDisplayWidth `  ` getDisplayHeight `  ` runTaskAsync `

## 📚 Documentation

Documentation is available in the docs folder or here on GitHub.  
[SUILib Documentation](https://0xmartin.github.io/SUILib/)

## 🚀 Installation

**Install from PyPI (recommended):**
```sh
pip install suilib
```

**_Optional: Prepare a virtual environment first (recommended):_**
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install locally from source (development mode):**

1. Clone this repository:
    ```sh
    git clone https://github.com/0xMartin/SUILib.git
    cd SUILib
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Install SUILib in development mode:
    ```sh
    pip install -e .
    ```

## License

Released under the [MIT License](https://opensource.org/licenses/MIT).  
© Martin Krcma