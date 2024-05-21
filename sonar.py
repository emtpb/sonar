import numpy as np
import pyfds as fd
import scipy.signal as sg


class Shallows:

    def __init__(self, scenario: str):
        """Create a shallows scenario.

        Args:
            scenario: Select a scenario.
        """
        self.postprocessor = None
        if scenario == '2020':
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

        elif scenario == '2021':
            water = fd.AcousticMaterial(1500, 1000, 1e-3, 3e-3)
            stone = fd.AcousticMaterial(1500, 5000)
            self.field = fd.Acoustic2D(t_delta=1e-7, t_samples=2700,
                                       x_delta=0.5e-3, x_samples=1600,
                                       y_delta=0.5e-3, y_samples=400,
                                       material=water)
            self.ping_pre_delay = 1e-5
            self.ping_frequency = 200e3
            self.ping_bandwidth = 2

            self.field.x.snap_radius = 25e-5
            self.field.y.snap_radius = 25e-5

            pos_x = 0.3 + np.random.rand() * 0.2
            pos_y = 0.075 + np.random.rand() * 0.05
            size = 0.0075
            self.field.add_material_region(
                self.field.get_tri_region((pos_x, pos_y - size,
                                           pos_x + size, pos_y,
                                           pos_x - size, pos_y)), stone)
            self.field.add_material_region(
                self.field.get_tri_region((pos_x, pos_y + size,
                                           pos_x + size, pos_y,
                                           pos_x - size, pos_y)), stone)
            self.field.pressure.add_output(
                self.field.get_point_region((pos_x, pos_y), name='stone'))
            self.postprocessor = lambda output: (output[0], output[1:])

        else:
            raise RuntimeError('Unknown scenario {}'.format(scenario))

    def ping(self, positions, delays=None, show=False):
        """Send delayed pings at the given positions. Positions are relative to
        the centre of the field.

        Args:
            positions: Positions to send and receive pings, relative to the
                centre of the field.
            delays: Delay of the pings.
            show: Animate the simulation.

        Returns:
            Returned signals.
        """

        # Reset field to allow for repeated execution.
        self.field.pressure.values = np.zeros_like(self.field.pressure.values)
        self.field.velocity_x.values = \
            np.zeros_like(self.field.velocity_x.values)
        self.field.velocity_y.values = \
            np.zeros_like(self.field.velocity_y.values)
        self.field.step = 0

        if delays is None:
            delays = np.zeros(len(positions))

        for position, delay in zip(positions, delays):
            self.field.pressure.add_boundary(
                self.field.get_point_region(
                    position=(
                        self.field.x.vector[len(self.field.x.vector) // 2]
                        + position, max(self.field.y.vector))),
                value=sg.gausspulse(
                    self.field.t.vector - self.ping_pre_delay - delay,
                    self.ping_frequency, self.ping_bandwidth),
                additive=True)
            self.field.pressure.add_output(
                self.field.get_point_region(
                    position=(
                        self.field.x.vector[len(self.field.x.vector) // 2]
                        + position, max(self.field.y.vector))))

        if show:
            animator = fd.Animator2D(field=self.field, scale=0.1)
            animator.show_boundaries = False
            animator.show_materials = False
            animator.show_output = False
            animator.start_simulation()
        else:
            self.field.simulate()

        if self.postprocessor:
            return self.postprocessor(
                [output.mean_signal for output in self.field.pressure.outputs])
        else:
            return \
                [output.mean_signal for output in self.field.pressure.outputs]


class Step:

    def __init__(self, scenario: str, height: float, distance: float):
        """Create a scenario with a step on the seafloor.

        Args:
            scenario: Select a scenario.
        """
        if scenario == '2024':
            water = fd.AcousticMaterial(1500, 1000, 1e-3, 3e-3)
            self.field = fd.Acoustic2D(t_delta=1e-5, t_samples=4000,
                                       x_delta=0.5e-1, x_samples=1600,
                                       y_delta=0.5e-1, y_samples=400,
                                       material=water)
            self.ping_pre_delay = 1.25e-3
            self.ping_frequency = 5e3
            self.ping_bandwidth = 0.25

            # Prevent field from wrapping around
            self.field.pressure.add_boundary(
                self.field.get_line_region(
                    (0, 0, 0, self.field.y.vector[-1])
                ))

            # Add step with a small bevel
            self.field.pressure.add_boundary(
                self.field.get_line_region(
                    (40 + distance, 0, 40 + distance, height - 0.1)
                ))
            self.field.pressure.add_boundary(
                self.field.get_line_region(
                    (40 + distance, height - 0.1, 40.1 + distance, height)
                ))
            self.field.pressure.add_boundary(
                self.field.get_line_region(
                    (40.1 + distance, height, self.field.x.vector[-1], height)
                ))

            self.field.x.snap_radius = 0.25e-1
            self.field.y.snap_radius = 0.25e-1

        else:
            raise RuntimeError('Unknown scenario {}'.format(scenario))

    def ping(self, size: float, show: bool = False):
        """Send a ping with the given size of the transducer at the centre of
        the field

        Args:
            size: Size of the transducer.
            show: Animate the simulation.

        Returns:
            Returned signals.
        """

        # Reset field to allow for repeated execution.
        self.field.pressure.values = np.zeros_like(self.field.pressure.values)
        self.field.velocity_x.values = \
            np.zeros_like(self.field.velocity_x.values)
        self.field.velocity_y.values = \
            np.zeros_like(self.field.velocity_y.values)
        self.field.step = 0

        ex_line = self.field.get_line_region(
            (40 - size / 2, self.field.y.vector[-1],
             40 + size / 2, self.field.y.vector[-1])
        )
        self.field.pressure.add_boundary(
            ex_line,
            value=sg.gausspulse(
                self.field.t.vector - self.ping_pre_delay,
                self.ping_frequency, self.ping_bandwidth),
            additive=True)
        self.field.pressure.add_output(ex_line)

        if show:
            animator = fd.Animator2D(field=self.field, scale=0.2)
            animator.show_boundaries = True
            animator.show_materials = False
            animator.show_output = False
            animator.start_simulation()
        else:
            self.field.simulate()

        return self.field.pressure.outputs[0].signals[0]
