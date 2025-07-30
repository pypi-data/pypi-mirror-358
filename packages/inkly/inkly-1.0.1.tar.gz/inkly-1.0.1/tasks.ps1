# Inkly Development Tasks
# PowerShell version of Makefile for Windows

param(
    [Parameter(Position=0)]
    [string]$Task = "help"
)

# Colors - Windows compatible
$Blue = [System.ConsoleColor]::Blue
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red
$White = [System.ConsoleColor]::White

function Write-Header($Message) {
    Write-Host $Message -ForegroundColor $Blue
}

function Write-Success($Message) {
    Write-Host $Message -ForegroundColor $Green
}

function Write-Warning($Message) {
    Write-Host $Message -ForegroundColor $Yellow
}

function Write-Error($Message) {
    Write-Host $Message -ForegroundColor $Red
}

function Show-Help {
    Write-Host "Inkly - OpenAPI Code Generator" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor $Green
    Write-Host "  help             " -ForegroundColor $Yellow -NoNewline; Write-Host "Show this help message"
    Write-Host "  install          " -ForegroundColor $Yellow -NoNewline; Write-Host "Install the package in development mode"
    Write-Host "  dev-install      " -ForegroundColor $Yellow -NoNewline; Write-Host "Install development dependencies"
    Write-Host "  test             " -ForegroundColor $Yellow -NoNewline; Write-Host "Run tests with pytest"
    Write-Host "  test-fast        " -ForegroundColor $Yellow -NoNewline; Write-Host "Run tests without coverage"
    Write-Host "  lint             " -ForegroundColor $Yellow -NoNewline; Write-Host "Run ruff linter"
    Write-Host "  lint-fix         " -ForegroundColor $Yellow -NoNewline; Write-Host "Run ruff linter with auto-fix"
    Write-Host "  format           " -ForegroundColor $Yellow -NoNewline; Write-Host "Format code with ruff"
    Write-Host "  format-check     " -ForegroundColor $Yellow -NoNewline; Write-Host "Check code formatting"
    Write-Host "  type-check       " -ForegroundColor $Yellow -NoNewline; Write-Host "Run pyright type checker"
    Write-Host "  build            " -ForegroundColor $Yellow -NoNewline; Write-Host "Build package"
    Write-Host "  build-clean      " -ForegroundColor $Yellow -NoNewline; Write-Host "Clean and build package"
    Write-Host "  clean            " -ForegroundColor $Yellow -NoNewline; Write-Host "Clean build artifacts and cache"
    Write-Host "  check            " -ForegroundColor $Yellow -NoNewline; Write-Host "Run all checks (lint, format-check, type-check)"
    Write-Host "  test-all         " -ForegroundColor $Yellow -NoNewline; Write-Host "Run all tests and checks"
    Write-Host "  ci               " -ForegroundColor $Yellow -NoNewline; Write-Host "Run CI pipeline (all checks and tests)"
    Write-Host "  dev              " -ForegroundColor $Yellow -NoNewline; Write-Host "Setup development environment"
    Write-Host "  generate-example " -ForegroundColor $Yellow -NoNewline; Write-Host "Generate example client and server code"
    Write-Host "  serve            " -ForegroundColor $Yellow -NoNewline; Write-Host "Start mock server for petstore example"
    Write-Host "  version          " -ForegroundColor $Yellow -NoNewline; Write-Host "Show current version"
    Write-Host "  install-req      " -ForegroundColor $Yellow -NoNewline; Write-Host "Install from requirements.txt"
    Write-Host "  install-dev-req  " -ForegroundColor $Yellow -NoNewline; Write-Host "Install from requirements-dev.txt"
    Write-Host "  install-build-req" -ForegroundColor $Yellow -NoNewline; Write-Host "Install build requirements"
    Write-Host "  quick-test       " -ForegroundColor $Yellow -NoNewline; Write-Host "Quick development test (fix lint + fast test)"
    Write-Host "  all              " -ForegroundColor $Yellow -NoNewline; Write-Host "Run complete workflow"
}

function Install-Package {
    Write-Header "Installing package in development mode..."
    pip install -e .
}

function Install-DevDependencies {
    Write-Header "Installing development dependencies..."
    pip install -e ".[dev]"
}

function Run-Tests {
    Write-Header "Running tests..."
    python -m pytest tests/ -v --cov=inkly --cov-report=html --cov-report=xml --cov-report=term-missing
}

