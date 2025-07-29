"""
Extract pedestals from pedestal file
"""

from ctapipe.calib.camera.pedestals import PedestalCalculator
from ctapipe.containers import PedestalContainer
from ctapipe.core import Provenance, Tool, traits
from ctapipe.io import EventSource, HDF5TableWriter
from traitlets import Dict, List, Unicode

__all__ = ["PedestalHDF5Writer"]


class PedestalHDF5Writer(Tool):
    """
    Example of tool that extract the pedestal value per pixel and write the pedestal
    container to disk in a hdf5 file
    """

    name = "PedestalHDF5Writer"
    description = "Generate a HDF5 file with pedestal values"

    output_file = Unicode("pedestal.hdf5", help="Name of the output file").tag(
        config=True
    )

    calculator_product = traits.Enum(PedestalCalculator, default="PedestalIntegrator")

    aliases = Dict(
        dict(
            input_file="EventSource.input_url",
            max_events="EventSource.max_events",
            tel_id="PedestalCalculator.tel_id",
            sample_duration="PedestalCalculator.sample_duration",
            sample_size="PedestalCalculator.sample_size",
            n_channels="PedestalCalculator.n_channels",
            charge_product="PedestalCalculator.charge_product",
        )
    )

    classes = List(
        [EventSource, PedestalCalculator, PedestalContainer, HDF5TableWriter]
        + traits.classes_with_traits(PedestalCalculator)
    )

    def __init__(self, **kwargs):
        """
        Example of tool that extract the pedestal value per pixel and write the pedestal
        container to disk
        """

        super().__init__(**kwargs)
        self.eventsource = None
        self.pedestal = None
        self.container = None
        self.writer = None
        self.group_name = None

    def setup(self):
        kwargs = dict(parent=self)
        self.eventsource = EventSource.from_config(**kwargs)
        self.pedestal = PedestalCalculator.from_name(self.calculator_product, **kwargs)
        self.group_name = "tel_" + str(self.pedestal.tel_id)

        self.writer = HDF5TableWriter(
            filename=self.output_file, group_name=self.group_name, overwrite=True
        )

    def start(self):
        """
        Example of tool that extract the pedestal value per pixel and write the pedestal
        container to disk
        """

        write_config = True

        # loop on events
        for count, event in enumerate(self.eventsource):
            # fill pedestal monitoring container
            if self.pedestal.calculate_pedestals(event):
                ped_data = event.mon.tel[self.pedestal.tel_id].pedestal

                if write_config:
                    ped_data.meta["config"] = self.config
                    write_config = False

                self.log.debug(f"write event in table: {self.group_name}/pedestal")

                # write data to file
                self.writer.write("pedestal", ped_data)

    def finish(self):
        Provenance().add_output_file(self.output_file, role="mon.tel.pedestal")
        self.writer.close()


def main():
    exe = PedestalHDF5Writer()
    exe.run()


if __name__ == "__main__":
    main()
