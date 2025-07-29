import click

from mosamatic.tasks import SegmentMuscleFatL3Task
from mosamatic.utils import input_dict_from_input, param_dict_from_params


@click.command(help='Extracts muscle and fat regions from CT images at L3 (uses PyTorch)')
@click.option(
    '--input', 
    multiple=True, 
    required=True, 
    type=click.Path(), 
    help='Named input directories: images, model_files'
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
    help='Parameters: model_verion'
)
@click.option(
    '--overwrite', 
    default=False, 
    type=click.BOOL, 
    help='Overwrite (true/false)'
)
def segmentmusclefatl3(input, output, params, overwrite):
    """
    Automatically extracts muscle and fat regions from CT images at the L3
    vertebral level. Outputs segmentation files in NumPy (.npy) format. This
    command uses a PyTorch AI model.
    
    Parameters
    ----------
    input : str
        [images] Path to directory with images.
        [model_files] Path to directory with PyTorch model files. This should
            be the following files:
            - model-<version>.pt
            - contour_model-<version>.pt
            - params-<version>.json
    
    output : str
        Path to output directory with segmentation files.
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    task = SegmentMuscleFatL3Task(
        input_dict_from_input(input), 
        output, 
        params=param_dict_from_params(params), 
        overwrite=overwrite,
    )
    task.run()