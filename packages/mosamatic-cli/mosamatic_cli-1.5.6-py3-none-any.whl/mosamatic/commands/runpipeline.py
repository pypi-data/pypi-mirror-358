import click

from mosamatic.pipelines import DefaultPipeline
from mosamatic.utils import param_dict_from_params, input_dict_from_input


@click.command(help='Runs default body composition pipeline')
@click.option(
    '--input', 
    multiple=True,
    required=True, 
    type=click.Path(exists=True), 
    help='Named input directories: images, model_files',
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
    help='Named parameters: model_type, model_version, fig_width, fig_height, full_scan'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def runpipeline(input, output, params, overwrite):
    """
    Runs default body composition pipeline on images in input directory. The input 
    directory can either contain a set of L3 images (one for each patient) or a set
    of DICOM images corresponding to a single CT scan. In the latter case, provide
    the parameter full_scan=true.
    
    Parameters
    ----------
    input : dict
        Path to input directory with L3 images or CT scan files

        {
            'images': '/path/to/images',
            'model_files': '/path/to/model_files',
        }
    
    output : str
        Path to output directory

    params : dict
        Dictionary of parameters:

        {
            'model_type': ['pytorch'|'tensorflow'],
            'model_version': '<model_version>',
            'fig_width': '<figure width for PNG images>',
            'fig_height': '<figure height for PNG images>',
            'full_scan': '<true|false>',
        }
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    pipeline = DefaultPipeline(
        input=input_dict_from_input(input), 
        output=output, 
        params=param_dict_from_params(params), 
        overwrite=overwrite,
    )
    pipeline.run()