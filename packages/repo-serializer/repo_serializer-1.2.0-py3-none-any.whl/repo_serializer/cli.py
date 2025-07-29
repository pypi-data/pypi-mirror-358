import argparse
import os
from .serializer import serialize
from .prompt_extractor import PromptExtractor, format_prompt_output


def main():
    parser = argparse.ArgumentParser(
        description="""Serialize a repository into a structured text file, capturing directory structure, 
        file names, and contents. Supports filtering by file type and various output formats."""
    )
    parser.add_argument("repo_path", help="Path to the repository to serialize")
    parser.add_argument(
        "-o",
        "--output",
        default="repo_serialized.txt",
        help="Output file path (default: repo_serialized.txt)",
    )
    parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Copy the output to clipboard in addition to saving to file",
    )
    parser.add_argument(
        "-s",
        "--structure-only",
        action="store_true",
        help="Only include directory structure and filenames (no file contents)",
    )
    parser.add_argument(
        "--python",
        action="store_true",
        help="Only include Python files (.py, .ipynb, .pyw, .pyx, .pxd, .pxi)",
    )
    parser.add_argument(
        "--javascript",
        action="store_true",
        help="Only include JavaScript/TypeScript files (.js, .jsx, .ts, .tsx, .vue, .svelte)",
    )
    parser.add_argument(
        "--skip-dir",
        action="append",
        default=[],
        help="Comma-separated list of directory names to skip (can be used multiple times)",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        action="store_true",
        help="Extract and display prompts from the repository (AI/LLM prompts only)",
    )

    args = parser.parse_args()

    # Ensure repo_path exists
    if not os.path.isdir(args.repo_path):
        print(f"Error: {args.repo_path} is not a valid directory")
        return 1

    # Handle language filtering
    language = None
    if args.python:
        language = "python"
    elif args.javascript:
        language = "javascript"

    if args.python and args.javascript:
        print("Error: Cannot specify both --python and --javascript")
        return 1
        
    # Check for conflicting options with prompt mode
    if args.prompt:
        if args.structure_only:
            print("Error: Cannot use --prompt with --structure-only")
            return 1
        if args.python or args.javascript:
            print("Error: Cannot use --prompt with language filters (--python or --javascript)")
            return 1

    # Flatten and split comma-separated skip-dir values
    skip_dirs = []
    for val in args.skip_dir:
        skip_dirs.extend([d.strip() for d in val.split(",") if d.strip()])

    # Handle prompt extraction mode
    if args.prompt:
        extractor = PromptExtractor()
        prompts = extractor.extract_prompts(args.repo_path)
        content = format_prompt_output(prompts)
        
        # Write to file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Prompts extracted to {args.output}")
        print(f"Found {len(prompts)} prompts in the repository")
        
        # Copy to clipboard if requested
        if args.clipboard:
            try:
                import pyperclip
                pyperclip.copy(content)
                print("Content also copied to clipboard")
            except ImportError:
                print(
                    "Warning: pyperclip package not found. Install it with 'pip install pyperclip' to enable clipboard functionality."
                )
            except Exception as e:
                print(f"Warning: Failed to copy to clipboard: {str(e)}")
                
        return 0
    
    # Normal serialization mode
    content = serialize(
        args.repo_path,
        args.output,
        return_content=True,
        structure_only=args.structure_only,
        language=language,
        skip_dirs=skip_dirs,
    )

    print(f"Repository serialized to {args.output}")
    if args.structure_only:
        print("Note: Only directory structure was included (no file contents)")

    # Copy to clipboard if requested
    if args.clipboard:
        try:
            import pyperclip

            pyperclip.copy(content)
            print("Content also copied to clipboard")
        except ImportError:
            print(
                "Warning: pyperclip package not found. Install it with 'pip install pyperclip' to enable clipboard functionality."
            )
        except Exception as e:
            print(f"Warning: Failed to copy to clipboard: {str(e)}")

    return 0


if __name__ == "__main__":
    exit(main())
