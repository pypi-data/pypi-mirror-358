import os
import shutil

from mosamatic.tasks.task import Task
from mosamatic.utils import (
    is_dicom, 
    load_dicom,
    is_jpeg2000_compressed,
)


class DecompressDicomFilesTask(Task):
    def __init__(self, input, output, params=None, overwrite=False):
        super(DecompressDicomFilesTask, self).__init__(input, output, params=params, overwrite=overwrite)

    def load_images(self):
        images = []
        for f in os.listdir(self.input()):
            f_path = os.path.join(self.input(), f)
            if is_dicom(f_path):
                images.append(f_path)
        if len(images) == 0:
            raise RuntimeError('Input directory has no DICOM files')
        return images

    def run(self):
        images = self.load_images()
        nr_steps = len(images)
        for step in range(nr_steps):
            source = images[step]
            source_name = os.path.split(source)[1]
            target = os.path.join(self.output(), source_name)
            p = load_dicom(source)
            if is_jpeg2000_compressed(p):
                p.decompress()
                p.save_as(target)
            else:
                shutil.copy(source, target)
            self.set_progress(step, nr_steps)
