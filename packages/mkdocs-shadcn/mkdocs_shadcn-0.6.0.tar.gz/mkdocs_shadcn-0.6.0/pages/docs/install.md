---
title: Install
---

Add the package to your project.

=== "pip"

        :::bash
        pip install mkdocs-shadcn


=== "uv"

        :::bash
        uv add mkdocs-shadcn

=== "poetry"

        :::bash
        poetry add mkdocs-shadcn


Configure MkDocs:

```yaml
# mkdocs.yml
site_name: "awesome-project"
theme:
  name: shadcn
  pygments_style: dracula # set by default
  icon: heroicons:rocket-launch # use the shadcn svg by default
```

Currently there are not many options and they are likely to change. You can define an `icon` (image url or [iconify class](https://icon-sets.iconify.design/)) for the top bar.