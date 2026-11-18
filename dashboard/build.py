"""Inline data (and Chart.js, so the page works offline on stage) into dashboard/index.html."""
import pathlib
here = pathlib.Path(__file__).parent
html = (here / "template.html").read_text().replace("__DATA__", (here / "data.json").read_text())
tag = '<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>'
vendor = here / "vendor" / "chart.umd.js"
if vendor.exists():
    html = html.replace(tag, "<script>" + vendor.read_text().replace("</script", "<\\/script") + "</script>")
(here / "index.html").write_text(html)
print("wrote", here / "index.html", len(html) // 1024, "KB")
