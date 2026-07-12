import os
import shutil
import sys
from pathlib import Path

VAULT_DIR = Path("C:/Users/manaz/Desktop/Obsidian Main Vault/10_Projects")
INBOX_DIR = Path("C:/Users/manaz/Desktop/Obsidian Main Vault/99_Inbox/vault_merge_reports")

groups = {
    "JobFilter": ["JobFilter", "JobFilterV1", "JobFilterV1-github"],
    "Zawiyah": ["zawiya-knowledge-vault", "zawiya-growth-hub", "khutba-io"],
    "FlowLens": ["flowlens", "hermes-support-flowlens"],
    "Hermes": ["awesome-hermes-agent", "AgentDock", "ForgeOS", "context7", "wondelai-skills", "black-forest-labs-skills", "Anthropic-Cybersecurity-Skills"],
    "MAZos": [], # Will assign loose projects below
}

# Assign the rest of the projects to their own Archive folders in 99_Inbox, to keep 10_Projects uncluttered
MISC_DIR = Path("C:/Users/manaz/Desktop/Obsidian Main Vault/99_Inbox/Archive_Misc")
misc_projects = ["inkweave", "omniscribe", "openflowkit", "LimitLens", "ecc", "flipsignal", "secure-shift", "scrap-finance-partners", "Vault Consolidation Backup"]

def copy_project(src_base, dest_base, project_name):
    src = Path(src_base) / project_name
    if not src.exists(): return 0
    
    dest_arc = Path(dest_base) / "Archive" / project_name
    dest_arc.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for root, dirs, files in os.walk(src):
        # Prune bad dirs
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "dist", ".next", "build", ".worktrees")]
        
        for f in files:
            if f.endswith(".md") or f.endswith(".txt"):
                src_file = Path(root) / f
                
                # compute relative path
                rel = src_file.relative_to(src)
                dest_file = dest_arc / rel
                
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src_file, dest_file)
                    count += 1
                except Exception as e:
                    pass
    return count

print("Copying JobFilter...")
jf_count = 0
for p in groups["JobFilter"]: jf_count += copy_project("C:/Users/manaz/Desktop", VAULT_DIR / "JobFilter", p)

print("Copying Zawiyah...")
zaw_count = 0
for p in groups["Zawiyah"]: zaw_count += copy_project("C:/Users/manaz/Desktop", VAULT_DIR / "Zawiyah", p)

print("Copying FlowLens...")
fl_count = 0
for p in groups["FlowLens"]: fl_count += copy_project("C:/Users/manaz/Desktop", VAULT_DIR / "FlowLens", p)

print("Copying Hermes-related...")
hermes_count = 0
for p in groups["Hermes"]: hermes_count += copy_project("C:/Users/manaz/Desktop", VAULT_DIR / "Hermes", p)

print("Copying Misc...")
misc_count = 0
for p in misc_projects: misc_count += copy_project("C:/Users/manaz/Desktop", MISC_DIR, p)

print("Copying loose desktop files to Inbox...")
loose_count = 0
desktop = Path("C:/Users/manaz/Desktop")
loose_dest = Path("C:/Users/manaz/Desktop/Obsidian Main Vault/99_Inbox/Desktop_Roots")
loose_dest.mkdir(parents=True, exist_ok=True)
for f in desktop.iterdir():
    if f.is_file() and (f.suffix == ".md" or f.suffix == ".txt"):
        try:
            shutil.copy2(f, loose_dest / f.name)
            loose_count += 1
        except: pass

print(f"\\n--- REPORT ---")
print(f"JobFilter files merged: {jf_count}")
print(f"Zawiyah files merged: {zaw_count}")
print(f"FlowLens files merged: {fl_count}")
print(f"Hermes-related files merged: {hermes_count}")
print(f"Misc projects merged: {misc_count}")
print(f"Loose desktop files merged: {loose_count}")
