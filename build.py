import argparse
import http.server
import os
import shutil
import socketserver
import markdown

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(ROOT_DIR, "build")
SOURCE_DIR = os.path.join(ROOT_DIR, "src")
PAGES_DIR = os.path.join(SOURCE_DIR, "pages")
STATIC_DIRS = ["css", "img"]


def load_layout(dev_mode=False):
    with open(os.path.join(SOURCE_DIR, "index.html"), "r") as f:
        layout = f.read()

    return layout


def build_website(layout):
    shutil.rmtree(BUILD_DIR, ignore_errors=True)

    # copy static files
    for static_dir in STATIC_DIRS:
        shutil.copytree(
            os.path.join(SOURCE_DIR, static_dir), os.path.join(BUILD_DIR, static_dir)
        )

    for root, dirs, files in os.walk(PAGES_DIR):
        # create subdirectories in build folder
        for subdir in dirs:
            os.makedirs(os.path.join(BUILD_DIR, subdir), exist_ok=True)

        for file in files:
            if not file.endswith(".md"):
                continue

            print(f"rendering {file}")
            with open(os.path.join(root, file), encoding="utf8") as f:
                md = f.read()
            html = markdown.markdown(md, extensions=["fenced_code", "codehilite"])
            full_page = layout.format(page=html)
            html_path = os.path.join(
                BUILD_DIR,
                root.replace(PAGES_DIR, "").lstrip(os.sep),
                f"{os.path.splitext(file)[0]}.html",
            )
            with open(html_path, "w", encoding="utf8") as f:
                f.write(full_page)


class RewriteUrlsHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Rewrite the URL for .html files.
        if self.path.endswith("/"):
            self.path += "index.html"
        elif not any(
            self.path.endswith(x)
            for x in [".html", ".js", ".css", ".png", ".jpg", ".jpeg", ".gif"]
        ):
            self.path += ".html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def serve_website(port=8000):
    os.chdir(BUILD_DIR)
    handler = RewriteUrlsHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler, bind_and_activate=False) as httpd:
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()

        print(f"Serving on http://localhost:{port}/ from {BUILD_DIR}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the server...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build and serve a static website with live reloading."
    )
    parser.add_argument("--dev", action="store_true", help="Enable development mode.")
    parser.add_argument(
        "--serve", action="store_true", help="Serve the website after building."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to serve the website on (default: 8000).",
    )

    args = parser.parse_args()

    layout = load_layout(args.dev)
    build_website(layout)

    if args.serve:
        serve_website(args.port)
