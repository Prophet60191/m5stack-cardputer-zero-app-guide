# Maintaining the online guide

Edit the Markdown and images in the guide's `docs/` directory and top-level
`README.md`. No duplicate website chapters are maintained. A push or merge to
`main` builds the website, its search index and the source revision marker.
Branches, pull requests and uncommitted local files are not deployed.

For a local check of your committed branch:

```sh
python3 -m pip install -r website/requirements.txt
python3 website/build.py
python3 -m http.server --bind 127.0.0.1 --directory build/online-guide 8765
```

For a new chapter, add its link in the guide's contents and, if appropriate,
in `website/mkdocs.yml`. MkDocs indexes content even without a sidebar entry.
Check **Actions → Publish online guide** for deployment status. Fix build
errors on the source branch rather than editing the generated website.
