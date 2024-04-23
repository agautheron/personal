[cosmith.fr](https://cosmith.fr)
=============================
Personal website 

# Website Build Script

This script automates the process of building a static website from markdown files and serving it locally for development and testing purposes.

## Features

- Converts Markdown files to HTML.
- Supports live reloading in development mode.
- Serves the website locally.
- Includes a layout template for consistent page design.
- Handles static assets like CSS and images.

## Requirements

- Install with `pip install -r requirements.txt`.

## Usage

1. **Build the Website**

    Run the script without any arguments to build the website. This will convert all Markdown files in the `src/pages` directory to HTML, apply the layout template, and copy static assets to the `build` directory.

    ```
    python build.py
    ```

2. **Serve the Website Locally**

    To build the website and serve it locally on a specified port (default is 8000), use the `--serve` flag.

    ```
    python build.py --serve
    ```

    Optionally, specify the port with `--port`:

    ```
    python build.py --serve --port 8080
    ```

3. **Development Mode**

    Enable development mode with the `--dev` flag. This mode can be combined with `--serve` to facilitate live reloading.

    ```
    python build.py --dev --serve
    ```

## Structure

- `src/`: Contains the source files for the website.
    - `pages/`: Markdown files to be converted into HTML.
    - `index.html`: Layout template.
    - `css/`, `img/`: Directories for static assets.
- `build/`: Destination directory for the built website.

## Extending

- Modify the `index.html` layout template to change the website's look and feel.
- Add more static directories in the `STATIC_DIRS` list as needed.
- Enhance the `RewriteUrlsHTTPRequestHandler` class for additional URL rewriting rules.
