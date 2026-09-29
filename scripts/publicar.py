"""Genera la rama `repo` (APKs + index.pb/index.json) a partir de lo que compiló Gradle.

Uso: python publicar.py <carpeta de extensions-source> <carpeta de salida>

Basado en .github/scripts/publish-repo.py de keiyoushi/extensions-source (Apache-2.0). Aquí se
reconstruye todo el índice en cada ejecución y los APKs viven en la misma rama, sin releases.
"""

import gzip
import json
import os
import shutil
import sys
from pathlib import Path

source_dir, out_dir = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(source_dir / ".github/scripts"))

import index_pb2  # noqa: E402
from google.protobuf import json_format  # noqa: E402

REPO = os.environ.get("GITHUB_REPOSITORY", "Jodaurro161997/keiyoushi-src")
BASE_URL = f"https://raw.githubusercontent.com/{REPO}/repo"
ICON_BASE_URL = "https://cdn.jsdelivr.net/gh/keiyoushi/extensions-source@main"
ICON_FILE = "res/mipmap-xhdpi/ic_launcher.png"
SIGNING_KEY = os.environ["SIGNING_KEY_SHA256"].replace(":", "").lower()


def icon_url(module: str, theme: str | None) -> str:
    for candidate in (
        f"src/{module.replace('.', '/')}/{ICON_FILE}",
        f"lib-multisrc/{theme}/{ICON_FILE}" if theme else None,
    ):
        if candidate and (source_dir / candidate).exists():
            return f"{ICON_BASE_URL}/{candidate}"
    return f"{ICON_BASE_URL}/core/src/main/{ICON_FILE}"


apk_dir = out_dir / "apk"
apk_dir.mkdir(parents=True, exist_ok=True)

extensions = []
for info_file in source_dir.glob("src/*/*/build/keiyoushi-source-info.json"):
    info = json.loads(info_file.read_text(encoding="utf-8"))
    apk = next((info_file.parent / "outputs/apk/release").glob("*.apk"))
    shutil.copy2(apk, apk_dir / apk.name)
    extensions.append(
        index_pb2.Extension(
            name=info["name"],
            packageName=info["packageName"],
            resources=index_pb2.Resources(
                apkUrl=f"{BASE_URL}/apk/{apk.name}",
                iconUrl=icon_url(info["module"], info.get("theme")),
            ),
            extensionLib=info["extensionLib"],
            versionCode=info["versionCode"],
            versionName=info["versionName"],
            contentWarning=info["contentWarning"],
            sources=[
                index_pb2.Source(
                    id=int(s["id"]),
                    name=s["name"],
                    language=s["lang"],
                    homeUrl=s["baseUrl"],
                    mirrorUrls=s.get("mirrorUrls", []),
                )
                for s in info["sources"]
            ],
        )
    )

if not extensions:
    sys.exit("No se encontró ninguna extensión compilada")
extensions.sort(key=lambda e: e.packageName)

index = index_pb2.Index(
    name="Extensiones Johan",
    badgeLabel="JOHAN",
    signingKey=SIGNING_KEY,
    contact=index_pb2.Contact(website=f"https://github.com/{REPO}"),
    extensionList=index_pb2.ExtensionList(extensions=extensions),
)

(out_dir / "index.pb").write_bytes(
    gzip.compress(index.SerializeToString(deterministic=True), mtime=0)
)
(out_dir / "index.json").write_text(
    json_format.MessageToJson(index, preserving_proto_field_name=True),
    encoding="utf-8",
)

lines = ["## Extensiones publicadas", "", "| Extensión | Versión |", "|---|---|"]
lines += [f"| {e.name} | {e.versionName} |" for e in extensions]
text = "\n".join(lines) + "\n"
print(text)
with Path(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull)).open("a", encoding="utf-8") as f:
    f.write(text)
