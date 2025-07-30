# Creating Custom Templates

WRD allows you to create custom project templates to streamline your workflow. This guide will show you how to create and use custom templates.

## Template Structure

A WRD template consists of the following structure:

```
template-name/
├── template.yml      # Template configuration
├── {{project_name}}/  # Project files (Jinja2 templating)
│   ├── {{file1}}.py
│   └── {{dir1}}/
│       └── {{file2}}.py
└── hooks/            # Optional hooks
    ├── pre_gen.py    # Pre-generation hook
    └── post_gen.py   # Post-generation hook
```

## Template Configuration (template.yml)

```yaml
# Required fields
name: my-template
description: My awesome template
author: Your Name
version: 0.1.0

# Template variables with defaults
variables:
  - name: project_name
    type: string
    description: Name of the project
    default: my-project
    
  - name: description
    type: string
    description: Project description
    default: A new project

# Files and directories to include
include:
  - "**/*"
  - "**/.*"  # Include hidden files

# Files and directories to exclude
exclude:
  - "**/__pycache__"
  - "**/*.pyc"
  - "**/*.pyo"
  - "**/*.pyd"
  - "**/.DS_Store"

# Hooks
hooks:
  pre_generate: hooks/pre_gen.py
  post_generate: hooks/post_gen.py

# Commands to run after generation
post_commands:
  - command: git init
    description: Initialize git repository
    cwd: {{project_name}}
    
  - command: git add .
    description: Stage all files
    cwd: {{project_name}}
    
  - command: git commit -m "Initial commit"
    description: Create initial commit
    cwd: {{project_name}}
```

## Template Variables

Variables can be used in file/folder names and file contents using Jinja2 syntax:

- `{{project_name}}` - Project name
- `{{project_slug}}` - URL-friendly project name
- `{{author}}` - Author name
- `{{email}}` - Author email
- `{{year}}` - Current year
- `{{date}}` - Current date (YYYY-MM-DD)

## Hooks

### Pre-generation Hooks

Pre-generation hooks run before template files are processed. They can be used to validate input or modify the context.

Example (`hooks/pre_gen.py`):

```python
import sys

def main(context):
    """Validate project name."""
    project_name = context['project_name']
    
    if not project_name.isidentifier():
        print(f"Error: '{project_name}' is not a valid Python package name.")
        sys.exit(1)
    
    return context

if __name__ == "__main__":
    import json
    context = json.loads(sys.stdin.read())
    result = main(context)
    print(json.dumps(result))
```

### Post-generation Hooks

Post-generation hooks run after template files are generated. They can be used to perform additional setup tasks.

Example (`hooks/post_gen.py`):

```python
def main(project_dir):
    """Initialize git repository and create initial commit."""
    import subprocess
    import os
    
    # Change to project directory
    os.chdir(project_dir)
    
    # Initialize git repository
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], 
        check=True
    )
    print("✓ Git repository initialized")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
```

## Creating a Single-File PWA Template

Here's an example of how to create a single-file PWA template using data URIs:

1. Create a new template directory:
   ```bash
   mkdir -p ~/.wrd/user_templates/pwa-single-file
   cd ~/.wrd/user_templates/pwa-single-file
   ```

2. Create `template.yml`:
   ```yaml
   name: pwa-single-file
   description: Single-file Progressive Web App
   author: Your Name
   version: 1.0.0
   
   variables:
     - name: app_name
       type: string
       description: Name of the PWA
       default: My PWA
     
     - name: description
       type: string
       description: App description
       default: A Progressive Web App
   ```

3. Create `{{app_name|lower}}.html`:
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>{{app_name}}</title>
       <meta name="description" content="{{description}}">
       <link rel="manifest" href="data:application/json;base64,ewogICJuYW1lIjogInt7YXBwX25hbWV9fSIsCiAgInNob3J0X25hbWUiOiAie3thcHBfbmFtZX19IiwKICAic3RhcnRfdXJsIjogIi4iLAogICJkaXNwbGF5IjogInN0YW5kYWxvbmUiLAogICJiYWNrZ3JvdW5kX2NvbG9yIjogIiNmZmZmZmYiLAogICJ0aGVtZV9jb2xvciI6ICIjMDA3OGQ3IiwKICAiaWNvbnMiOiBbXQp9">
       <style>
           body {
               font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
               margin: 0;
               padding: 1rem;
               text-align: center;
           }
           h1 { color: #0078d7; }
       </style>
   </head>
   <body>
       <h1>{{app_name}}</h1>
       <p>{{description}}</p>
       
       <script>
           // Register service worker
           if ('serviceWorker' in navigator) {
               window.addEventListener('load', () => {
                   navigator.serviceWorker.register('data:application/javascript;base64,' + btoa(`
                       self.addEventListener('install', event => {
                           console.log('Service Worker installing');
                       });
                       self.addEventListener('activate', event => {
                           console.log('Service Worker activating');
                       });
                       self.addEventListener('fetch', event => {
                           // Handle fetch events
                       });
                   `), { scope: '/' });
               });
           }
           
           // Install prompt
           let deferredPrompt;
           
           window.addEventListener('beforeinstallprompt', (e) => {
               e.preventDefault();
               deferredPrompt = e;
               
               // Show install button
               const installButton = document.createElement('button');
               installButton.textContent = 'Install App';
               installButton.style.cssText = `
                   background: #0078d7;
                   color: white;
                   border: none;
                   padding: 0.5rem 1rem;
                   border-radius: 4px;
                   font-size: 1rem;
                   cursor: pointer;
                   margin: 1rem 0;
               `;
               installButton.onclick = () => {
                   deferredPrompt.prompt();
                   deferredPrompt.userChoice.then(choice => {
                       if (choice.outcome === 'accepted') {
                           console.log('User accepted install');
                       } else {
                           console.log('User dismissed install');
                       }
                       deferredPrompt = null;
                   });
               };
               document.body.appendChild(installButton);
           });
       </script>
   </body>
   </html>
   ```

4. Use the template:
   ```bash
   wrd init my-pwa --template pwa-single-file
   ```

## Publishing Your Template

To share your template:

1. Create a Git repository for your template
2. Add a README.md with usage instructions
3. Publish to GitHub or another Git hosting service
4. Others can install it using:
   ```bash
   wrd template install https://github.com/yourusername/your-template-repo.git
   ```

## Best Practices

1. **Keep it simple**: Focus on one purpose per template
2. **Documentation**: Include a README.md explaining the template's purpose and usage
3. **Variables**: Use descriptive names and provide defaults
4. **Testing**: Test your template with different inputs
5. **Versioning**: Use semantic versioning for your templates
6. **Dependencies**: Document any required tools or dependencies
7. **Security**: Be careful with shell commands and user input

## Advanced: Template Inheritance

WRD supports template inheritance. You can extend an existing template by specifying a `base_template` in your `template.yml`:

```yaml
name: my-extended-template
base_template: python  # Extends the python template
description: My extended Python template
# ... rest of the configuration
```

This allows you to build on top of existing templates while customizing specific aspects.
