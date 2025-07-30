from pathlib import Path
import glob
import hashlib
import json
import sys

from docutils import nodes
from nltk.tokenize import word_tokenize


# TODO: Create setup function

# TODO: core can have one version of searchtools.js that contains the common logic.
# clients can provide a little more js for their custom needs. core will inject the
# client custom logic into a certain location. maybe it's searchtools.tmpl in core
# core and then client.js


def _embeddings_dir(srcdir):
    return Path(srcdir) / Path("embeddings")


def _data_dir(srcdir):
    return _embeddings_dir(srcdir) / Path("data")


def init(app, static_dir):
    # Create embeddings dir
    embeddings_dir = _embeddings_dir(app.srcdir)
    data_dir = _data_dir(app.srcdir)
    if not embeddings_dir.is_dir():
        embeddings_dir.mkdir(exist_ok=False, parents=False)
    if not data_dir.is_dir():
        data_dir.mkdir(exist_ok=False, parents=False)
    # Add embeddings dir to static path
    # TODO: Only add embeddings.json to static path
    # TODO: Maybe expose it as a JS file so that you can add with add_js_file()?
    app.config.html_static_path.append(str(embeddings_dir.absolute()))
    # Add client's static dir
    app.config.html_static_path.append(str(static_dir.absolute()))
    # Create script tag for JS file in client's static dir
    app.add_js_file("searchtools2.js", type="module")


def compute_checksum(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def save(srcdir, docname, embeddings):
    # [docName, title, anchor, descr, score, _filename, kind]
    filename = _to_filename(docname)
    path = _data_dir(srcdir) / Path(f"{filename}.json")
    with open(path, "w") as f:
        json.dump(embeddings, f)


def _to_filename(docname):
    return docname.replace("/", "_")


def _title(node):
    if node.children and isinstance(node.children[0], nodes.title):
        return node.children[0].astext()
    return None


def _id(node):
    ids = node.attributes.get("ids", None)
    if ids is None:
        error(f"This section has no IDs: {text}")
    # It seems like the section ID is generated off the heading text
    # and the custom anchor is inserted as a span. Sphinx generates
    # SERP previews based off these anchors so we need to get it right.
    # Maybe use beautiful soup?
    return ids[0]


def generate_document_retrieval_embeddings(docname, doctree, model, embed_fn, count_fn):
    embeddings = []
    # sys.exit(doctree.asdom().toxml())
    for node in doctree.traverse(nodes.section):
        text = node.astext()
        section_id = None if isinstance(node.parent, nodes.document) else _id(node)
        title = _title(node)
        token_count = count_fn(text)
        # [docName, title, anchor, descr, score, _filename, kind]
        if token_count > 250:
            print("need to split up the section")
            for child in node.children:
                text = child.astext()
                token_count = count_fn(text)
                embeddings.append({
                    "docname": docname,
                    "title": _title(node),
                    "id": section_id,
                    "checksum": compute_checksum(text),
                    "embedding": embed_fn(text),
                    "tokens": count_fn(text)
                })
        else:
            print("don't need to split up the section")
            embeddings.append({
                "docname": docname,
                "title": _title(node),
                "id": section_id,
                "checksum": compute_checksum(text),
                "embedding": embed_fn(text),
                "tokens": count_fn(text)
            })
    return embeddings


def merge(srcdir, outdir):
    out = []
    data_dir = str(_data_dir(srcdir).absolute())
    pattern = f"{data_dir}/*.json"
    for file in glob.glob(pattern):
        with open(file, "r") as f:
            data = json.load(f)
            out += data
    out_path = Path(outdir) / Path("embeddings.json")
    with open(out_path, "w") as f:
        json.dump(out, f)
