import os

from mosamatic.tasks.task import Task
from mosamatic.tasks import (
    DecompressDicomFilesTask, 
    RescaleDicomFilesTask, 
    SegmentMuscleFatL3Task,
    SegmentMuscleFatL3TensorFlowTask,
    CreatePngsFromSegmentationsTask,
    CalculateScoresTask,
)


class DefaultPipeline(Task):
    def __init__(self, input, output, params=None, overwrite=False):
        super(DefaultPipeline, self).__init__(input, output, params, overwrite)
        model_type = self.param('model_type')
        segmentation_task_class = SegmentMuscleFatL3Task if model_type == 'pytorch' else SegmentMuscleFatL3TensorFlowTask
        self._tasks = [

            DecompressDicomFilesTask(
                input=self.input('images'), 
                output=output, 
                overwrite=overwrite,
            ),

            RescaleDicomFilesTask(
                input=os.path.join(output, 'DecompressDicomFilesTask'), 
                params={
                    'target_size': self.param('target_size')
                }, 
                output=output, 
                overwrite=overwrite,
            ),

            segmentation_task_class(
                input={
                    'images': os.path.join(output, 'RescaleDicomFilesTask'),
                    'model_files': self.input('model_files'),
                }, params={
                    'model_version': self.param('model_version')
                }, 
                output=output, 
                overwrite=overwrite,
            ),

            CreatePngsFromSegmentationsTask(
                input=os.path.join(output, 'SegmentMuscleFatL3Task'), 
                params={
                    'fig_width': self.param('fig_width'), 
                    'fig_height': self.param('fig_height'),
                }, 
                output=output, 
                overwrite=overwrite,
            ),

            CalculateScoresTask(
                input={
                    'images': os.path.join(output, 'RescaleDicomFilesTask'),
                    'segmentations': os.path.join(output, 'SegmentMuscleFatL3Task'),
                }, 
                output=output, 
                params={'file_type': 'npy'}, 
                overwrite=overwrite,
            )
        ]

    def run(self):
        for task in self._tasks:
            task.run()