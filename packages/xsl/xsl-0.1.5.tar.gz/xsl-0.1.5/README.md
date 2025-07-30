# FileX - Universal File Editor

🛠️ Powerful CLI tool and library for editing XML, SVG, and HTML files using XPath and CSS selectors.

## ✨ Features

- **XPath & CSS Selectors** - Precise element targeting
- **Multiple Formats** - XML, SVG, HTML support  
- **Local & Remote Files** - Edit files locally or from URLs
- **Data URI Extraction** - Extract and decode embedded content (PDFs, images)
- **Multiple Interfaces** - CLI commands, interactive shell, HTTP server
- **Web Interface** - Browser-based editor with API

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install filex

# Full installation with all features
pip install filex[full]

# Specific features
pip install filex[xpath]     # XPath support
pip install filex[css]       # CSS selectors  
pip install filex[remote]    # Remote file support

[XPath File Editing CLI Tool - Claude](https://claude.ai/chat/c8910e64-c97a-448f-bee7-7b6237b8145f)

> ### Usage
> 
> bash
> 
>     # CLI Commands
>     filex load example.svg
>     filex query "//svg:text[@id='title']"
>     filex set "//svg:text[@id='title']" "New Title"
>     filex extract "//svg:image/@xlink:href" --output document.pdf
>     filex save --output modified.svg
>     
>     # Interactive Shell
>     filex shell
>     
>     # HTTP Server
>     filex server --port 8080
> 
> ### Python API
> 
> python
> 
>     from filex import FileEditor
>     
>     # Load and edit file
>     editor = FileEditor('example.svg')
>     editor.set_element_text("//svg:text[@id='title']", "New Title")
>     editor.save('modified.svg')
>     
>     # Extract Data URI
>     result = editor.extract_data_uri("//svg:image/@xlink:href")
>     print(f"Found {result['mime_type']} ({result['size']} bytes)")
> 
> ## 📖 Documentation
> 
> -   [CLI Reference](https://claude.ai/chat/docs/cli.md)
> -   [API Documentation](https://claude.ai/chat/docs/api.md)
> -   [Examples](https://claude.ai/chat/docs/examples.md)
> 
> ## 🤝 Contributing
> 
> 1.  Fork the repository
> 2.  Create feature branch (`git checkout -b feature/amazing-feature`)
> 3.  Commit changes (`git commit -m 'Add amazing feature'`)
> 4.  Push to branch (`git push origin feature/amazing-feature`)
> 5.  Open Pull Request