function Run-FastTests {
    Write-Header "Running fast tests..."
    python -m pytest tests/ -v
}

function Run-Lint {
    Write-Header "Running ruff linter..."
    python -m ruff check inkly/ tests/
}

function Run-LintFix {
    Write-Header "Running ruff linter with auto-fix..."
    python -m ruff check inkly/ tests/ --fix
}

function Run-Format {
    Write-Header "Formatting code with ruff..."
    python -m ruff format inkly/ tests/
}

function Run-FormatCheck {
    Write-Header "Checking code formatting..."
    python -m ruff format inkly/ tests/ --check
}

function Run-TypeCheck {
    Write-Header "Running pyright type checker..."
    python -m pyright inkly/ tests/
}

function Build-Package {
    Write-Header "Building package..."
    python -m build
}

function Clean-BuildArtifacts {
    Write-Header "Cleaning build artifacts..."
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    if (Test-Path ".ruff_cache") { Remove-Item -Recurse -Force ".ruff_cache" }
    if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    if (Test-Path ".pytype") { Remove-Item -Recurse -Force ".pytype" }
    if (Test-Path ".mypy_cache") { Remove-Item -Recurse -Force ".mypy_cache" }
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | ForEach-Object { Remove-Item -Recurse -Force $_ }
    Get-ChildItem -Recurse -File -Name "*.pyc" | ForEach-Object { Remove-Item -Force $_ }
}

function Run-AllChecks {
    Write-Header "Running all checks..."
    Run-Lint
    Run-FormatCheck
    Run-TypeCheck
}

function Run-AllTestsAndChecks {
    Write-Header "Running all tests and checks..."
    Run-AllChecks
    Run-Tests
}

function Run-CI {
    Write-Header "Running CI pipeline..."
    Install-DevDependencies
    Run-AllTestsAndChecks
}

function Setup-Dev {
    Write-Header "Setting up development environment..."
    Install-DevDependencies
    Write-Success "Development environment ready!"
    Write-Host "Run '" -NoNewline; Write-Host ".\tasks.ps1 help" -ForegroundColor $Yellow -NoNewline; Write-Host "' to see available commands"
}

function Generate-Example {
    Write-Header "Generating example code..."
    python -m inkly generate examples/petstore.yaml --output client_example/
    python -m inkly generate-server examples/petstore.yaml --output server_example/
}

function Start-MockServer {
    Write-Header "Starting mock server..."
    python -m inkly serve examples/petstore.yaml --mock
}

function Show-Version {
    Write-Header "Current version:"
    python -c "import inkly; print(inkly.__version__)"
}

function Install-FromRequirements {
    Write-Header "Installing from requirements.txt..."
    pip install -r requirements.txt
}

function Install-DevFromRequirements {
    Write-Header "Installing from requirements-dev.txt..."
    pip install -r requirements-dev.txt
}

function Install-BuildRequirements {
    Write-Header "Installing build requirements..."
    pip install -r requirements-build.txt
}

function Run-QuickTest {
    Write-Header "Quick development test (fix lint + fast test)..."
    Run-LintFix
    Run-FastTests
}

function Run-All {
    Write-Header "Running complete workflow..."
    Clean-BuildArtifacts
    Install-DevDependencies
    Run-AllTestsAndChecks
    Build-Package
}

# Main task router
switch ($Task) {
    "help" { Show-Help }
    "install" { Install-Package }
    "dev-install" { Install-DevDependencies }
    "test" { Run-Tests }
    "test-fast" { Run-FastTests }
    "lint" { Run-Lint }
    "lint-fix" { Run-LintFix }
    "format" { Run-Format }
    "format-check" { Run-FormatCheck }
    "type-check" { Run-TypeCheck }
    "build" { Build-Package }
    "build-clean" { Clean-BuildArtifacts; Build-Package }
    "clean" { Clean-BuildArtifacts }
    "check" { Run-AllChecks }
    "test-all" { Run-AllTestsAndChecks }
    "ci" { Run-CI }
    "dev" { Setup-Dev }
    "generate-example" { Generate-Example }
    "serve" { Start-MockServer }
    "version" { Show-Version }
    "install-req" { Install-FromRequirements }
    "install-dev-req" { Install-DevFromRequirements }
    "install-build-req" { Install-BuildRequirements }
    "quick-test" { Run-QuickTest }
    "all" { Run-All }
    default {
        Write-Error "Unknown task: $Task"
        Write-Host ""
        Show-Help
        exit 1
    }
} 
