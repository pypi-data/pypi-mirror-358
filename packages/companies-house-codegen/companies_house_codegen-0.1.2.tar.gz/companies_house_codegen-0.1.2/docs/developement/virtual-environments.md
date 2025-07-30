# Python Virtual Environments

It is recommended to create a **virtual environment** to isolate packages you install for each project.

> [!NOTE]
> If you already know about virtual environments, or you do not mind installing Python packages system-wide, you may skip this tutorial.

## What Is A Virtual Environment

In Python programming, a **virtual environment** is an a directory containing various files that can be used to create the isolated environment. This allows you to manage project specific dependencies without interfering with other projects or the original Python installation.

## Creating Virtual Environment

There are multiple tools that can be used to create a virtual environment in Python. Here are a few of them.

## Creating Virtual Environment Using `virtualenv`

[virtualenv](https://github.com/pypa/virtualenv) is a third party CLI tool that creates
Python virtual environments. It is very similar to [venv](#creating-virtual-environment-using-venv).

First you must install virtualenv:

=== "pip"
    ```shell
    pip install virtualenv
    ```

=== "pipx"
    ```shell
    # install in an isolated environment
    pipx install virtualenv
    ```

To create a new virtual environment simply run the following:

```shell
# creates a virtual environment stored in the directory `./venv/`
python -m venv venv
```

Once you’ve created a virtual environment, you may activate it.

/// tab | Unix/macOS

```bash
source ./venv/bin/activate
```

///

/// tab | Windows

```powershell
.\venv\Scripts\activate.bat
```

///

For Python 3.3+, it is generally recommended to use [venv](#creating-virtual-environment-using-venv)
over virtualenv.

### Creating Virtual Environment Using `venv`

Introduce in Python 3.3, [venv](https://docs.python.org/3/library/venv.html) is a
Python standard library module that can be used to create virtual Python environments. 

To create a new virtual environment simply run the following:

```shell
# creates a virtual environment stored in the directory `./venv/`
python -m venv venv
```

Once you’ve created a virtual environment, you may activate it.

/// tab | Unix/MacOS

```shell
source ./venv/bin/activate
```

///

/// tab | Windows

```powershell
.\venv\Scripts\activate.bat
```

///

You can manage python packages in a `venv` virtual environment [using pip](https://docs.python.org/3/tutorial/venv.html#managing-packages-with-pip)

`venv` is the most convient way of creating virtual environments.

## Creating Virtual Environment Using `uv`

> [!TIP]
> `uv` is considered to be the best tool
> for managing python environments.

[uv](https://docs.astral.sh/uv/) is an exceptionally Python package and project manager.
Amongst its many tool is [`uv venv`](https://docs.astral.sh/uv/pip/environments/),
a tool that functionally equivalently to `venv` in usage; most of what applies to `venv`
applies to `uv venv`. Note that you should use `uv pip` over `pip` when
using an environment created by `uv env`. See more information at the
[official docs](https://docs.astral.sh/uv/pip/environments)

> [!TIP] Environment Naming Conventions
> If you are using Astral's (the creators of `uv`) ecosystem
> name whatever environmets you create `.venv` rather than `venv`
> to make them discoverable
