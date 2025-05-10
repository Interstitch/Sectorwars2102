#!/bin/bash

# Unified setup script for Sector Wars 2102
# Automatically detects environment and adapts setup accordingly

# Function to detect environment
detect_environment() {
  if [ -n "$REPL_ID" ] || [ -n "$REPL_SLUG" ] || [ -d "/home/runner" ]; then
    echo "replit"
  elif [ -n "$CODESPACE_NAME" ] || [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    echo "codespaces"
  else
    echo "local"
  fi
}

# Set environment variable if not already set
export DEV_ENVIRONMENT=${DEV_ENVIRONMENT:-$(detect_environment)}
echo "Detected environment: $DEV_ENVIRONMENT"

# Get the correct path for the repository root
if [ "$DEV_ENVIRONMENT" = "replit" ] && [ -d "/home/runner/Sectorwars2102" ]; then
  REPO_ROOT="/home/runner/Sectorwars2102"
else
  REPO_ROOT=$(pwd)
fi

# Make all scripts executable
chmod +x "$REPO_ROOT/dev-scripts/"*.sh

# Create necessary directories
mkdir -p ~/.config
mkdir -p /tmp/sectorwars/data
mkdir -p "$HOME/.local/bin"

# Function to check if a command exists
command_exists() {
  type "$1" &> /dev/null
}

# Function to setup NVM and Node.js
setup_node() {
  echo "Setting up Node.js environment..."
  
  # Try to use NVM if available
  if [ -f "$REPO_ROOT/nvm/nvm.sh" ]; then
    echo "NVM found, setting up..."
    source "$REPO_ROOT/nvm/nvm.sh"
    
    # Get current version
    if command_exists node; then
      CURRENT_NODE_VERSION=$(node -v)
      echo "Current Node.js version: $CURRENT_NODE_VERSION"
    fi
    
    # Install Node.js 18 LTS (more recent but stable)
    echo "Installing Node.js 18 LTS..."
    nvm install 18 || echo "Failed to install Node.js 18, falling back to Node.js 16"
    
    # If Node.js 18 installation failed, try Node.js 16
    if ! nvm list | grep -q "v18"; then
      echo "Attempting to install Node.js 16..."
      nvm install 16 || echo "Failed to install Node.js via NVM"
      nvm use 16 || true
    else
      echo "Setting Node.js 18 as default..."
      nvm use 18
      nvm alias default 18
    fi
    
    # Verify the version
    if command_exists node; then
      NEW_NODE_VERSION=$(node -v)
      echo "Node.js version: $NEW_NODE_VERSION"
      
      # Set environment path to include the new Node.js version
      export PATH="$(dirname $(which node)):$PATH"
      
      # Report npm version
      echo "NPM version: $(npm -v)"
    fi
  elif command_exists node; then
    echo "Node.js found: $(node --version)"
    echo "NPM found: $(npm --version)"
  else
    echo "WARNING: Node.js not found and NVM not available."
    echo "Some functionality may be limited."
  fi
}

# Function to update npm
update_npm() {
  echo "Updating npm to compatible version..."
  
  # Get current node version to determine compatible npm version
  if command_exists node; then
    NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
    
    # Choose npm version based on Node.js version
    if [ "$NODE_VERSION" -ge 20 ]; then
      NPM_VERSION="9.9.0"  # Compatible with Node.js 20+
    elif [ "$NODE_VERSION" -ge 18 ]; then
      NPM_VERSION="9.9.0"  # Compatible with Node.js 18
    elif [ "$NODE_VERSION" -ge 16 ]; then
      NPM_VERSION="8.19.4"  # Compatible with Node.js 16
    else
      NPM_VERSION="8.5.5"  # Last version for older Node.js
    fi
    
    echo "Installing npm $NPM_VERSION for Node.js v$NODE_VERSION..."
  else
    # Default to a conservative version if node not found
    NPM_VERSION="8.19.4"
    echo "Node.js version not detected, installing npm $NPM_VERSION..."
  fi
  
  # Use local installation to avoid permission issues
  npm install -g npm@$NPM_VERSION --prefix=$HOME/.local || echo "Warning: Could not update npm"
  export PATH="$HOME/.local/bin:$PATH"
  
  # Attempt to persist PATH changes even without ~/.bashrc write access
  if [ -w "$HOME/.bashrc" ]; then
    # Standard approach if we have write access
    grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  else
    echo "Note: Cannot modify .bashrc (permission denied). Trying alternative PATH persistence methods..."

    # Alternative 1: Try to use .profile instead
    if [ -w "$HOME/.profile" ]; then
      grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.profile" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.profile"
      echo "Added PATH to ~/.profile"
    # Alternative 2: Try to use .bash_profile
    elif [ -w "$HOME/.bash_profile" ]; then
      grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bash_profile" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bash_profile"
      echo "Added PATH to ~/.bash_profile"
    # Alternative 3: Create a custom environment script in the project directory
    else
      # Create a persistent env script in the project that can be sourced
      mkdir -p "$REPO_ROOT/.env.d"
      cat > "$REPO_ROOT/.env.d/path.sh" << EOF
#!/bin/bash
# Path settings for Sector Wars 2102
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$PYTHON_USER_SITE:$REPO_ROOT/services/gameserver:$PYTHONPATH"
EOF
      chmod +x "$REPO_ROOT/.env.d/path.sh"
      echo "Created custom environment script at $REPO_ROOT/.env.d/path.sh"

      # Create a README to explain its use
      cat > "$REPO_ROOT/.env.d/README.md" << EOF
# Environment Configuration

These scripts contain environment settings for the project.

To use them, add this to the beginning of your scripts:

\`\`\`bash
# Source environment settings if available
if [ -d "\$(dirname "\$0")/../.env.d" ]; then
  for script in "\$(dirname "\$0")/../.env.d"/*.sh; do
    source "\$script"
  done
fi
\`\`\`

Or source them manually:

\`\`\`bash
source ./.env.d/path.sh
\`\`\`
EOF
    fi

    # Regardless, we'll ensure all scripts that need PATH have it explicitly set
    echo "Note: Will update scripts to include PATH settings directly."
  fi
}

# Function to install PM2
install_pm2() {
  if ! command_exists pm2; then
    echo "Installing PM2 process manager..."
    
    # Try local installation to avoid permission issues
    mkdir -p "$HOME/.local/bin"
    npm install pm2 --prefix=$HOME/.local || echo "WARNING: Could not install PM2 locally"
    export PATH="$HOME/.local/bin:$PATH"
    
    # Create symlink to make pm2 available
    if [ -f "$HOME/.local/node_modules/.bin/pm2" ]; then
      ln -sf "$HOME/.local/node_modules/.bin/pm2" "$HOME/.local/bin/pm2"
      echo "PM2 installed at $HOME/.local/bin/pm2"
    fi
    
    # If still not found, try project-level installation
    if ! command_exists pm2; then
      cd "$REPO_ROOT"
      npm install pm2
      export PATH="$REPO_ROOT/node_modules/.bin:$PATH"
    fi
  fi
}

# Function to setup Python environment
setup_python() {
  echo "Setting up Python environment..."
  
  # Check if pip3 exists, otherwise try pip
  if command_exists pip3; then
    PIP_CMD="pip3"
  elif command_exists pip; then
    PIP_CMD="pip"
  else
    echo "WARNING: pip not found."
    # Try to install pip if python is available
    if command_exists python3; then
      echo "Attempting to install pip..."
      python3 -m ensurepip || python3 -m ensurepip --user || echo "Could not install pip"
      if command_exists pip3; then
        PIP_CMD="pip3"
      elif command_exists pip; then
        PIP_CMD="pip"
      fi
    else
      echo "Python not found. Cannot proceed with pip installation."
    fi
  fi

  # Ensure python user base is in PATH
  PYTHON_USER_BASE=$(python3 -m site --user-base)
  export PATH="$PYTHON_USER_BASE/bin:$PATH"
  
  # Display Python paths to help troubleshoot
  echo "Python site packages location:"
  python3 -m site
  
  # Get user site-packages directory
  PYTHON_USER_SITE=$(python3 -m site --user-site)
  echo "Python user site-packages: $PYTHON_USER_SITE"
  
  # Ensure directory exists
  mkdir -p "$PYTHON_USER_SITE"
  
  # Add site-packages to PYTHONPATH
  export PYTHONPATH="$PYTHON_USER_SITE:$REPO_ROOT/services/gameserver:$PYTHONPATH"
  
  # Function to check and fix Python package vulnerabilities
  check_python_vulnerabilities() {
    echo "Checking for Python package vulnerabilities..."

    # Install safety tool for vulnerability checking
    $PIP_CMD install --user safety >/dev/null 2>&1

    if python3 -m pip show safety >/dev/null 2>&1; then
      echo "Scanning for vulnerable Python packages..."
      python3 -m safety check || echo "Safety check completed"

      # Try to fix vulnerabilities
      echo "Attempting to update vulnerable packages..."
      python3 -m safety check --full-report | grep -B 2 "Vulnerability" | grep "Package" | awk '{print $2}' | while read pkg; do
        if [ -n "$pkg" ]; then
          echo "Upgrading potentially vulnerable package: $pkg"
          $PIP_CMD install --user --upgrade "$pkg" || echo "Failed to upgrade $pkg"
        fi
      done
    fi

    # Install pip-audit for more thorough checking
    $PIP_CMD install --user pip-audit >/dev/null 2>&1

    if python3 -m pip show pip_audit >/dev/null 2>&1; then
      echo "Running pip-audit for deeper vulnerability scan..."
      python3 -m pip_audit || echo "Audit completed"

      echo "Attempting to fix vulnerable packages with pip-audit..."
      python3 -m pip_audit --fix || echo "Some issues might remain"
    fi
  }

  # If we have pip, use it safely with --user flag to avoid permission issues
  if [ -n "$PIP_CMD" ]; then
    echo "Using $PIP_CMD to install Python packages..."
    cd "$REPO_ROOT"

    # Suppress pip version check to avoid the error
    export PIP_DISABLE_PIP_VERSION_CHECK=1

    # Update pip itself
    $PIP_CMD install --user --upgrade pip

    # Install core dependencies explicitly with specific versions
    echo "Installing core Python packages..."
    $PIP_CMD install --user uvicorn==0.23.2 fastapi==0.103.1 pydantic==1.10.8 starlette==0.27.0 || echo "Failed to install core Python dependencies"

    # Verify we can find the packages and show paths
    echo "Checking uvicorn installation path:"
    python3 -c "import uvicorn; print(f'uvicorn installed at: {uvicorn.__file__}')" || echo "❌ uvicorn not found"

    echo "Checking fastapi installation path:"
    python3 -c "import fastapi; print(f'fastapi installed at: {fastapi.__file__}')" || echo "❌ fastapi not found"

    # Install the rest of dependencies
    cd "$REPO_ROOT/services/gameserver"
    $PIP_CMD install --user -r requirements.txt --no-warn-script-location || echo "Failed to install some Python dependencies"

    # Check for and fix any vulnerabilities
    check_python_vulnerabilities

    # Run verification script if it exists
    if [ -f "$REPO_ROOT/services/gameserver/verify_imports.py" ]; then
      echo "Running Python module verification script..."
      cd "$REPO_ROOT"
      python3 "$REPO_ROOT/services/gameserver/verify_imports.py"
    fi

    # Create a .pth file in site-packages to add our project path
    echo "Creating .pth file to ensure project modules are found..."
    echo "$REPO_ROOT/services/gameserver" > "$PYTHON_USER_SITE/sectorwars.pth"
  else
    echo "WARNING: Skipping Python dependencies installation due to missing pip."
  fi
}

# Setup environment config
setup_env() {
  echo "Setting up environment configuration..."
  if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    
    # Configure database URL if provided
    if [ -n "$DATABASE_URL" ]; then
      sed -i "s#DATABASE_URL=.*#DATABASE_URL=$DATABASE_URL#" "$REPO_ROOT/.env"
    else
      sed -i 's#DATABASE_URL=.*#DATABASE_URL=postgresql://postgres:postgres@db.example.com:5432/sectorwars#' "$REPO_ROOT/.env"
    fi
    
    echo "Created .env file. Please update the database connection if needed."
  fi
}

# Address npm vulnerabilities and update dependencies
fix_npm_vulnerabilities() {
  local DIR=$1
  echo "Checking for vulnerabilities in $DIR..."
  cd "$DIR"

  # Audit to identify vulnerabilities first
  npm audit

  # Attempt to fix vulnerabilities without breaking changes
  echo "Attempting to fix vulnerabilities in $DIR..."
  npm audit fix || echo "Note: Some vulnerabilities couldn't be fixed automatically"

  # Check if critical vulnerabilities remain
  if npm audit | grep -i "critical" >/dev/null; then
    echo "Critical vulnerabilities remain - attempting more aggressive fix..."

    # Try force-resolution for npm to fix specific packages
    if ! grep -q "resolutions" package.json; then
      # Create temporary backup
      cp package.json package.json.bak

      # Extract vulnerable packages and their recommended versions
      VULN_PACKAGES=$(npm audit --json | jq -r '.advisories | to_entries[] | select(.value.severity == "critical") | .value.findings[].paths[0] | split(">")[0]' | sort -u)

      # For each vulnerable package, add a resolution
      for pkg in $VULN_PACKAGES; do
        if [ -n "$pkg" ]; then
          echo "Attempting to force-resolve critical vulnerability in $pkg"

          # Try npm audit fix with force, which can break things but fix security issues
          npm audit fix --force || echo "Force fix might have failed"

          # Another approach is to directly install the latest version of the vulnerable package
          npm install "$pkg@latest" || echo "Failed to update $pkg to latest"
        fi
      done
    fi
  fi

  # Perform a safe update of dependencies
  echo "Updating dependencies in $DIR..."
  # Use npm-check-updates if available
  if ! npm list -g npm-check-updates >/dev/null 2>&1; then
    echo "Installing npm-check-updates tool..."
    npm install -g npm-check-updates --prefix=$HOME/.local || echo "Warning: Could not install npm-check-updates"
    export PATH="$HOME/.local/bin:$PATH"
  fi

  if command -v ncu >/dev/null 2>&1; then
    # Update minor and patch versions only (safer)
    echo "Upgrading minor and patch versions of dependencies..."
    ncu -u --target minor && npm install || echo "Warning: Could not safely update dependencies"
  else
    # Fallback if ncu isn't available
    echo "Using basic npm update..."
    npm update || echo "Warning: Could not update dependencies"
  fi

  # Check for missing peer dependencies
  echo "Checking for missing peer dependencies..."
  if command -v npx >/dev/null 2>&1; then
    # Install check-peer-dependencies if not available
    if ! npm list check-peer-dependencies >/dev/null 2>&1; then
      echo "Installing check-peer-dependencies..."
      npm install --no-save check-peer-dependencies || echo "Failed to install dependency checker"
    fi

    # Run peer dependency check and install missing ones
    npx check-peer-dependencies --install || echo "Could not automatically install all peer dependencies"
  fi

  # Run audit again to see if we fixed issues
  echo "Re-checking vulnerabilities in $DIR..."
  npm audit || echo "Some vulnerabilities may still exist"

  # If audit shows moderate or high vulnerabilities but not critical, we'll accept that
  if ! npm audit | grep -i "critical" >/dev/null; then
    echo "✅ No critical vulnerabilities remain in $DIR"
  else
    echo "⚠️ Critical vulnerabilities still exist in $DIR. Manual review recommended."
  fi
}

# Install frontend dependencies
setup_frontend() {
  echo "Installing frontend dependencies..."

  # Player Client
  cd "$REPO_ROOT/services/player-client"
  npm install
  fix_npm_vulnerabilities "$REPO_ROOT/services/player-client"

  # Admin UI
  cd "$REPO_ROOT/services/admin-ui"
  npm install
  fix_npm_vulnerabilities "$REPO_ROOT/services/admin-ui"

  # Go back to root directory
  cd "$REPO_ROOT"
}

# Environment-specific setup
case "$DEV_ENVIRONMENT" in
  "replit")
    echo "Setting up for Replit environment..."
    setup_node
    update_npm
    install_pm2
    setup_python
    setup_env
    setup_frontend
    
    # Create a marker file to indicate setup is complete
    touch "$REPO_ROOT/.replit_setup_done"
    ;;
    
  "codespaces")
    echo "Setting up for GitHub Codespaces environment..."
    # For Codespaces, we primarily rely on the built-in environment
    setup_env
    ;;
    
  "local")
    echo "Setting up for local environment..."
    # For local environment, we primarily rely on docker
    setup_env
    ;;
    
  *)
    echo "Unknown environment: $DEV_ENVIRONMENT"
    echo "Please set DEV_ENVIRONMENT to 'local', 'codespaces', or 'replit'"
    exit 1
    ;;
esac

echo "Setup complete! Run './dev-scripts/start-unified.sh' to start the application."