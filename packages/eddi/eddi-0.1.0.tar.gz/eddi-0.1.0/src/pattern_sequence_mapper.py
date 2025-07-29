import numpy as np
from perlin_numpy import generate_perlin_noise_3d
import cv2

from src.pipeline_node import PipelineNode


class PatternSequenceMapper(PipelineNode):
    """
    This is a generic pattern sequence mapper class that provides
    the "Fundamental frequency" so to speak for the lights.
    The patterns loaded here will be the baseline lights that run.
    Other sequence patterns will be added on top of the patterns that
    run here.

    TODO - currently a simple oscillation is programmed, but
    we could load in really specific world looks here that are
    dynamic or static.

    TODO - additionally, this class is where event triggered "scenes"
    can be specified / triggered via midi or osc or whatever
    """

    def __init__(self, director=None):
        self.director = director
        self.counter = 0
        self.weight = self.director.config["output_weights"]["pattern_sequencer"]
        self.name = "pattern_sequencer"
        self.modulator_value = 75
        self.sequence_mode = self.director.config["pattern_sequencer"]["sequence_mode"]
        self.perline_range = self.director.config["pattern_sequencer"][
            "default_perline_range"
        ]
        self.amplitude = 0.3
        self.color_mode = self.director.config["pattern_sequencer"]["color_mode"]
        if self.sequence_mode == "oscillator1":
            self.samples = np.linspace(
                self.amplitude,
                1 - self.amplitude,
                int(self.modulator_value),
                endpoint=False,
            )
            r = reversed(self.samples)
            self.samples = list(r) + self.samples
        elif self.sequence_mode == "oscillator2":
            self.samples = np.linspace(
                -self.amplitude,
                self.amplitude,
                int(self.modulator_value),
                endpoint=False,
            )
        elif self.sequence_mode == "perlin":
            # if self.color_mode == "ocean":
            # self.modulator_value = 25
            # self.perline_range = (0.3, 0.9)
            self.samples = self.generate_perlin_noise()

    def process_input_device_values(self, input_device_instance=None):
        out_value = 0
        sample_idx = int(self.counter % self.modulator_value)
        if self.sequence_mode == "static":
            constant = 0.2
            front = constant
            back = constant
            middle = constant
            top = constant
            bottom = constant
            left = constant
            right = constant
        elif self.sequence_mode == "oscillator1":
            out_value = self.samples[sample_idx]
            out_value = self.constrain(out_value)
            back = out_value
            front = out_value
            bottom = out_value
            top = out_value
            right = out_value
            left = out_value
            middle = out_value
        elif self.sequence_mode == "oscillator2":
            out_value = self.amplitude - np.abs(self.samples[sample_idx])
            out_value2 = np.abs(self.samples[sample_idx])
            back = out_value
            front = out_value2
            bottom = out_value2
            top = out_value
            right = out_value
            left = out_value2
            middle = self.amplitude
        elif self.sequence_mode == "perlin":
            back = self.samples[sample_idx, 0, 0]
            bottom = self.samples[sample_idx, 0, 1]
            front = self.samples[sample_idx, 0, 2]
            right = self.samples[sample_idx, 0, 3]
            top = self.samples[sample_idx, 0, 4]
            left = self.samples[sample_idx, 0, 5]
            middle = self.amplitude

        output = {
            "back": (self.mod_r(back), self.mod_g(back), self.mod_b(back)),
            "front": (self.mod_r(front), self.mod_g(front), self.mod_b(front)),
            "bottom": (self.mod_r(bottom), self.mod_g(bottom), self.mod_b(bottom)),
            "top": (self.mod_r(top), self.mod_g(top), self.mod_b(top)),
            "right": (self.mod_r(right), self.mod_g(right), self.mod_b(right)),
            "left": (self.mod_r(left), self.mod_g(left), self.mod_b(left)),
            "middle": (self.mod_r(middle), self.mod_g(middle), self.mod_b(middle)),
        }
        self.output = [output]
        self.counter += 1

    def mod_r(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.05
        elif self.color_mode == "lava":
            out = value * 1
        elif self.color_mode == "sunshine":
            out = value * 0.9

        if self.director.config["pattern_sequencer"]["director_control"]["enabled"]:
            out = (
                value
                * self.director.config["pattern_sequencer"]["director_control"][
                    "r_ratio"
                ]
            )
        return self.constrain(out)

    def mod_g(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.8
        elif self.color_mode == "lava":
            out = value * 0.10
        elif self.color_mode == "sunshine":
            out = value * 0.9
        elif self.director.config["director_control"]["enabled"]:
            out = value * self.director.config["director_control"]["g_ratio"]

        if self.director.config["pattern_sequencer"]["director_control"]["enabled"]:
            out = (
                value
                * self.director.config["pattern_sequencer"]["director_control"][
                    "g_ratio"
                ]
            )
        return self.constrain(out)

    def mod_b(self, value):
        out = value
        if self.color_mode == "ocean":
            out = value * 0.95
        elif self.color_mode == "lava":
            out = value * 0.05
        elif self.color_mode == "sunshine":
            out = value * 0.10

        if self.director.config["pattern_sequencer"]["director_control"]["enabled"]:
            out = (
                value
                * self.director.config["pattern_sequencer"]["director_control"][
                    "b_ratio"
                ]
            )
        return self.constrain(out)

    def constrain(self, value, min=0.0, max=1.0):
        if value < min:
            return min
        if value > max:
            return max
        return value

    def generate_perlin_noise(self):
        # https://github.com/pvigier/perlin-numpy
        # https://weber.itn.liu.se/~stegu/simplexnoise/simplexnoise.pdf
        np.random.seed(0)
        d = self.modulator_value
        noise = generate_perlin_noise_3d(
            (d, 1, 6), (1, 1, 6), tileable=(True, True, True)
        )

        samples = cv2.normalize(
            noise, noise, self.perline_range[0], self.perline_range[1], cv2.NORM_MINMAX
        )

        return samples
