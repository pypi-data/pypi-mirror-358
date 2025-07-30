# SCPYGEN 🚀

SCPYGEN is a Python CLI tool that instantly generates production-ready Flask project skeletons. Whether you need a minimal API or a full-stack Flask app (with templates, static files, and blueprints), SCPYGEN saves you time creating your project.

## Features ✨

- Interactive CLI: Choose between a Flask API or a full-stack Flask app with a single command.
- Best Practices: Projects include blueprints, config, models, migrations, .env, and more.
- Customizable: Generated code is modular and easy to extend.
- Fast Start: Go from zero to a working Flask project in seconds.

## Installation ⚙️

Install via pip:

```bash
pip install scpygen
```

## Usage 🖥️

Run the CLI in your terminal:

```bash
scpygen
```

You’ll be prompted to choose:

```bash
1: Flask API Skeleton (RESTful, no frontend)
2: Flask Full Stack Application (with templates, static, and database models)
```

Then enter your project name. scpygen will generate a new folder with all required files and folders.

Example Output Structure

For a Flask API Skeleton:
```bash
my-flask-api/
├── run.py
├── requirements.txt
├── .env
├── api/
│   ├── __init__.py
│   ├── config/
│   ├── models/
│   ├── routes/
│   └── ...
├── tests/
└── ...
```

For a Full Stack Flask App:
```bash
my-flask-app/
├── run.py
├── requirements.txt
├── .env
├── app/
│   ├── __init__.py
│   ├── templates/
│   ├── static/
│   ├── models/
│   ├── routes/
│   └── ...
├── tests/
└── ...
```

## Change Log 📄
You can view the Change Log [HERE](https://github.com/xShadowCodingx/scpygen/blob/prod/changelog.md).

## License 🪪
This project is licensed under the MIT License - see the [LICENSE](https://github.com/xShadowCodingx/scpygen/blob/prod/LICENSE) file for details.