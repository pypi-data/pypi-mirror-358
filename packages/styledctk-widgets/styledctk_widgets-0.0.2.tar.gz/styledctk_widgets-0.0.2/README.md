# styledctk-widgets

[![PyPI - Version](https://img.shields.io/pypi/v/styledctk-widgets.svg)](https://pypi.org/project/styledctk-widgets)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/styledctk-widgets.svg)](https://pypi.org/project/styledctk-widgets)

-----

## Table of Contents

- [styledctk-widgets](#styledctk-widgets)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [License](#license)
- [Example](#example)

## Installation

```console
pip install styledctk-widgets
```

## License

`styledctk-widgets` is distributed under the terms of the following  [License](License) license.

# Example
In the example, a SCTkButton is used. The theme number is 1, and the style number is 3

```python
import styledctk_widgets.CTK_Buttons.SCTkButton as SCTk_B
import customtkinter as ctk


def oneB():
    main_window = ctk.CTk()
    main_window.geometry("300x200")
    main_window.title("Testing the library")
    
    but= SCTk_B.SCTkButton(main_window, theme=1,style=3)
    but.pack(padx=20,pady=20)
    
    main_window.mainloop()
    
    
if __name__=="__main__":
    oneB()
```