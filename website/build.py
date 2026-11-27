"""Build the public guide site from committed Markdown, never the working tree."""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUTPUT = REPO / "build" / "online-guide"
PROJECT = "https://github.com/Prophet60191/m5stack-cardputer-zero-app-guide"
HOME = "https://prophet60191.github.io/m5stack-cardputer-zero-app-guide/"
LINK = re.compile(r"\[([^\]\n]+)\]\(([^()\s]+)\)")


def git(*args, **kwargs):
    return subprocess.run(["git", "-C", str(REPO), *args], **kwargs)


def build():
    revision = git("rev-parse", "HEAD", capture_output=True, check=True, text=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="cardputer-guide-") as tmp:
        scratch = Path(tmp).resolve()
        source = scratch / "source"
        source.mkdir()
        git("archive", f"--output={scratch / 'source.tar'}", revision, "docs", "README.md", "LICENSE", check=True)
        with tarfile.open(scratch / "source.tar") as archive:
            archive.extractall(source, filter="data")
        stage = scratch / "stage"
        stage.mkdir()
        shutil.copytree(source / "docs", stage / "docs")
        shutil.copyfile(source / "LICENSE", stage / "LICENSE.txt")
        (stage / "source-revision.txt").write_text(revision + "\n")
        (stage / "styles").mkdir()
        shutil.copyfile(HERE / "reader.css", stage / "styles" / "reader.css")

        def rewrite(text, original, output):
            def convert(match):
                label, address = match.groups()
                if address.startswith(("#", "https://", "http://", "mailto:")):
                    return match.group()
                rel, separator, fragment = address.partition("#")
                path = (original.parent / rel).resolve().relative_to(source).as_posix()
                if fragment == "develop-in-the-desktop-simulator--and-why":
                    fragment = "develop-in-the-desktop-simulator-and-why"
                tail = separator + fragment
                if path == "README.md":
                    prefix = "../" * (len(output.relative_to(stage).parts) - 1)
                    return f"[{label}]({prefix}index.md{tail})"
                if (source / path).is_file() and path.startswith("docs/"):
                    return f"[{label}]({rel}{tail})"
                if git("cat-file", "-e", f"{revision}:{path}", capture_output=True).returncode:
                    raise ValueError(f"Missing source link in {original.name}: {address}")
                return f"[{label}]({PROJECT}/blob/{revision}/{path}{tail})"
            return LINK.sub(convert, text)

        for original in (source / "docs").rglob("*.md"):
            output = stage / original.relative_to(source)
            output.write_text(rewrite(original.read_text(), original, output))
        original = source / "README.md"
        output = stage / "index.md"
        readme = original.read_text().replace(f"**[Read the online guide]({HOME})**\n\n", "", 1)
        readme = re.sub(r"^<h1[^>]*>.*?</h1>", "# Building apps for the Cardputer Zero", readme, count=1)
        output.write_text(rewrite(readme, original, output)
                          + f"\n\n---\n\n[Guide source on GitHub]({PROJECT}/tree/{revision})"
                          + " · [Documentation license](LICENSE.txt)\n")
        shutil.copyfile(HERE / "mkdocs.yml", scratch / "mkdocs.yml")
        subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict",
                        "-f", str(scratch / "mkdocs.yml"), "-d", str(OUTPUT)], check=True)
        assert (OUTPUT / "index.html").is_file() and (OUTPUT / "search/search_index.json").is_file()


if __name__ == "__main__":
    build()
