# Python mooch.settings

![PyPI](https://img.shields.io/pypi/v/mooch.settings?label=mooch.settings)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mooch.settings)
<img alt="GitHub Issues or Pull Requests" src="https://img.shields.io/github/issues/nickstuer/mooch.settings">

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![license](https://img.shields.io/github/license/nickstuer/mooch.settings.svg)](LICENSE)

This Python package is a collection of useful Python code that is commonly used on all types of Python projects.

## Table of Contents

- [Features](https://github.com/nickstuer/mooch.settings?tab=readme-ov-file#-features)
- [Install](https://github.com/nickstuer/mooch.settings?tab=readme-ov-file#-install)
- [Usage](https://github.com/nickstuer/mooch.settings?tab=readme-ov-file#-usage)
- [Contributing](https://github.com/nickstuer/mooch.settings?tab=readme-ov-file#-contributing)
- [License](https://github.com/nickstuer/mooch.settings?tab=readme-ov-file#-license)

## 📖 Features


### Settings File
Uses a TOML settings file. Easily get/set settingsuration values. Automatically sets values to defaults if they're not currently saved in the settingsuration file.


## 🛠 Install

```
# PyPI
pip install mooch.settings
```
or
```
uv add mooch.settings
```

##  📌 Dependencies
Python 3.9 or greater

## 🎮 Usage

### settings File
```python
from mooch.settings import Settings
default_settings = {
    "settings": {
        "name": "MyName,
        "mood": "happy",
    },
}

settings = Settings("settings.toml", default_settings)

print(settings["settings.mood"])
settings["settings.mood"] = "angry"
print(settings["settings.mood"])
```
## 🏆 Contributing

PRs accepted.

If editing the Readme, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

#### Bug Reports and Feature Requests
Please use the [issue tracker](https://github.com/nickstuer/mooch.settings/issues) to report any bugs or request new features.

#### Contributors

<a href = "https://github.com/nickstuer/mooch.settings/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=nickstuer/mooch.settings"/>
</a>

## 📃 License

[MIT © Nick Stuer](LICENSE)