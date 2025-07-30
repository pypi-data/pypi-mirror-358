### How to install

```bash
pip install fig2q
```

Then add a add `FIGMA_TOKEN` .bashrc or .zshrc. For example:

```bash
echo 'export FIGMA_TOKEN=YOURTOKEN' >> ~/.zshrc
```

You can generate a token on your Figma Account page under the Tab "Security".

### How to use

In you project folder, create a file called `q.yaml`.
The file should contain a link to the q-infographic you
want to update, and the links to the figma frames that should be used.

```yaml
- type: infographic
  q: https://qv2.st.nzz.ch/editor/infographic/560x7350xf5bxb3a50cb836998edabcd
  staging: https://qv2.st-staging.nzz.ch/editor/infographic/560x7350xf5bxb3a50cb836998edabcd
  mw: https://www.figma.com/design/26LECd2dAce34lxzgCtala/Mein-Projekt?node-id=1-1787&node-type=FRAME
  cw: https://www.figma.com/design/26LECd2dAce34lxzgCtala/Mein-Projekt?node-id=1-1982&node-type=FRAME
  kw: https://www.figma.com/design/26LECd2dAce34lxzgCtala/Mein-Projekt?node-id=1-1983&node-type=FRAME
  fw: https://www.figma.com/design/26LECd2dAce34lxzgCtala/Mein-Projekt?node-id=1-1984&node-type=FRAME
```

Then run the script with the following command in the folder with the `q.yaml` file:

```bash
fig2q
```

Or pass the path of the file as an argument:

```bash
fig2q path/to/q.yaml
```

Only `mw` and `cw` are required. The other links are optional.
Also, the `staging` link is optional. If it is not provided, the script will not update the staging version of the q-infographic.

You can also use the script to update a scroll_graphic. In this case, the `q.yaml` file should look like this:

```yaml
- type: scroll_graphic
  q: https://qv2.st.nzz.ch/editor/scroll_graphic/599cb06749192d5221a2f8e4dcabcdef
  staging: https://qv2.st-staging.nzz.ch/editor/infographic/560x7350xf5bxb3a50cb836998edabcd
  steps:
      - mw: https://www.figma.com/design/26LECd2dAce34lxzgCtala/Untitled?node-id=1-2&node-type=frame&t=dVqDEKkaO47UMmde-11
        cw: https://www.figma.com/design/26LECd2dAce34lxzgCtala/Untitled?node-id=1-17&node-type=frame&t=dVqDEKkaO47UMmde-11
        text: Text of the first textbox
      - mw: https://www.figma.com/design/26LECd2dAce34lxzgCtala/Untitled?node-id=1-18&node-type=frame&t=dVqDEKkaO47UMmde-11
        cw: https://www.figma.com/design/26LECd2dAce34lxzgCtala/Untitled?node-id=1-19&node-type=frame&t=dVqDEKkaO47UMmde-11
        text: Text of the second textbox
```

## Use it without Figma

If you are not using Figma or don't want to link Frames directly, you can also add image paths.

```yaml
- type: infographic
  q: https://qv2.st.nzz.ch/editor/infographic/560x7350xf5bxb3a50cb836998edabcd
  mw: pngs/mw.png
  cw: pngs/cw.png
```

## Development

You can run the script from a folder like this:

```sh
python -m fig2q q.yaml
```
