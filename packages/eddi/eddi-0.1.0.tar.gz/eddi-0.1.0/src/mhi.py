import cv2
import numpy as np
import math
import copy

from skimage.draw import line

from collections import deque
from src.pipeline_node import PipelineNode


class MotionHistoryImager(PipelineNode):
    """
    This class take input device state representing people joint coordinates
    and produces a volume of Motion History Images, Motion Engergy Images and
    a volume of Hu Moments
    """

    def __init__(
        self,
        min_max_dimensions,
        frame_window_length,
        frame_decay,
        display_canvas=False,
        display_params={},
        director=None,
    ):
        self.director = director
        self.input_joint_list = []
        # for normalizing constants
        self.min_x = min_max_dimensions["min_x"]
        self.max_x = min_max_dimensions["max_x"]
        self.min_y = min_max_dimensions["min_y"]
        self.max_y = min_max_dimensions["max_y"]
        self.min_z = min_max_dimensions["min_z"]
        self.max_z = min_max_dimensions["max_z"]

        self.display_canvas = display_canvas
        self.display_params = display_params
        # set each MHI canvas's dimensions
        self.w = int(min_max_dimensions["max_x"] - min_max_dimensions["min_x"])
        self.h = int(min_max_dimensions["max_y"] - min_max_dimensions["min_y"])

        self.canvas_center = (self.w / 2, self.h / 2)
        self.center_joint = "torso"  # name of joint to center MHI on

        self.tracking = False  # are we tracking any user?
        # self.init_canvas = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.init_canvas = np.zeros((self.h, self.w), dtype=np.uint8)
        # Motion History Images (Time Decayed)
        self.MHI_canvases = {}  # will store a MHI canvas for each person
        # Motion Energy Images
        self.MEI_canvases = {}  # will store a MEI canvas for each person
        # Store image moments for each person
        self.MHI_Hu_moments = {}
        self.MEI_Hu_moments = {}
        # Store volume of canvases / moments
        self.MHI_volumes = {}  # will store a VMHI for each person
        self.MEI_volumes = {}  # will store a VMEI for each person
        self.MHI_moments_volumes = {}
        self.MEI_moments_volumes = {}
        self.energy_moment_delta_volumes = {}
        # How many frames in a volume
        self.tau = frame_window_length
        # How fast will energy decay per frame (MHI)?
        # i.e. 0.9 = 90% of previous pixel value this frame
        self.decay = frame_decay

        # joint position tracking
        self.joint_position_indices = {}
        self.previous_joint_position_indices = {}  # for smoothing between frames

        # For drawing skel - should be a DAG
        # NB: not focusing below hips for now
        self.joint_connections = {
            "head": ["neck"],
            "neck": ["leftShoulder", "rightShoulder", "torso"],
            "leftShoulder": ["leftElbow", "torso"],
            "leftElbow": ["leftHand"],
            "leftHand": [],
            "rightShoulder": ["rightElbow", "torso"],
            "rightElbow": ["rightHand"],
            "rightHand": [],
            "torso": ["leftHip", "rightHip"],
            "leftHip": ["rightHip"],
            # "leftHip": ["leftKnee", "rightHip"],
            # "rightHip": ["rightKnee"],
            # "leftKnee": ["leftFoot"],
            # "rightKnee": ["rightFoot"],
            # "leftFoot": [],
            # "rightFoot": [],
        }

        super().__init__(min_max_dimensions)

    def update_config_values(self):
        self.min_max_dimensions = (self.director.config["space_min_max_dimensions"],)
        self.frame_window_length = self.director.config["frame_window_length"]
        self.frame_decay = self.director.config["frame_decay"]

    def input_object_is_tracking_user(self):
        return any(list(self.input_object_instance.tracking.values()))

    def process_input_device_values(self, input_object_instance):
        """
        This is the primary entry point for this pipeline node
        """
        self.update_config_values()
        self.input_object_instance = input_object_instance
        if self.input_object_is_tracking_user():
            self.tracking = True
        else:
            self.tracking = False

        if not self.input_joint_list:
            self.input_joint_list = input_object_instance.joint_list

        self.process_data_frame(input_object_instance)
        if self.display_canvas:
            self.display_canvases()
        # self.display_info_window()
        self.energy_moment_delta_volumes = self.process_output_matrices()

    def process_data_frame(self, input_object_instance):
        """
        This pipeline caller method parses the skel joints from the input object
        Then it calls the function to render polygons agains the skel
        Then it computes a motion history image volume and a motion energy image volume
        """
        if not input_object_instance.people.items():
            return
        for person, attrs in input_object_instance.people.items():
            if person in self.MHI_canvases:
                self.decay_MHI_canvas(person)
            self.check_and_initialize_canvases_and_volumes(person)
            self.parse_skeleton_joints(person, attrs)
            self.fill_skeleton(person)
            self.post_process_canvas(person)
            self.compute_moments(person)
            self.update_image_volumes(person)
            self.update_moment_volumes(person)
        self.previous_joint_position_indices = copy.copy(self.joint_position_indices)

    def post_process_canvas(self, person):
        self.MHI_canvases[person]
        self.MEI_canvases[person]
        cv2.medianBlur(self.MHI_canvases[person], 7)
        cv2.medianBlur(self.MEI_canvases[person], 7)

    def safe_log10(self, x, eps=1e-10):
        """
        protect against zero division edge cases
        this basically replaces 0 with extremely small val
        """
        result = np.where(x > eps, x, -10)
        np.log10(result, out=result, where=result > 0)
        return result

    def compute_moments(self, person):
        """
        This method computes image moments and then Hu moments
        for each person's current MEI and MHI canvas. It converts
        the result to log scale.
        """
        mhi_canvas = np.copy(self.MHI_canvases[person])
        mei_canvas = np.copy(self.MEI_canvases[person])

        mhi_moments = cv2.moments(mhi_canvas)
        mei_moments = cv2.moments(mei_canvas)
        mhi_hu_moments = cv2.HuMoments(mhi_moments).flatten()
        mei_hu_moments = cv2.HuMoments(mei_moments).flatten()
        # Log scale hu moments
        for i in range(0, 7):
            mei_hu_moments[i] = (
                -1
                * math.copysign(1.0, mei_hu_moments[i])
                * self.safe_log10(abs(mei_hu_moments[i]))
            )
            mhi_hu_moments[i] = (
                -1
                * math.copysign(1.0, mhi_hu_moments[i])
                * self.safe_log10(abs(mhi_hu_moments[i]))
            )

        self.MEI_Hu_moments[person] = mei_hu_moments
        self.MHI_Hu_moments[person] = mhi_hu_moments

    def decay_MHI_canvas(self, person):
        # update energy values with decay rate
        canvas = self.MHI_canvases[person]
        canvas[canvas > 0] = canvas[canvas > 0] - self.decay
        canvas[canvas < 0] = 0  # stay above 0

    def fill_skeleton(self, person):
        """
        For a person tracked in the input object instance
        Draw polyfilled skeleton for MEI and MHI canvases
        """
        if (
            person not in self.MHI_canvases
            or person not in self.MEI_canvases
            or not self.tracking
        ):
            return
        MEI_canvas = self.MEI_canvases[person]
        MHI_canvas = self.MHI_canvases[person]

        # each polygon below will be filled
        tri1 = "head", "leftShoulder", "neck", "rightShoulder"
        tri2 = "leftShoulder", "leftElbow", "leftHand"
        tri3 = "rightShoulder", "rightElbow", "rightHand"
        tri4 = "torso", "leftShoulder", "rightShoulder"
        tri5 = "torso", "leftHip", "rightHip"
        tri6 = "leftHand", "torso", "leftShoulder"
        tri7 = "rightHand", "torso", "rightShoulder"
        tri8 = (
            "leftHand",
            "rightHand",
            "head",
        )
        tri8 = (
            "leftHand",
            "rightHand",
            "rightShoulder",
            "leftShoulder",
        )
        for joint_list in [tri1, tri2, tri3, tri4, tri5, tri6, tri7, tri8]:
            joint_positions = []
            joint_inputs = copy.copy(self.joint_position_indices[person])
            joints = [
                joint_inputs[joint] for joint in joint_list if joint in joint_inputs
            ]
            joint_positions = np.array(list(joints))
            if len(joint_positions):
                cv2.fillConvexPoly(MHI_canvas, joint_positions, 255)
                cv2.fillConvexPoly(MEI_canvas, joint_positions, 255)

        ## Here, use the previous coords and the current coords to "fill in"
        # the gaps between frames so image is smooth
        if (
            person in self.previous_joint_position_indices
            and person in self.joint_position_indices
        ):
            if (
                self.previous_joint_position_indices[person]
                != self.joint_position_indices[person]
            ):
                # in each filler array, first item is previous joint position,
                # next is same joint in current position,
                # then the third complete triangle
                fillers = [
                    ["leftHand", "leftHand", "leftElbow"],
                    ["leftHand", "leftHand", "rightHand"],
                    ["rightHand", "rightHand", "rightElbow"],
                    ["rightHand", "rightHand", "leftHand"],
                    ["rightShoulder", "rightShoulder", "head"],
                    ["leftShoulder", "leftShoulder", "head"],
                    ["head", "head", "leftShoulder"],
                    ["head", "head", "rightShoulder"],
                    ["leftElbow", "leftElbow", "leftHand"],
                    ["rightElbow", "rightElbow", "rightHand"],
                    ["leftElbow", "leftElbow", "leftShoulder"],
                    ["rightElbow", "rightElbow", "rightShoulder"],
                    ["leftHip", "leftHip", "torso"],
                    ["rightHip", "rightHip", "torso"],
                ]
                previous = self.previous_joint_position_indices[person]
                current = self.joint_position_indices[person]
                for poly in fillers:
                    self.draw_filler_joint_polygon(
                        prev_joint=poly[0],
                        current_joint_1=poly[1],
                        current_joint_2=poly[2],
                        previous_joints=previous,
                        current_joints=current,
                        MEI_canvas=MEI_canvas,
                        MHI_canvas=MHI_canvas,
                    )

    def draw_filler_joint_polygon(
        self,
        prev_joint,
        current_joint_1,
        current_joint_2,
        previous_joints,
        current_joints,
        MHI_canvas,
        MEI_canvas,
    ):
        if (
            prev_joint in previous_joints
            and current_joint_1 in current_joints
            and current_joint_2 in current_joints
        ):
            p = previous_joints[prev_joint]
            c1 = current_joints[current_joint_1]
            c2 = current_joints[current_joint_2]
            poly_coords = np.array([p, c1, c2])
            cv2.fillConvexPoly(MHI_canvas, poly_coords, 255)
            cv2.fillConvexPoly(MEI_canvas, poly_coords, 255)

    def parse_skeleton_joints(self, person, attrs):
        # init joint position lookup table if we don't have one
        if not self.tracking:
            return
        if person not in self.joint_position_indices:
            self.joint_position_indices[person] = {}
        joint_positions = copy.copy(self.joint_position_indices[person])

        self.MEI_canvases[person] = np.copy(self.init_canvas)
        # Only need this if drawing the joints
        # canvas = self.MHI_canvases[person]

        # create offset for centering skel on canvas (torso is good choice)
        if self.center_joint not in attrs:
            return

        center_joint_x = self.normalize_point(
            attrs[self.center_joint]["x"], self.min_x, self.max_x, 0, self.w
        )
        center_joint_y = self.normalize_point(
            attrs[self.center_joint]["y"], self.min_y, self.max_y, 0, self.h
        )
        offset_x = int(center_joint_x - self.canvas_center[0])
        offset_y = int(center_joint_y - self.canvas_center[1])

        for joint in self.input_joint_list:
            if joint in attrs:
                x = int(
                    self.normalize_point(
                        attrs[joint]["x"], self.min_x, self.max_x, 0, self.w
                    )
                )
                y = int(
                    self.normalize_point(
                        attrs[joint]["y"], self.min_y, self.max_y, 0, self.h
                    )
                )
                z = int(
                    self.normalize_point(
                        attrs[joint]["z"], self.min_z, self.max_z, 0, 255, True
                    )
                )

                x_prime = x - offset_x
                y_prime = y - offset_y
                # offsets may push some coords out of bounds
                # if so, skip this joint
                joint_out_of_bounds = (
                    (x_prime >= self.w)
                    or (x_prime <= 0)
                    or (y_prime >= self.h)
                    or (y_prime <= 0)
                )
                if joint_out_of_bounds:
                    continue

                joint_positions[joint] = (x_prime, y_prime)
            self.joint_position_indices[person] = joint_positions
        # self.connect_skel_joints(person)

    def check_and_initialize_canvases_and_volumes(self, person):
        """
        Instantiate canvases for each person as well as volume storage
        """
        if person not in self.MHI_canvases or self.tracking == False:
            self.MHI_canvases[person] = np.copy(self.init_canvas)
        if person not in self.MEI_canvases or self.tracking == False:
            self.MEI_canvases[person] = np.copy(self.init_canvas)
        if person not in self.MHI_volumes:
            self.MHI_volumes[person] = deque(maxlen=self.tau)
        if person not in self.MEI_volumes:
            self.MEI_volumes[person] = deque(maxlen=self.tau)
        # also init hu moment objects
        if person not in self.MHI_moments_volumes:
            self.MHI_moments_volumes[person] = deque(maxlen=self.tau)
        if person not in self.MEI_moments_volumes:
            self.MEI_moments_volumes[person] = deque(maxlen=self.tau)

    def connect_skel_joints(self, person):
        """
        For each joint position, use the initialized joint_connections DAG
        to draw a skeleton on the canvas

        NOTE: this is only implemented currently for MHI canvas
        Not using this currently in favor of the polyfilled skeleton
        """
        canvas = self.MHI_canvases[person]
        for joint, connections in self.joint_connections.items():
            if joint in self.joint_position_indices[person]:
                x1, y1 = self.joint_position_indices[person][joint]
                for connection in connections:
                    if connection in self.joint_position_indices[person]:
                        x2, y2 = self.joint_position_indices[person][connection]
                        rr, cc = line(x1, y1, x2, y2)
                        # This is from an attempt to depth interpolate the line color
                        # for the z axis - however, because of the occlusion problem
                        # with MHI, going a different route with the volume MHI
                        # leaving for now
                        # z1 = canvas[y1, x1, 0]
                        # z2 = canvas[y2, x2, 0]
                        # depth_interpolated_values = np.linspace(
                        #     z1, z2, num=len(rr)
                        # ).astype("uint8")

                        # canvas[cc, rr, 0] = depth_interpolated_values
                        # canvas[cc, rr, 1:] = 255
                        canvas[cc, rr] = 255

    def update_image_volumes(self, person):
        # we only want the values of the most recent position
        # so threshold the canvas to zero values other than 255
        mhi_canvas = np.copy(self.MHI_canvases[person])
        mei_canvas = np.copy(self.MEI_canvases[person])
        mhi_canvas[mhi_canvas < 0] = 0
        mei_canvas[mei_canvas < 0] = 0
        self.MHI_volumes[person].append(mhi_canvas)
        self.MEI_volumes[person].append(mei_canvas)

    def update_moment_volumes(self, person):
        mhi_hu_moments = np.copy(self.MHI_Hu_moments[person])
        mei_hu_moments = np.copy(self.MEI_Hu_moments[person])
        self.MHI_moments_volumes[person].append(mhi_hu_moments)
        self.MEI_moments_volumes[person].append(mei_hu_moments)

    def display_info_window(self):
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontscale = 0.55
        color = 255
        info_window = np.zeros((400, 1200))
        info_window = cv2.putText(
            info_window,
            str(self.MHI_Hu_moments),
            (10, 50),
            fontFace=font,
            fontScale=fontscale,
            color=color,
            thickness=1,
        )
        info_window = cv2.putText(
            info_window,
            str(self.MEI_Hu_moments),
            (10, 100),
            fontFace=font,
            fontScale=fontscale,
            color=color,
            thickness=1,
        )
        cv2.imshow("Hu Moments", info_window)

    def display_canvases(self):
        try:
            MHI_canvases = np.copy(self.init_canvas)
            MEI_canvases = np.copy(self.init_canvas)
            if self.MHI_canvases and self.MEI_canvases:
                MHI_canvases = np.concatenate(list(self.MHI_canvases.values()), axis=1)
                MEI_canvases = np.concatenate(list(self.MEI_canvases.values()), axis=1)
            MHI_canvases = cv2.resize(MHI_canvases, (self.w * 2, self.h * 2))
            MEI_canvases = cv2.resize(MEI_canvases, (self.w * 2, self.h * 2))
            # Not super usefule to see the MEI, so commenting out for now
            # canvases = np.concatenate([MHI_canvases, MEI_canvases], axis=0)
            canvases = MHI_canvases
            window_name = "MHI Canvas"
            if self.director.config["miror_canvas_display"]:
                canvases = cv2.flip(canvases, 1)
            cv2.imshow(window_name, canvases)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
            cv2.waitKey(1)
        except Exception as e:
            print(f"Problem rendering MHI data: {e}")

    def process_output_matrices(self):
        """
        This function computes the absolute diff between the MHI and MEI volumes
        over duration Tau.
        """
        volume_diffs = {}
        for person in self.MEI_Hu_moments.keys():
            mei_volume = np.array(self.MEI_moments_volumes[person])
            mhi_volume = np.array(self.MHI_moments_volumes[person])
            # TODO need abs?
            volume_diffs[person] = np.abs(np.subtract(mei_volume, mhi_volume))
        return volume_diffs
