import logging
import os
import pathlib

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)
log.handlers = logging.getLogger("__main__").handlers

from nectarchain.makers.calibration import PedestalNectarCAMCalibrationTool

run_number = 3938
max_events = 2999
events_per_slice = 300
outfile = os.environ["NECTARCAMDATA"] + "/runs/pedestal_{}.h5".format(run_number)

tool = PedestalNectarCAMCalibrationTool(
    progress_bar=True,
    run_number=run_number,
    max_events=max_events,
    events_per_slice=events_per_slice,
    log_level=20,
    output_path=outfile,
    overwrite=True,
    filter_method="WaveformsStdFilter",
    wfs_std_threshold=4.0,
)

tool.initialize()
tool.setup()

tool.start()
output = tool.finish(return_output_component=True)
