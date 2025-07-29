import click

from mosamatic.tasks import DecompressDicomFilesTask


@click.command(help='Decompress DICOM files')
@click.option(
    '--input', 
    required=True, 
    type=click.Path(exists=True), 
    help='Input directory'
)
@click.option(
    '--output', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def decompressdicomfiles(input, output, overwrite):
    """
    Decompresses DICOM files.
    
    Parameters
    ----------
    input : str
        Path to directory with DICOM files.
    
    output : str
        Path to output directory.
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    task = DecompressDicomFilesTask(input, output, overwrite=overwrite)
    task.run()