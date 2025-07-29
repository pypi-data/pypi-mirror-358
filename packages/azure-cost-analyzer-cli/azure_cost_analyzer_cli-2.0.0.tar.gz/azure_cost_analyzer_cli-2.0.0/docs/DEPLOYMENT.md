# 🚀 Deployment Guide

This project uses **tag-based deployment** to automatically publish to PyPI via GitHub Actions.

## 📋 Prerequisites

1. **PyPI Account**: Ensure you have a PyPI account and the project is set up
2. **Trusted Publishing**: Configure PyPI trusted publishing for this GitHub repository
3. **GitHub Environment**: Create a `release` environment in GitHub repository settings

## 🏷️ Tag-Based Deployment Process

### 1. **Create and Push a Version Tag**

```bash
# Make sure you're on the main branch
git checkout main
git pull origin main

# Create a version tag (follows semantic versioning)
git tag v2.0.1
git push origin v2.0.1
```

### 2. **Automatic Deployment**

Once you push a tag starting with `v` to the main branch:

- ✅ GitHub Actions automatically triggers
- ✅ Verifies the tag is on the main branch
- ✅ Extracts version from tag (removes `v` prefix)
- ✅ Updates version in `setup.py` and `pyproject.toml`
- ✅ Builds the package
- ✅ Tests the installation
- ✅ Publishes to PyPI using trusted publishing

### 3. **Version Tag Format**

Use semantic versioning with `v` prefix:

- `v1.0.0` - Major release
- `v1.1.0` - Minor release  
- `v1.1.1` - Patch release
- `v2.0.0-beta.1` - Pre-release

## 🔧 Manual Deployment (if needed)

You can also trigger deployment manually:

1. Go to **GitHub Actions** tab
2. Select **"Publish to PyPI"** workflow
3. Click **"Run workflow"**
4. Choose the branch and run

## 🛡️ Security Features

- **Branch Protection**: Only deploys from `main` branch
- **Tag Verification**: Confirms tag exists on main branch
- **Trusted Publishing**: No API tokens needed (more secure)
- **Environment Protection**: Uses GitHub `release` environment

## 📦 After Deployment

Once deployed, users can install via:

```bash
pip install azure-cost-analyzer-cli==2.0.1
```

And use the CLI:

```bash
azure-cost-analyzer data.csv --format all
```

## 🐛 Troubleshooting

### Tag not on main branch
```bash
# Delete wrong tag
git tag -d v2.0.1
git push origin :refs/tags/v2.0.1

# Create tag on main branch
git checkout main
git tag v2.0.1
git push origin v2.0.1
```

### Deployment failed
- Check GitHub Actions logs
- Verify PyPI trusted publishing is configured
- Ensure `release` environment exists in GitHub settings

## 📝 Example Workflow

```bash
# 1. Make changes and commit
git add .
git commit -m "feat: add new analysis features"
git push origin main

# 2. Create and push tag
git tag v2.1.0
git push origin v2.1.0

# 3. Wait for automatic deployment
# 4. Verify on PyPI: https://pypi.org/project/azure-cost-analyzer-cli/
```

## 🎯 Best Practices

1. **Always tag from main branch**
2. **Use semantic versioning**
3. **Test locally before tagging**
4. **Write clear commit messages**
5. **Update CHANGELOG.md** (if you have one)
6. **Verify deployment success** on PyPI

---

**Note**: The deployment automatically updates the version numbers in `setup.py` and `pyproject.toml` based on the git tag, so you don't need to manually update them in your code. 