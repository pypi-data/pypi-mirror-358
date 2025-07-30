# Install Python

The following describes how to set up your development environment for working on this project.
For this specific tutorial we will be installing Python 3.8, but you can install any version
you like (recommend installing the latest).

## `pyenv`

[pyenv](https://github.com/pyenv/pyenv) is a Python version manager written in shell script;
it allows you to install and manage different version of python.
See [this](https://github.com/pyenv/pyenv#installation) guide on installation.
Once installed simply run:

```shell
pyenv install 3.8
```

> [!TIP]
> See [this](https://github.com/pyenv/pyenv#usage) for more info on usage.

## `uv`

> [!TIP]
> This is the recommended way of installing Python.

[uv](https://docs.astral.sh/uv/) is an Python package and project manager.
It has many useful features, including the ability to download and manage different
Python versions.

> [!TIP] Installation
> See [this](https://docs.astral.sh/uv/getting-started/installation/) guide on
> installation.

To install - say - Python 3.8, run:

```shell
uv python install 3.8
```

> [!TIP] Usage
> See [this](https://docs.astral.sh/uv/guides/install-python/#getting-started)
> for more info on usage.

## Unix/MacOs

If you are using a Unix-based (like Linux) or Unix-like (like MacOS) system, you can find Python
in your prefered package manager.

/// tab | Ubuntu

> [!TIP]
> On some version of Ubuntu you may need to use the
> [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa)
> repository to install Python.
>
> If you are on such a version, run this command first:
>
> ```shell
> sudo apt-get install software-properties-common
> sudo add-apt-repository ppa:deadsnakes/ppa
> ```
>
> Then run the below:

```shell
sudo apt-get update
sudo apt-get install python3.8 # install Python 3.8
```

///

/// tab | Fedora

```shell
sudo dnf install python3.8
```

///

/// tab | Arch

> [!TIP]
> If you have an AUR helper like [`yay`](https://github.com/Jguer/yay),
> you can specify the specific Python package you want in the
> [Arch User Repository](https://aur.archlinux.org/packages) (**AUR**):
> `yay -S python38`

```shell
sudo pacman -S python3.8
```

///

/// tab | macOs

> [!TIP] Homebrew Installation
> If you do not have [Homebrew](https://brew.sh/) installed on your OS X terminal,
> you can install it using the following command:
>
> ```shell
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
> ```

```shell
brew install python3.8
```

///

## Windows

See [this](https://www.geeksforgeeks.org/how-to-install-python-on-windows/) guide
on how to install Python on Windows.
