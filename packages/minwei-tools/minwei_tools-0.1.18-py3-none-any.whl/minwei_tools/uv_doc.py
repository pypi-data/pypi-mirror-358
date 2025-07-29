import os
import colorama as cm
from pathlib import Path
import textwrap

from .dotter_style import DotStyle
from .dotter       import Dotter


IGNORE_DIRS = {".venv", "__pycache__", ".git", ".mypy_cache", ".idea", "*.egg", "*.egg-info", "node_modules", ".vscode", ".pytest_cache", "dist"}

def get_project_name(path : Path):
    return path.name if path.is_dir() else path.parent.name

def build_tree(path: Path, prefix = "", exclude_dirs : list[str] = [], dot : Dotter = None) -> list[str]:
    lines = []
    entries = sorted([p for p in path.iterdir() if not ((p.name in IGNORE_DIRS) or (p.name in exclude_dirs))])
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if dot:
            dot.insert_message(f"{entry.name}")
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(build_tree(entry, prefix + extension, exclude_dirs, dot = dot))
    return lines

def generate_readme(project_name, tree_structure):
    if tree != "":
        tree_str = f"""
        
## 📁 專案結構範例

```
{project_name}/
{tree_structure}
```

"""
    else:
        tree_str = ""
    
    return f"""\
# {project_name}
{tree_str}
---

## 🚀 安裝與啟動說明

此專案使用 [uv](https://github.com/astral-sh/uv) 來管理 Python 環境與套件。
以下是安裝與啟動的步驟：

### 1. 安裝 uv

如果已安裝 Rust，可透過 cargo 安裝：

```bash
cargo install uv
```

如果有基本的python跟pip

```bash
pip install uv
```

或使用官方安裝腳本：

```ps
curl -LsSf https://astral.sh/uv/install.sh | sh
```

如果是在 windows底下:
```ps
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

### 1. 同步 `pyproject.toml` 

```bash
uv sync
```

---

### 3. 進入開發環境

```bash
source .venv/bin/activate   # 或使用 uv shell
```

### 4. 啟動專案
```bash
uv run main.py
```

"""


if __name__ == "__main__":
    import argparse
    import os
    parser = argparse.ArgumentParser(description="Generate a README.md file for the current project.")
    parser.add_argument("-p", "--project_name", type=str, help="Name of the project. Defaults to the current directory name.")
    parser.add_argument("-o", "--output"      , type=str, default="README.md", help="Output file name. Defaults to README.md.")
    parser.add_argument("-d", "--directory"   , type=str, default=os.getcwd(), help="Directory to scan. Defaults to the current working directory.")
    parser.add_argument("-e", "--exclude"     , action = 'append', help = "The file or folders that need to exclude")
    parser.add_argument('-nt', "--no_tree"    , action = "store_true", help="Don't build the tree")
    
    args = parser.parse_args()

    project_path    = Path(args.directory).resolve() if args.directory else Path.cwd()
    exclude_files   = args.exclude if args.exclude else []
    no_tree         = args.no_tree

    project_name = args.project_name if args.project_name else None
    if not project_name:
        project_name    = get_project_name(project_path)

    output_filename : str  = args.output
    output_filepath : Path = Path(project_path) / output_filename
    
    while output_filepath.exists():
        try:
            user_input = input(f"[{cm.Fore.RED}Warning{cm.Style.RESET_ALL}] {cm.Fore.YELLOW}{output_filepath}{cm.Style.RESET_ALL} exist !!! Do you to continue? (yes/no/rename) (y/n/r) : ")
        except:
            print()
            exit(0)
        if user_input.lower() == "y" or user_input.lower() == "yes":
            try:
                user_input2 = input(f"[{cm.Fore.RED}Warning{cm.Style.RESET_ALL}] {cm.Fore.YELLOW}{output_filepath.name}{cm.Style.RESET_ALL} will replace, are you sure ? (y/n)")
            except:
                print()
                exit(0)
            if user_input2.lower() == "y" or user_input2.lower() == "yes":
                break
        elif user_input.lower() == "n" or user_input.lower() == "no":
            exit(0)
        elif user_input.lower() == "r" or user_input.lower() == "rename":
            try:
                output_filename : str  = input("[*] please type new filename : ")
            except:
                print()
                exit(0)
            if not output_filename.endswith(".md"):
                output_filename = output_filename + ".md"
            output_filepath : Path = Path(project_path) / output_filename
                
    # 獲取專案結構
    if not no_tree:
        print(f"walk though the project")
        with Dotter(message = f"Walk though project : {project_path}", show_timer = 1, cycle = DotStyle.gear_style, delay = 0.1) as dot:
            tree_lines = build_tree(project_path, exclude_dirs = exclude_files, dot = dot)
            tree       = "\n".join(tree_lines)
    else:
        tree = ""
    
    # 生成 README 內容
    readme_content = generate_readme(project_name, tree)
    
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(readme_content))
    
    print(f"README.md 已生成於 {output_filepath}")
