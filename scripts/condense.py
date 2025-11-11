#!/usr/bin/env python3
# scripts/condense.py
"""
Condense codebase into a single text file, respecting .gitignore patterns.

Usage:
    # Entire codebase
    python scripts/condense.py

    # Specific directories/files
    python scripts/condense.py backend/agents/ backend/models/

    # Only agent code
    python scripts/condense.py backend/agents/

    # Exclude large files
    python scripts/condense.py --max-size 100

    # Include .env for debugging
    python scripts/condense.py --include-env

    # Dry run to see what would be included
    python scripts/condense.py --dry-run
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import fnmatch
import mimetypes
from collections import defaultdict

class GitignoreParser:
    DEFAULT_IGNORES = [
        # Version control
        '.git',
        '.gitignore',
        '.gitattributes',
        '.svn',
        '.hg',
        '.bzr',
        '_darcs',
        'CVS',

        # OS files
        '.DS_Store',
        'Thumbs.db',
        'desktop.ini',
        '._*',

        # Python
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        '*.so',
        '*.egg',
        '*.egg-info',
        '.eggs',
        'pip-log.txt',
        'pip-delete-this-directory.txt',
        '.installed.cfg',

        # Virtual environments
        '.venv',
        'venv',
        'ENV',
        'env',
        '.env.local',
        '.env.*.local',
        'virtualenv',

        # Testing
        '.tox',
        '.coverage',
        '.coverage.*',
        '.cache',
        '.pytest_cache',
        'htmlcov',
        '.hypothesis',
        'coverage.xml',
        '*.cover',
        '.nox',

        # Type checking
        '.mypy_cache',
        '.dmypy.json',
        'dmypy.json',
        '.pyre',
        '.ruff_cache',
        '.pytype',

        # IDEs
        '.vscode',
        '.idea',
        '*.swp',
        '*.swo',
        '*~',
        '.project',
        '.pydevproject',
        '.settings',
        '*.sublime-project',
        '*.sublime-workspace',

        # Build/Distribution
        'build',
        'develop-eggs',
        'dist',
        'downloads',
        'eggs',
        'lib',
        'lib64',
        'parts',
        'sdist',
        'var',
        'wheels',
        '*.manifest',
        '*.spec',

        # Docker
        '.dockerignore',

        # Logs
        '*.log',
        'logs',
        '*.log.*',

        # Database
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        '*.db-journal',

        # Secrets
        '.env',
        '.env.*',
        '*.key',
        '*.pem',
        '*.crt',
        '*.p12',
        'secrets.json',
        'credentials.json',

        # State files
        'state.json',
        '*.pid',

        # Large data files
        '*.csv',
        '*.json',
        '*.xml',
        '*.pkl',
        '*.pickle',
        '*.h5',
        '*.hdf5',
        '*.parquet',
        '*.feather',

        # Media files
        '*.jpg',
        '*.jpeg',
        '*.png',
        '*.gif',
        '*.ico',
        '*.svg',
        '*.webp',
        '*.mp4',
        '*.mp3',
        '*.wav',
        '*.avi',
        '*.mov',

        # Archives
        '*.zip',
        '*.tar',
        '*.gz',
        '*.rar',
        '*.7z',
        '*.bz2',
        '*.xz',

        # Documentation builds
        'docs/_build',
        'site',
        '_site',

        # Node.js / Frontend
        'node_modules',
        'npm-debug.log*',
        'yarn-debug.log*',
        'yarn-error.log*',
        'package-lock.json',
        'yarn.lock',
        'pnpm-lock.yaml',
        '.next',
        '.nuxt',
        'out',
        '.output',
        '.vercel',
        '.netlify',

        # Test outputs
        'test_outputs',
        'test-results',
        'playwright-report',

        # Backups
        '*.bak',
        '*.backup',
        '*.old',
        '*.orig',
        '*.tmp',

        # Compiled files
        '*.class',
        '*.dll',
        '*.exe',
        '*.o',
        '*.a',

        # Lock files
        'poetry.lock',
        'Pipfile.lock',

        # Output files from this script
        '*_codebase_*.txt',
        'codebase_*.txt',
    ]

    def __init__(self, gitignore_path):
        self.patterns = self.DEFAULT_IGNORES.copy()
        self.gitignore_path = Path(gitignore_path)
        self.root_dir = self.gitignore_path.parent

        if self.gitignore_path.exists():
            with open(self.gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.patterns.append(line)

    def should_ignore(self, path, max_size_kb=None):
        """Check if a path should be ignored based on patterns and size"""
        path = Path(path)

        # Always ignore .git and other VCS directories immediately
        if path.name in ['.git', '.svn', '.hg', '.bzr', '_darcs', 'CVS']:
            return True

        # Check if any parent directory is .git
        for parent in path.parents:
            if parent.name in ['.git', '.svn', '.hg', '.bzr', '_darcs', 'CVS']:
                return True

        # Check file size if specified
        if max_size_kb and path.is_file():
            try:
                size_kb = path.stat().st_size / 1024
                if size_kb > max_size_kb:
                    return True
            except Exception:
                pass

        # Check if file is binary (skip binary files)
        if path.is_file() and not self._is_text_file(path):
            return True

        # Get relative path from root
        try:
            rel_path = path.relative_to(self.root_dir)
        except ValueError:
            return False

        # Convert to string with forward slashes
        rel_str = str(rel_path).replace('\\', '/')

        # Check each pattern
        for pattern in self.patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith('/'):
                pattern_base = pattern.rstrip('/')
                if path.is_dir():
                    if self._match_pattern(rel_str, pattern_base):
                        return True
                # Check if file is within ignored directory
                parts = rel_str.split('/')
                for i in range(len(parts)):
                    partial = '/'.join(parts[:i+1])
                    if self._match_pattern(partial, pattern_base):
                        return True
            else:
                # Regular pattern
                if self._match_pattern(rel_str, pattern):
                    return True

                # Check if pattern matches any part of the path
                if '/' not in pattern:
                    # Pattern without slash matches anywhere in tree
                    parts = rel_str.split('/')
                    for part in parts:
                        if self._match_pattern(part, pattern):
                            return True

        return False

    def _is_text_file(self, path):
        """Check if a file is text (not binary)"""
        # Check by extension first
        text_extensions = {
            '.py', '.txt', '.md', '.rst', '.json', '.yaml', '.yml', '.toml',
            '.cfg', '.ini', '.conf', '.sh', '.bash', '.zsh', '.fish',
            '.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.sass', '.html',
            '.xml', '.sql', '.graphql', '.proto', '.env', '.gitignore',
            '.dockerignore', '.editorconfig', '.c', '.cpp', '.h', '.hpp',
            '.java', '.go', '.rs', '.rb', '.php', '.pl', '.lua', '.r',
            '.swift', '.kt', '.scala', '.clj', '.ex', '.exs', '.erl',
            '.vim', '.emacs', '.el', '.tex', '.bib', '.csv'
        }

        if path.suffix.lower() in text_extensions:
            return True

        # Check by MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type and mime_type.startswith('text/'):
            return True

        # For files without extension, read first few bytes
        try:
            with open(path, 'rb') as f:
                chunk = f.read(8192)
                if not chunk:
                    return True
                # Check for null bytes
                if b'\x00' in chunk:
                    return False
                # Try to decode as UTF-8
                try:
                    chunk.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        except Exception:
            return False

    def _match_pattern(self, path, pattern):
        """Match a path against a gitignore pattern"""
        # Handle negation (patterns starting with !)
        if pattern.startswith('!'):
            return False

        # Handle patterns starting with /
        if pattern.startswith('/'):
            pattern = pattern[1:]
            # Must match from root
            return fnmatch.fnmatch(path, pattern)

        # Pattern can match anywhere
        if fnmatch.fnmatch(path, pattern):
            return True

        # Check if pattern matches end of path
        if path.endswith('/' + pattern) or '/' + pattern + '/' in path:
            return True

        return False


def generate_tree(root_path, gitignore_parser, prefix="", is_last=True, max_depth=None, current_depth=0, max_size_kb=None):
    """Generate a tree structure of the directory"""
    lines = []
    root_path = Path(root_path)

    # Skip if should be ignored
    if gitignore_parser.should_ignore(root_path, max_size_kb):
        return lines

    # Add current item with file size if it's a file
    connector = "└── " if is_last else "├── "
    name = root_path.name

    if root_path.is_file():
        try:
            size = root_path.stat().st_size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f}KB"
            else:
                size_str = f"{size/1024/1024:.1f}MB"
            name = f"{name} ({size_str})"
        except Exception:
            pass

    lines.append(prefix + connector + name)

    # Only recurse if it's a directory and we haven't hit max depth
    if root_path.is_dir() and (max_depth is None or current_depth < max_depth):
        # Get all items and filter
        items = []
        try:
            for item in sorted(root_path.iterdir()):
                if not gitignore_parser.should_ignore(item, max_size_kb):
                    items.append(item)
        except PermissionError:
            pass

        # Process items
        for i, item in enumerate(items):
            is_last_item = (i == len(items) - 1)
            extension = "    " if is_last else "│   "
            subtree = generate_tree(
                item,
                gitignore_parser,
                prefix + extension,
                is_last_item,
                max_depth,
                current_depth + 1,
                max_size_kb
            )
            lines.extend(subtree)

    return lines


def get_file_content(file_path, root_path, include_line_numbers=False):
    """Get the content of a file with proper header"""
    rel_path = Path(file_path).relative_to(root_path)
    content = []

    # Add file header
    content.append("=" * 80)
    content.append(f"# FILE: {rel_path}")
    content.append("=" * 80)
    content.append("")

    # Try to read file content
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

            if include_line_numbers:
                # Add line numbers
                for i, line in enumerate(lines, 1):
                    content.append(f"{i:4d}: {line.rstrip()}")
            else:
                content.append(''.join(lines))

    except Exception as e:
        content.append(f"[Error reading file: {e}]")

    content.append("")  # Add empty line after file
    return '\n'.join(content)


def process_path(path, root_path, gitignore_parser, processed_files, max_size_kb=None, include_line_numbers=False):
    """Process a path (file or directory) and return its contents"""
    path = Path(path)
    contents = []

    if path.is_file():
        if not gitignore_parser.should_ignore(path, max_size_kb) and path not in processed_files:
            processed_files.add(path)
            contents.append(get_file_content(path, root_path, include_line_numbers))
    elif path.is_dir():
        # Recursively process directory
        for item in sorted(path.rglob('*')):
            if item.is_file() and not gitignore_parser.should_ignore(item, max_size_kb) and item not in processed_files:
                processed_files.add(item)
                contents.append(get_file_content(item, root_path, include_line_numbers))

    return contents


def print_summary(output_file, file_count, file_size_kb, file_stats=None):
    """Print a formatted summary"""
    print("")
    print("=" * 60)
    print("✅ CODEBASE EXPORT COMPLETE")
    print("=" * 60)
    print(f"📁 Output file: {output_file}")
    print(f"📊 Files included: {file_count}")
    print(f"💾 Output size: {file_size_kb:.2f} KB", end="")

    if file_size_kb > 1024:
        print(f" ({file_size_kb/1024:.2f} MB)")
    else:
        print()

    if file_stats:
        print("\n📈 File Type Breakdown:")
        sorted_stats = sorted(file_stats.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_stats[:10]:  # Top 10
            ext_name = ext if ext else 'no extension'
            print(f"   • {ext_name}: {count} files")

    print("-" * 60)
    print("📋 File contains:")
    print("   • Complete file tree structure")
    print("   • Full source code for all included files")
    print("   • Timestamp and metadata")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Condense codebase into a single text file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/condense.py                         # Entire codebase
  python scripts/condense.py backend/agents/         # Specific directory
  python scripts/condense.py --include-env           # Include .env files
  python scripts/condense.py --max-size 100          # Skip files > 100KB
  python scripts/condense.py --line-numbers          # Add line numbers
  python scripts/condense.py --dry-run               # See what would be included
        """
    )

    parser.add_argument('paths', nargs='*',
                       help='Specific files or directories to include (default: entire codebase)')
    parser.add_argument('--max-depth', type=int,
                       help='Maximum tree depth to display')
    parser.add_argument('--max-size', type=int,
                       help='Maximum file size in KB to include (default: no limit)')
    parser.add_argument('--include-env', action='store_true',
                       help='Include .env files (normally excluded)')
    parser.add_argument('--include-logs', action='store_true',
                       help='Include log files (normally excluded)')
    parser.add_argument('--include-data', action='store_true',
                       help='Include data files like .json, .csv (normally excluded)')
    parser.add_argument('--line-numbers', action='store_true',
                       help='Add line numbers to source code')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory (default: current directory)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be included without writing file')

    args = parser.parse_args()

    # Setup paths
    root_path = Path.cwd()
    gitignore_path = root_path / '.gitignore'

    # Create gitignore parser
    gitignore_parser = GitignoreParser(gitignore_path)

    # Handle include flags
    if args.include_env:
        gitignore_parser.patterns = [p for p in gitignore_parser.patterns
                                    if not p.startswith('.env')]
        print("✓ Including .env files")

    if args.include_logs:
        gitignore_parser.patterns = [p for p in gitignore_parser.patterns
                                    if not (p.endswith('.log') or p == 'logs')]
        print("✓ Including log files")

    if args.include_data:
        data_extensions = ['*.json', '*.csv', '*.xml', '*.pkl', '*.pickle']
        gitignore_parser.patterns = [p for p in gitignore_parser.patterns
                                    if p not in data_extensions]
        print("✓ Including data files")

    # Setup output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = root_path.name

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = root_path

    output_file = output_dir / f'{project_name}_codebase_{timestamp}.txt'

    print(f"\n🔄 Codebase Condenser")
    print("=" * 60)
    print(f"📂 Source: {root_path}")
    if not args.dry_run:
        print(f"📄 Output: {output_file}")
    else:
        print(f"🔍 Mode: DRY RUN (no file will be written)")

    if args.max_size:
        print(f"📏 Max file size: {args.max_size} KB")

    print("-" * 60)

    # Prepare output content
    output_lines = []

    # Add header
    output_lines.append("=" * 80)
    output_lines.append("CODEBASE EXPORT")
    output_lines.append(f"Project: {project_name}")
    output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"Root Directory: {root_path}")
    output_lines.append("=" * 80)
    output_lines.append("")

    # Generate and add tree structure
    output_lines.append("=" * 80)
    output_lines.append("FILE TREE STRUCTURE")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append(str(root_path.name) + "/")

    # Generate tree for all subdirectories
    items = []
    try:
        for item in sorted(root_path.iterdir()):
            if not gitignore_parser.should_ignore(item, args.max_size):
                items.append(item)
    except PermissionError:
        pass

    print("🌳 Generating file tree...")
    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        tree_lines = generate_tree(
            item,
            gitignore_parser,
            "",
            is_last,
            args.max_depth,
            max_size_kb=args.max_size
        )
        output_lines.extend(tree_lines)

    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("FILE CONTENTS")
    output_lines.append("=" * 80)
    output_lines.append("")

    # Process files
    processed_files = set()
    file_stats = defaultdict(int)

    if args.paths:
        # Process specific paths
        print(f"📝 Processing specified paths: {', '.join(args.paths)}")
        for path_str in args.paths:
            path = Path(path_str)
            if not path.is_absolute():
                path = root_path / path

            if path.exists():
                print(f"  ✓ Processing: {path.relative_to(root_path)}")
                contents = process_path(
                    path,
                    root_path,
                    gitignore_parser,
                    processed_files,
                    args.max_size,
                    args.line_numbers
                )
                output_lines.extend(contents)
            else:
                print(f"  ✗ Path not found: {path}")
    else:
        # Process entire codebase
        print("📝 Processing entire codebase...")

        # Define processing order for better organization
        priority_dirs = ['backend', 'frontend', 'scripts', 'docs', 'tests']

        # Process priority directories first
        for dir_name in priority_dirs:
            dir_path = root_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"  ✓ Processing {dir_name}/...")
                for item in sorted(dir_path.rglob('*')):
                    if item.is_file() and not gitignore_parser.should_ignore(item, args.max_size) and item not in processed_files:
                        output_lines.append(get_file_content(item, root_path, args.line_numbers))
                        processed_files.add(item)
                        file_stats[item.suffix] += 1

        # Process remaining files in root and other directories
        print("  ✓ Processing remaining files...")
        for item in sorted(root_path.rglob('*')):
            if item.is_file() and item not in processed_files:
                if not gitignore_parser.should_ignore(item, args.max_size):
                    output_lines.append(get_file_content(item, root_path, args.line_numbers))
                    processed_files.add(item)
                    file_stats[item.suffix] += 1

    # Add footer
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append(f"END OF CODEBASE EXPORT - {len(processed_files)} files")
    output_lines.append("=" * 80)

    # Write output file or show dry run results
    output_content = '\n'.join(output_lines)

    if args.dry_run:
        print("\n" + "=" * 60)
        print("📋 DRY RUN RESULTS")
        print("=" * 60)
        print(f"Files that would be included: {len(processed_files)}")
        print(f"Estimated output size: {len(output_content) / 1024:.2f} KB")

        if file_stats:
            print("\n📈 File Type Breakdown:")
            sorted_stats = sorted(file_stats.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_stats[:10]:
                ext_name = ext if ext else 'no extension'
                print(f"   • {ext_name}: {count} files")

        print("\nRun without --dry-run to generate the file.")
        return

    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)

        # Calculate statistics
        file_count = len(processed_files)
        file_size_kb = output_file.stat().st_size / 1024

        print_summary(output_file, file_count, file_size_kb, file_stats)

    except Exception as e:
        print(f"❌ Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
