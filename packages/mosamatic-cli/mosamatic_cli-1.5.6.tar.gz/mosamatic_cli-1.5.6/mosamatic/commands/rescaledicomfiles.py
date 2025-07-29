import click

from mosamatic.tasks import RescaleDicomFilesTask
from mosamatic.utils import param_dict_from_params


@click.command(help='Rescale DICOM files to target size')
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
    '--params', 
    multiple=True, 
    required=True, 
    type=str, 
    help='Parameters: target_size'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def rescaledicomfiles(input, output, params, overwrite):
    """
    Rescales DICOM images to 512 x 512 (or any square dimension). Images that are
    already at the target size are copied to the output directory without modification.
    
    Parameters
    ----------
    input : str
        Path to directory with images.
    
    output : str
        Path to output directory.
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    params = param_dict_from_params(params)
    task = RescaleDicomFilesTask(input, output, params=params, overwrite=overwrite)
    task.run()