
![banner](https://raw.githubusercontent.com/asiffer/mkdocs-shadcn/master/.github/assets/banner.png)

![screenshot](https://raw.githubusercontent.com/asiffer/mkdocs-shadcn/master/.github/assets/screenshot2.png)


> [!IMPORTANT]  
> This is an unofficial port of shadcn/ui to MkDocs, and is not affiliated with [@shadcn](https://twitter.com/shadcn).


## Documentation

Yes, yes, the [documentation](https://asiffer.github.io/mkdocs-shadcn/) is built with this theme.

## Quick start

`mkdocs-shadcn` can be installed with `pip`

```shell
pip install mkdocs-shadcn
```

Add the following line to `mkdocs.yml`:

```yaml
theme:
  name: shadcn
```

## Extensions

The theme tries to support the built-in extensions along with some `pymdownx` ones. 

- [x] [`admonition`](https://python-markdown.github.io/extensions/admonition/)
- [x] [`codehilite`](https://python-markdown.github.io/extensions/code_hilite/)
- [x] [`fenced_code`](https://python-markdown.github.io/extensions/fenced_code_blocks/)
- [x] [`pymdownx.tabbed`](https://facelessuser.github.io/pymdown-extensions/extensions/tabbed/)
- [x] [`pymdownx.blocks.details`](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/details/) 
- [x] [`pymdownx.blocks.tab`](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/tab/) 
- [x] [`pymdownx.progressbar`](https://facelessuser.github.io/pymdown-extensions/extensions/progressbar/)
- [x] [`pymdownx.arithmatex`](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/)
- [x] custom [`shadcn.echarts`](https://echarts.apache.org)

## Plugins

We also provides an alpha version of an [`excalidraw`](https://excalidraw.com/) plugin. With this plugin, you can directly edit your excalidraw in dev mode (kind of WYSIWYG) while it is rendered as svg at build time.
