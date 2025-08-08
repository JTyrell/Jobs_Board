# Global Installation Guide

This guide explains how to install the Jobs Platform requirements globally on your system (outside of a virtual environment).

## ⚠️ Important Note

Installing packages globally is generally not recommended because:
- It can cause conflicts between different projects
- It makes it harder to manage dependencies
- It can affect system Python packages

**Recommended approach**: Use virtual environments for each project.

## Global Installation Steps

### 1. Install Development Requirements (Recommended for Global)

For development and testing without PostgreSQL:

```bash
pip install -r requirements-dev.txt
```

This installs all core dependencies except PostgreSQL support.

### 2. Install Full Requirements (If PostgreSQL is needed)

If you need PostgreSQL support, install the full requirements:

```bash
pip install -r requirements.txt
```

**Note**: This requires PostgreSQL development files to be installed on your system.

### 3. Alternative: Install PostgreSQL Support Separately

If the main requirements fail due to PostgreSQL issues:

```bash
# First install development requirements
pip install -r requirements-dev.txt

# Then install PostgreSQL support separately
pip install psycopg2-binary
```

## Troubleshooting Global Installation

### PostgreSQL Issues

If you encounter PostgreSQL-related errors:

1. **Install PostgreSQL on your system**:
   - Windows: Download from https://www.postgresql.org/download/windows/
   - macOS: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql postgresql-contrib`

2. **Or use the latest binary version**:
   ```bash
   pip install psycopg2-binary
   ```

3. **Or skip PostgreSQL for development**:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Pillow Issues

If Pillow installation fails:

```bash
pip install --only-binary=all Pillow
```

### Permission Issues

If you get permission errors:

**Windows**:
- Run PowerShell as Administrator
- Or use: `pip install --user -r requirements-dev.txt`

**macOS/Linux**:
- Use: `pip install --user -r requirements-dev.txt`
- Or: `sudo pip install -r requirements-dev.txt` (not recommended)

## Verification

After installation, verify everything works:

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Package Locations

When installed globally, packages are located in:

**Windows**:
```
C:\Users\[Username]\AppData\Local\Programs\Python\Python313\Lib\site-packages\
```

**macOS/Linux**:
```
/usr/local/lib/python3.x/site-packages/
```

## Managing Global Packages

### List installed packages:
```bash
pip list
```

### Check specific package:
```bash
pip show django
```

### Uninstall packages:
```bash
pip uninstall package-name
```

### Update packages:
```bash
pip install --upgrade package-name
```

## Environment Variables

For global installation, you may need to set environment variables:

**Windows**:
```cmd
set PYTHONPATH=%PYTHONPATH%;C:\path\to\your\project
```

**macOS/Linux**:
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/your/project
```

## Security Considerations

When installing globally:
- Be careful with packages that require system-level access
- Regularly update packages to patch security vulnerabilities
- Consider using `pip install --user` to install in user directory instead of system directory

## Recommended Workflow

1. **For Development**: Use `requirements-dev.txt` globally
2. **For Production**: Use virtual environments with `requirements.txt`
3. **For Testing**: Use virtual environments to avoid conflicts

## Fallback Options

If global installation continues to have issues:

1. **Use virtual environments** (recommended)
2. **Use Docker** for consistent environments
3. **Use conda** for better dependency management
4. **Install packages individually** as needed 