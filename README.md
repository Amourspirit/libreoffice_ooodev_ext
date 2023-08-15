<p align="center">
<img src="https://user-images.githubusercontent.com/4193389/260558706-6a975af5-0815-4d85-987a-6f8b3ff20609.png" alt="OooDev Logo" width="174" height="174">
</p>

# OOO Development Tools Extension

This project brings to power of [OOO Development Tools] (OooDev) to LibreOffice as an extension.

[OOO Development Tools] can be [pip installed](https://pypi.org/project/ooo-dev-tools/) or [compiled into a macro](https://oooscript.readthedocs.io/en/latest/); However, this can be cumbersome that is the reason for this project.

By installing this extension you can have the power of [OOO Development Tools] at your fingertips with no extra need to pip install or compile into a macro.

On LibreOffice Extensions the `OooDev` extension can be found [here](https://extensions.libreoffice.org/en/extensions/show/41700), locally the `OooDev` extension can is found in the [dist](dist) folder.

<details>
<summary>Develop Notes</summary>

## Development

To update the extension from the development container, run the following command:

```bash
poetry update
```

This command will install the latest version of [OOO Development Tools].

Edit the `pyproject.toml` file and update the version number.

Then run the following command:


```bash
python -m app build
```

This command will build the extension and place it in the [dist](dist) folder. The build command also will automatically update the `dist/ooodev.ext.update.xml`. That's it. You can now install the extension.

</details>

This project is based upon the [Live LibreOffice Python](https://github.com/Amourspirit/live-libreoffice-python) template. Beleow is the original readme from the template.

<details>
<summary>Original Template Readme</summary>

# Live LibreOffice Python

Live LibreOffice Python is a complete development environment for creating, debugging and testing python scripts. It leverages the power of [VS Code] and has [LibreOffice] baked in that can be access via the internal web browser or via your local web browser which allows for a much more pleasant and consistent debugging experience.

With the power of [GitHub Codespaces](https://docs.github.com/en/codespaces/overview) it is possible to have [VS Code] and [LibreOffice] running together. One big benefit is a isolated and [VS Code]/[LibreOffice] environment.

Locally a project based upon this template can also be run in a [Development Container](https://code.visualstudio.com/remote/advancedcontainers/overview).

It is also possible to use [GitHub CLI/CD] to create a workflow that test your project with the presents of LibreOffice. This template has a working example of testing using [GitHub CLI/CD].

There are Built in [Tools](https://github.com/Amourspirit/live-libreoffice-python/wiki/Tools) such as [gitget](https://github.com/Amourspirit/live-libreoffice-python/wiki/Tools#gitget) that allow you to quickly add examples to your project from sources such as [LibreOffice Python UNO Examples]. Also there is a built in [console](https://github.com/Amourspirit/live-libreoffice-python/wiki/Console) to help debug the [API](https://api.libreoffice.org/).

This templated can also be leveraged to demonstrate working examples of code.

[![image](https://github.com/Amourspirit/live-libreoffice-python/assets/4193389/35758c26-63b7-48f9-99c0-84dd19b26a8f)](https://github.com/Amourspirit/live-libreoffice-python/assets/4193389/35758c26-63b7-48f9-99c0-84dd19b26a8f)

## Getting Started

See the [Getting Started](https://github.com/Amourspirit/live-libreoffice-python/wiki/Getting-Started) in the [Wiki](https://github.com/Amourspirit/live-libreoffice-python/wiki).

</details>

[VS Code]:https://code.visualstudio.com/

[LibreOffice]:https://www.libreoffice.org/
[GitHub CLI/CD]:https://resources.github.com/ci-cd/
[LibreOffice Python UNO Examples]:https://github.com/Amourspirit/python-ooouno-ex
[OOO Development Tools]: https://python-ooo-dev-tools.readthedocs.io/en/main/index.html