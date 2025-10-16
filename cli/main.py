"""Command-line interface for file converter."""
import argparse
import sys
import uuid
from pathlib import Path
from colorama import Fore, Style, init

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from file_converter.core.registry import Registry
from file_converter.core.detect import sniff_mime
from file_converter.core.planner import plan_conversion
from file_converter.core.presets import load_defaults
from file_converter.core.jobs import Job, Status
from file_converter.core.engine import plan_and_run


def main():
    """Main CLI entry point."""
    init(autoreset=True)  # Initialize colorama
    
    parser = argparse.ArgumentParser(
        description="File Converter - Local-only file conversion tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Plan a conversion")
    plan_parser.add_argument("input", help="Input file path")
    plan_parser.add_argument("--to", required=True, help="Target MIME type")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a conversion")
    run_parser.add_argument("input", help="Input file path")
    run_parser.add_argument("--to", required=True, help="Target MIME type")
    run_parser.add_argument("--out", help="Output directory (default: same as input)")
    run_parser.add_argument("--opt", action="append", help="Option in key=value format")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize
    registry = Registry()
    plugin_dir = Path(__file__).parent.parent / "src" / "file_converter" / "plugins"
    registry.load_plugins(plugin_dir)
    
    presets = load_defaults()
    
    if args.command == "plan":
        return cmd_plan(args, registry)
    elif args.command == "run":
        return cmd_run(args, registry, presets)
    
    return 0


def cmd_plan(args, registry):
    """Execute the plan command."""
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"{Fore.RED}Error: File not found: {input_path}")
        return 1
    
    # Detect source MIME
    print(f"{Fore.CYAN}Detecting file type...")
    src_mime = sniff_mime(str(input_path))
    print(f"  Source MIME: {Fore.GREEN}{src_mime}")
    
    # Plan conversion
    print(f"\n{Fore.CYAN}Planning conversion to {args.to}...")
    plan = plan_conversion(src_mime, args.to, registry)
    
    if not plan:
        print(f"{Fore.RED}Error: No conversion route found")
        print(f"  Cannot convert {src_mime} → {args.to}")
        return 1
    
    print(f"{Fore.GREEN}✓ Conversion is possible")
    print(f"  Plugin: {plan['plugin'].name} v{plan['plugin'].version}")
    print(f"  Cost: {plan['plan'].get('cost', 'unknown')}")
    print(f"  Lossiness: {plan['plan'].get('lossiness', 'unknown')}")
    
    return 0


def cmd_run(args, registry, presets):
    """Execute the run command."""
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"{Fore.RED}Error: File not found: {input_path}")
        return 1
    
    # Parse options
    options = {}
    if args.opt:
        for opt in args.opt:
            if "=" not in opt:
                print(f"{Fore.YELLOW}Warning: Ignoring invalid option: {opt}")
                continue
            key, value = opt.split("=", 1)
            # Try to parse as int
            try:
                value = int(value)
            except ValueError:
                pass
            options[key] = value
    
    # Detect source MIME
    print(f"{Fore.CYAN}Detecting file type...")
    src_mime = sniff_mime(str(input_path))
    print(f"  Source: {Fore.GREEN}{src_mime}")
    print(f"  Target: {Fore.GREEN}{args.to}")
    
    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        src_path=str(input_path),
        src_mime=src_mime,
        dst_mime=args.to,
        options=options,
    )
    
    # Progress callback
    last_progress = [0]
    
    def on_progress(j):
        if j.status == Status.RUNNING.value:
            progress_pct = int(j.progress * 100)
            # Only print on significant progress change
            if progress_pct >= last_progress[0] + 5 or progress_pct == 100:
                print(f"{Fore.YELLOW}  Progress: {progress_pct}%")
                last_progress[0] = progress_pct
    
    # Run conversion
    print(f"\n{Fore.CYAN}Starting conversion...")
    result = plan_and_run(job, registry, presets, args.out, on_progress)
    
    if result.status == Status.DONE.value:
        print(f"\n{Fore.GREEN}✓ Conversion completed successfully")
        print(f"  Output: {result.output_path}")
        return 0
    else:
        print(f"\n{Fore.RED}✗ Conversion failed")
        if result.logs:
            print(f"\n{Fore.YELLOW}Last log entries:")
            for log in result.logs[-5:]:
                print(f"  {log}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
