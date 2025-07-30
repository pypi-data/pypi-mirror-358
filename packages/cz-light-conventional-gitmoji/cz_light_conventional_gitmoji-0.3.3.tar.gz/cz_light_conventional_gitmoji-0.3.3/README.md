# cz-conventional-gitmoji

A [commitizen](https://github.com/commitizen-tools/commitizen) plugin that combines [gitmoji](https://gitmoji.dev/) and [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) in a lightweight way.
This fork of [cz-conventional-gitmoji](https://github.com/ljnsn/cz-conventional-gitmoji) adds a `simple-types` and `conventional` option to the template.
We will only have the emojis that are related to the `cz_conventional_commits` types and they will be added to `<subject>` section of the commit message.

```
init: 🎉 initial version
```

## Installation

With `pip` or any other package manager of your choice, the usual way:

```bash
pip install cz-light-conventional-gitmoji
```

## Usage

This package can be used as a normal `commitizen` plugin, either by specifying the name on the command line

```bash
cz --name cz_light_gitmoji commit
```

or by setting it in your **pyproject.toml**

```toml
[tool.commitizen]
name = "cz_light_gitmoji"
```

This will make `commitizen` use the commit message parsing rules defined by this plugin, which are 100% compatible with [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/). As such, the gitmojis are completely optional and all commands will continue to validate commit messages in conventional format just fine. This is useful if you're transitioning an existing repo to `cz-light-conventional-gitmoji` or you work in a team in which some colleagues don't like gitmojis.

### gitmojify

Apart from the conventional-gitmoji rules, this package provides the `gitmojify` command which is also available as a pre-commit hook. The command reads a commit message either from cli or a commit message file and prepends the correct gitmoji based on the type. If the message already has a gitmoji, it is returned as is.

```bash
$ gitmojify -m "init: initial version"
🎉 init: initial version
```

To use it as a pre-commit hook, install this packages as well as `commitizen` and put the following into your **.pre-commit-config.yaml**

```yaml
repos:
  - repo: https://github.com/sasirven/cz-light-conventional-gitmoji
    rev: 0.2.4
    hooks:
      - id: conventional-gitmoji
```

Make sure to install the relevant pre-commit hooks with

```bash
pre-commit install --install-hooks
```

Commit with a message in conventional format that contains a valid type mapped by conventional gitmoji and the gitmoji will automagically be added.

## Features

- [x] Enable conventional gitmoji commit messages via `cz commit`.
- [x] Add hook to automatically prepend the appropriate gitmoji for the commit's type.

## Inspiration

- [`cz-conventional-gitmoji`](https://github.com/ljnsn/cz-conventional-gitmoji) (Forked from)

## Author
- ljnsn (Original Author)
- Samuel Sirven
    - [![Samuel Sirven](https://img.shields.io/badge/-sasirven-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/sasirven)
    - [![Samuel Sirven](https://img.shields.io/badge/-Samuel%20Sirven-0077B5?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/samuel-sirven-b49b53211/)

