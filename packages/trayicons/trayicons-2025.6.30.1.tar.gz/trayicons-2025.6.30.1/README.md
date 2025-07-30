# trayicons

<a href="https://pypi.org/project/trayicons/">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/trayicons">
</a>

 Previewing your tray icons made easy!

 Currently only support Krita files. Feature contributions are welcome.

## install

`pip install trayicons`

or as a dependency:

`uv add trayicons`

## Usage

Create an `icons.toml` with the following content:

```toml
[[icon]]
src = "demo.kra"
dst = "./demo.ico"
```

Then run `trayicons -c icons.toml`. Multiple icons are supported.

The icon will update once you save the Krita file. This ensure realtime previewing and a streamlined experience.

Use Ctrl+C or right click in the taskbar icon to exit.

## Example

Clone [the repo][repo], then run `trayicons -c tests/icons.toml`

[repo]: https://github.com/soda92/trayicons
