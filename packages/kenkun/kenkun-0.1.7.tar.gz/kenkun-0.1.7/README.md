# Kenkun Project

## Overview
Welcome to the Kenkun Project! This project aims to be a scaffolding tool for python web projects. 
It is designed to help developers quickly create new projects with a predefined structure and configuration.
The project is currently in development and is not yet ready for production use.

## Features
- Feature 1: Create diferent types of web applications, such as Flask, FastHTML and FastHTML standalone.
- Feature 2: Model driven development, with automatic generation of models, views and controllers.

## Installation
To install the necessary dependencies, run the following command:
```bash
pip install kenkun
```

Once installed. Create a configuration file in the root of your project with the following content, inserting your Github access properties:
```python
# Github access properties
GITHUB_USER=''
GITHUB_TOKEN=''
GITHUB_URL=f''
```

## Usage
To start the project, use the following command:
```bash
kk create -a [project-name]
```

To generate a new model, use the following command:
```bash
kk domain -d [model-name]
```

To generate all: views, controllers and models, use the following command:
```bash
kk all -d [model-name]
```

For detailed usage instructions, refer to the [documentation](https://github.com/sylvioazevedo/kenkun/wiki).

## Contributing
We welcome contributions! Please see our [contributing guidelines](https://github.com/sylvioazevedo/kenkun) for more details.

## License
This project is licensed under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Contact
For any questions or feedback, please contact <sylvioazevedo@gmail.com>.
