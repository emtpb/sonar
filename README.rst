=====
sonar
=====

An exercise environment to experiment with acoustic arrays using sonar as an example.


Installation
============

As the environment consists of a single Python class, no installation of sonar is required.
Placing *sonar.py* in the working directory should suffice.
A Python interpreter is, however, required.
We recommend using `Anaconda <https://www.anaconda.com/>`_.
The field simulations are implemented using the Python package *pyfds*, which can be installed
using *pip* (comes with Anaconda) by the following command:

.. code-block:: bash

    pip install pyfds

Usage
=====

Here is a minimal working example (to be placed in the same directory as *sonar.py*):

.. code-block:: python

    from sonar import Shallows

    if __name__ == '__main__':

        field = Shallows(scenario='2020')
        result = field.ping(
            positions=[0, 1],
            delays=[0, 0.1e-3],
            show=True
        )

The first line imports the class :code:`Shallows` from the :code:`sonar` module (the Python file
*sonar.py*).
The following statement (placement in :code:`if __name__ == '__main__':`) is necessary for
the animation of the field simulation to work.
Next up, an object of the type :code:`Shallows` called :code:`field` is created, using the
scenario for 2020.
The last statement allows you to send a number of pings (acoustic impulses) at given positions
and with delays.
Note that all delays should be positive.
The example sends pings at 0 m (center of the field) and 1 m with the first ping having no delay
and the second one being delayed by 0.1 ms.
The display of the field simulation can be disabled by setting :code:`show=False`.

2020 scenario
-------------

This scenario constitutes a classic echolocation example and can be used to experiment with sonar
imaging algorithms.
Note that not all excitation positions are valid, as the field is spatially quantized with an
increment of 0.05 m.
After the simulation is finished, the return value of :code:`ping` contains a list of echo signals
recorded at the positions the pings where send at.
The transmitted signals are also present in these signals.

2021 scenario
-------------

This scenario simulates medical ultrasound applications, e.g. lithotripsy.
A small, high-density object is placed at a randomized position in the field.
The field is spatially quantized with an increment of 0.5 mm, so excitation positions need to
adhere to this quantization.
The return value of :code:`ping` is a tuple that contains the signal at the center of the
high-density object and a list of echo signals recorded at the positions the pings where send at.
