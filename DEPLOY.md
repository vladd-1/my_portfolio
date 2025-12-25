# Deploy Portfolio to GitHub Pages

Your portfolio is ready to be deployed to GitHub Pages! Follow these steps:

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name your repository (e.g., `portfolio` or `abhay-tiwari-portfolio`)
5. **Important**: Make it **Public** (required for free GitHub Pages)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Connect and Push to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

```bash
cd /home/vladd/portfolio

# Add your GitHub repository as remote (replace YOUR_USERNAME and YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your code to GitHub
git push -u origin main
```

**Example:**
If your GitHub username is `abhaytiwari` and your repo is named `portfolio`, the command would be:
```bash
git remote add origin https://github.com/abhaytiwari/portfolio.git
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings** (top menu)
3. Scroll down to **Pages** (in the left sidebar)
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**

## Step 4: Access Your Portfolio

After a few minutes, your portfolio will be live at:
```
https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/
```

**Example:**
If your username is `abhaytiwari` and repo is `portfolio`:
```
https://abhaytiwari.github.io/portfolio/
```

## Updating Your Portfolio

Whenever you make changes:

```bash
cd /home/vladd/portfolio
git add .
git commit -m "Your commit message"
git push
```

Changes will be live on GitHub Pages within a few minutes!

## Custom Domain (Optional)

If you have a custom domain:
1. Go to repository Settings > Pages
2. Enter your custom domain
3. Update your domain's DNS settings as instructed by GitHub

---

**Note:** Make sure your repository is **Public** for free GitHub Pages hosting.

