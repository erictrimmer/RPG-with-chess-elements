"""Export a Level to Godot: atlas PNGs + JSON spec, then let headless Godot import and build scenes.

    from pipeline import to_godot
    to_godot(level, "World/Downtown", name="downtown")
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
GODOT = os.environ.get("GODOT_BIN", r"F:/Godot_v4.5.1-stable_mono_win64/Godot_v4.5.1-stable_mono_win64_console.exe")


def run_godot(*args, timeout=900):
    cmd = [GODOT, "--headless", "--path", PROJECT, *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout or "") + (r.stderr or "")
    lines = [ln for ln in out.splitlines() if ln.strip() and "Chess" not in ln and "puzzles" not in ln]
    return r.returncode, "\n".join(lines[-40:])


def to_godot(level, rel_dir, name, chunk=32):
    out_dir = os.path.join(PROJECT, rel_dir)
    res_dir = "res://" + rel_dir.replace("\\", "/")
    level.export(out_dir, res_dir, name=name, chunk=chunk)
    code, log = run_godot("--import")
    print("[godot import]", code)
    code, log = run_godot("--script", "res://Tools/world_builder/godot/build_level.gd", "--",
                          f"{res_dir}/{name}.json", res_dir)
    print("[godot build]", code)
    print(log)
    return code
