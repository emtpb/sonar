import numpy as np
import pyfds as fd
import scipy.signal as sg


class Shallows:

    def __init__(self, scenario):
        """Create a shallows scenario.

        Args:
            scenario: Select a scenario.
        """

        if scenario is '2020':
            water = fd.AcousticMaterial(1500, 1000, 1e-3, 3e-3)
            self.field = fd.Acoustic2D(t_delta=2e-5, t_samples=2000,
                                       x_delta=0.5e-1, x_samples=1600,
                                       y_delta=0.5e-1, y_samples=400,
                                       material=water)
            self.ping_pre_delay = 1e-3
            self.ping_frequency = 2e3
            self.ping_bandwidth = 2

            submarine_boundary = [
                self.field.get_line_region((40, 6, 45, 6)),
                self.field.get_line_region((45, 6, 46, 5)),
                self.field.get_line_region((46, 5, 46, 4)),
                self.field.get_line_region((46, 4, 45, 3)),
                self.field.get_line_region((45, 3, 40, 3)),
                self.field.get_line_region((40, 3, 38, 4)),
                self.field.get_line_region((38, 4, 38, 5)),
                self.field.get_line_region((38, 5, 40, 6)),
                self.field.get_line_region((42, 6, 42, 8)),
                self.field.get_line_region((42, 8, 44, 8)),
                self.field.get_line_region((44, 8, 42, 6)),
            ]

            for boundary in submarine_boundary:
                self.field.pressure.add_boundary(boundary)

        self.field.x.snap_radius = 1e-3
        self.field.y.snap_radius = 1e-3

    def ping(self, positions, delays=None, show=False):
        """Send delayed pings at the given positions. Positions are relative to the center of
        the field.

        Args:
            positions: Positions to send and receive pings, relative to the center of the field.
            delays: Delay of the pings.
            show: Animate the simulation.

        Returns:
            Returned signals.
        """
        if delays is None:
            delays = np.zeros(len(positions))

        for position, delay in zip(positions, delays):
            self.field.pressure.add_boundary(
                self.field.get_point_region(
                    position=(self.field.x.vector[len(self.field.x.vector) // 2] + position,
                              max(self.field.y.vector))),
                value=sg.gausspulse(self.field.t.vector - self.ping_pre_delay - delay,
                                    self.ping_frequency, self.ping_bandwidth),
                additive=True)
            self.field.pressure.add_output(
                self.field.get_point_region(
                    position=(self.field.x.vector[len(self.field.x.vector) // 2] + position,
                              max(self.field.y.vector))))

        if show:
            animator = fd.Animator2D(field=self.field, scale=0.1)
            animator.start_simulation()
        else:
            self.field.simulate()

        return [output.mean_signal for output in self.field.pressure.outputs]
