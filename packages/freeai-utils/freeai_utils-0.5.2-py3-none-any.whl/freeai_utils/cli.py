# freeai_utils/cli.py
import sys
import click
from ._setup import install_model, remove_dir
import os

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        sys.exit(1)

@main.command(help="Download default models for this library through hugging face ")
@click.argument("target", required=False)
@click.option("-y", "--yes", is_flag=True, help="Automatically confirm downloads without prompting")
def setup(target: str = "", yes: bool = False):
    install_model(target, yes)
    
@main.command(help="Detail guide on command line")
def help():
    print("*" * 100)
    print("HELP")
    print("*" * 100)
    print("Usage: freeai-utils setup [FLAG]\n")
    print(" Flags:")
    print("   A   Default models             →  freeai-utils setup A")
    print("   S   Speech-to-Text models      →  freeai-utils setup S")
    print("   D   Document-related models     →  freeai-utils setup D")
    print("   I   Image OCR models            →  freeai-utils setup I")
    print("   T   Translation models          →  freeai-utils setup T")
    print("   L   Default LLM models          →  freeai-utils setup L")
    print("   ICF Image generator models      →  freeai-utils setup ICF")
    print("   ICE Embeded for Image generator models      →  freeai-utils setup ICE")
    print("   V Vosk models      →  freeai-utils setup V")
    print("*" * 100)
    print("Usage: freeai-utils clean\n")
    print("Description: Clean up downloaded files and model through setup command")
    print("*" * 100)
    
@main.command(help="Remove extra downloaded files")
def clean():
    decision = input(
        "This function will remove all downloaded files from civitai as well as vosk model\n"
        "This should only be used when you want to clean up the libraries before pip uninstall\n"
        "Are you sure you want to proceed? (Y/n): ").strip().lower()
        
    if decision != "y":
        print("Clean Up cancelled.")
        return
    
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    
    #known folder
    known_folder = ["downloaded_models", "vosk_models"]
    for folder in known_folder:
        path = os.path.join(cur_dir, folder)
        try:
            remove_dir(path=path)
        except FileNotFoundError:
            pass
        except Exception as e:
            raise Exception(e)
    
    unknown_item = []
    #unknown folder in the directory
    for item_name in os.listdir(cur_dir):
            item_path = os.path.join(cur_dir, item_name)
            if not os.path.isdir(item_path) or "__pycache__" in item_path:
                continue
            unknown_item.append(item_path)
            
    if len(unknown_item) > 0:
        print(f"Warning. Unknowned folder found, did you personally add extra folders? If not, please go to {cur_dir} to delete manually")
        print(f"Unknown folder amount: {len(unknown_item)}")
        for item in unknown_item:
            print(f"Path : {item}") 