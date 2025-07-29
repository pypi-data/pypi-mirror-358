#!/bin/bash
# GitHub Repository Setup Script for Traffic-Aware Route Optimizer

echo "🚀 Setting up GitHub repository for traffic-aware-route-optimizer"
echo "================================================================"

echo "📋 Before running this script, make sure you have:"
echo "1. Created the GitHub repository: https://github.com/new"
echo "   - Repository name: traffic-aware-route-optimizer"
echo "   - Description: Traffic-aware route optimization using Google Routes API"
echo "   - Set to Public"
echo "   - Do NOT initialize with README, .gitignore, or license"
echo ""

read -p "❓ Have you created the GitHub repository? (y/N): " response
if [[ ! $response =~ ^[Yy]$ ]]; then
    echo "Please create the GitHub repository first, then run this script again."
    exit 1
fi

echo ""
echo "🔧 Setting up local git repository..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Create .gitignore for Python projects
cat > .gitignore << EOF
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
upload_wheel_to_databricks.py
upload_to_databricks.py
DATABRICKS_UPLOAD_INSTRUCTIONS.md
EOF

echo "✅ .gitignore created"

# Add all files
git add .
echo "✅ Files staged for commit"

# Initial commit
git commit -m "Initial commit: Traffic-aware route optimizer package

- Complete Python package with Google Routes API integration
- Pydantic models for type safety
- MIT License
- Ready for PyPI publication"

echo "✅ Initial commit created"

# Add remote origin
echo ""
read -p "🔗 Enter your GitHub username: " github_username
git remote add origin https://github.com/$github_username/traffic-aware-route-optimizer.git

echo "✅ Remote origin added"

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "🎉 SUCCESS! Repository set up successfully!"
echo "🌐 View at: https://github.com/$github_username/traffic-aware-route-optimizer"
echo ""
echo "📋 Next steps:"
echo "1. Verify the repository looks correct on GitHub"
echo "2. Update the package URLs in pyproject.toml (we'll do this next)"
echo "3. Build and publish to PyPI"
