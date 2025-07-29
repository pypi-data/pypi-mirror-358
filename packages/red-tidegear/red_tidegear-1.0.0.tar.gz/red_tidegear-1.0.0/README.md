# Tidegear

[![Discord](https://img.shields.io/discord/1070058354925383681?logo=discord&color=%235661f6)](https://discord.gg/eMUMe77Yb8)
![Python Versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fc.csw.im%2Fcswimr%2FCogUtils%2Fraw%2Fbranch%2Fmain%2Fpyproject.toml&logo=python)

A collection of utilities for use with [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot), made for [SeaCogs](https://c.csw.im/cswimr/SeaCogs).

## Metadata File

The cog class provided by [`tidegear.Cog`](./tidegear/cog.py) requires consuming cogs to have a `meta.json` file in your cog's bundled data directory. The `meta.json` file must match the schema provided in [`schema/meta/meta.json`](./schema/meta/meta.json). An example file is located at [`scheme/meta/meta.example.json`](./schema/meta/meta.example.json). Additional keys are disallowed by the schema but will not cause errors.

## Developing

You'll need some prerequisites before you can start working on CogUtils.  
[git](https://git-scm.com) - [uv](https://docs.astral.sh/uv)  
Additionally, I recommend a code editor of some variety. [Visual Studio Code](https://code.visualstudio.com) is a good, beginner-friendly option.

### Installing Prerequisites

_This section of the guide only applies to Windows systems.
If you're on Linux, refer to the documentation of the projects listed above. I also offer a [Nix Flake](./flake.nix) that contains all of the required prerequisites, if you're a Nix user._

#### [`git`](https://git-scm.com)

You can download git from the [git download page](https://git-scm.com/downloads/win).

Alternatively, you can use `winget`:

```ps1
winget install --id=Git.Git -e --source=winget
```

#### [`uv`](https://docs.astral.sh/uv)

You can install uv with the following Powershell command:

```ps1
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Alternatively, you can use `winget`:

```ps1
winget install --id=astral-sh.uv -e
```

### Getting the Source Code

Once you have [`git`](https://git-scm.com) installed, you can use the `git clone` command to get a copy of the repository on your system.

```bash
git clone https://c.csw.im/cswimr/tidegear.git
```

Then, you can use `uv` to install the Python dependencies required for development.

```bash
uv sync --all-groups --all-extras --frozen
```
