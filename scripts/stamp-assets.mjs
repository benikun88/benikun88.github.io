// GitHub Pages serves styles.css and script.js with a 10-minute cache, so
// index.html requests them by content hash to make every change load at once.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

const page = "index.html";
let html = readFileSync(page, "utf8");

for (const asset of ["styles.css", "script.js"]) {
  const hash = createHash("sha256").update(readFileSync(asset)).digest("hex").slice(0, 8);
  const pattern = new RegExp(`(["'])${asset.replace(".", "\\.")}(\\?v=[0-9a-f]*)?\\1`, "g");
  if (!pattern.test(html)) throw new Error(`${asset} is not referenced in ${page}`);
  html = html.replace(pattern, `$1${asset}?v=${hash}$1`);
}

writeFileSync(page, html);
