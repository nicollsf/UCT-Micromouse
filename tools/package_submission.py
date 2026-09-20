#!/usr/bin/env python3
import os
import sys
import argparse
import zipfile
import json

def compute_fnv1a(filepath_or_bytes):
    # FNV-1a 32-bit hash matching C-Kernel's checksum algorithm
    h = 2166136261
    if isinstance(filepath_or_bytes, bytes):
        data = filepath_or_bytes
    else:
        with open(filepath_or_bytes, "rb") as f:
            data = f.read()
            
    for b in data:
        h = h ^ b
        h = (h * 16777619) & 0xFFFFFFFF
    return h

def main():
    parser = argparse.ArgumentParser(description="UCT Micromouse Student Submission Packager")
    parser.add_argument("-t", "--task", required=True, choices=["milestone1", "final_demo"], help="Target assignment milestone")
    parser.add_argument("-s", "--src", required=True, help="Path to your task workspace directory (e.g., workspace/task1_square/)")
    parser.add_argument("-o", "--output", help="Output zip filename (defaults to submission_<task>.zip)")
    args = parser.parse_args()

    src_dir = os.path.abspath(args.src)
    if not os.path.exists(src_dir) or not os.path.isdir(src_dir):
        print(f"[Error] Source workspace directory not found: {args.src}")
        sys.exit(1)

    output_zip = args.output or f"submission_{args.task}.zip"
    print(f"=== Packaging Submission for {args.task.upper()} ===")
    print(f"Source Workspace: {src_dir}")

    # Gather files and classify track (Python vs Simulink)
    python_files = []
    simulink_models = []
    ert_rtw_dirs = []
    log_file = None
    config_file = None

    for root, dirs, files in os.walk(src_dir):
        for d in dirs:
            if d.endswith("_ert_rtw"):
                ert_rtw_dirs.append(os.path.join(root, d))
        for f in files:
            full_path = os.path.join(root, f)
            if f.endswith(".py"):
                python_files.append(full_path)
            elif f.endswith(".slx"):
                simulink_models.append(full_path)
            elif f == "run_log.jsonl":
                log_file = full_path
            elif f in ["sim_config.json", "simulation_config.json"]:
                config_file = full_path

    # Also search central build directory for Simulink code generation if not in workspace
    if not ert_rtw_dirs:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        build_dir = os.path.join(repo_root, "build")
        if os.path.exists(build_dir):
            for d in os.listdir(build_dir):
                d_path = os.path.join(build_dir, d)
                if d.endswith("_ert_rtw") and os.path.isdir(d_path):
                    ert_rtw_dirs.append(d_path)

    # Validate contents
    is_python = len(python_files) > 0 and len(simulink_models) == 0
    is_simulink = len(simulink_models) > 0 or len(ert_rtw_dirs) > 0

    if not is_python and not is_simulink:
        print("[Error] No valid Python scripts (.py) or Simulink models (.slx) found in workspace!")
        sys.exit(1)

    track = "Simulink" if is_simulink else "Python"
    print(f"Detected Track: {track}")

    # Log file verification and checksum math
    if not log_file:
        # Check root directory as fallback
        fallback_log = os.path.join(os.path.dirname(os.path.abspath(src_dir)), "run_log.jsonl")
        if os.path.exists(fallback_log):
            log_file = fallback_log
        else:
            fallback_log2 = os.path.join(os.getcwd(), "run_log.jsonl")
            if os.path.exists(fallback_log2):
                log_file = fallback_log2

    if not log_file:
        print("[Warning] Missing 'run_log.jsonl'! You must include your physical run log in the submission.")
    else:
        print(f"Found Telemetry Log: {log_file}")
        try:
            with open(log_file, "r") as f:
                header_line = f.readline()
                if header_line:
                    header = json.loads(header_line.strip())
                    if "log_header" in header:
                        print(f"  -> Log Device UID: {header.get('uid')}")
                        print(f"  -> Log Code Hash:  {header.get('hash')}")
        except Exception as e:
            print(f"  -> Could not verify log header format: {e}")

    # Build the zip archive
    # List of files/folders to package, mapped to their destination in the ZIP
    files_to_package = []
    
    # AST Compile check for Python scripts to catch syntax issues locally
    import py_compile
    has_syntax_error = False
    
    if is_python:
        for f_path in python_files:
            try:
                py_compile.compile(f_path, doraise=True)
            except py_compile.PyCompileError as e:
                print(f"\n[Syntax Error] Found compilation issue in: {os.path.basename(f_path)}")
                print(e.msg)
                has_syntax_error = True
                
        if has_syntax_error:
            print("\n[Error] Packaging aborted. Please fix the syntax errors above before submitting!")
            sys.exit(1)
            
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Add log file and simulation config
            if log_file:
                zipf.write(log_file, "run_log.jsonl")
            if config_file:
                zipf.write(config_file, "sim_config.json")
                print(f"Packaged Custom Dynamic Configuration: sim_config.json")
                
            # 2. Add Python files recursively
            if is_python:
                for f_path in python_files:
                    rel_path = os.path.relpath(f_path, src_dir)
                    zipf.write(f_path, rel_path)
                    print(f"Packaged: {rel_path}")
                    
            # 3. Add Simulink files
            if is_simulink:
                # Add SLX files
                for f_path in simulink_models:
                    rel_path = os.path.relpath(f_path, src_dir)
                    zipf.write(f_path, rel_path)
                    print(f"Packaged Model: {rel_path}")
                # Add code-gen directory recursively
                for d_path in ert_rtw_dirs:
                    dir_name = os.path.basename(d_path)
                    for root, dirs, files in os.walk(d_path):
                        for file in files:
                            full_file = os.path.join(root, file)
                            rel_to_gen = os.path.relpath(full_file, d_path)
                            arcname = os.path.join(dir_name, rel_to_gen)
                            zipf.write(full_file, arcname)
                    print(f"Packaged Code-Gen Folder: {dir_name}/")

        print(f"\n[Success] Created package: {output_zip}")
        print("Ready for upload! Please submit this zip file directly to Gradescope.")
    except Exception as e:
        print(f"[Error] Failed to package zip: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
