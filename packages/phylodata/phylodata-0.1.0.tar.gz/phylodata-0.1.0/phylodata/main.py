import click
import subprocess

@click.group()
def phylodata():
    ...


@phylodata.command(help="Process an experiment before uploading it to PhyloData.")
def process():
    subprocess.Popen(["streamlit", "run", "phylodata/ui.py"])

@phylodata.command(help="Validate if a given JSON file contains valid PhyloData metadata.")
@click.argument('file_path', type=click.Path(exists=True), help="The path to the JSON file to validate.")
def validate(file_path: str):
    print(file_path)
