import json


class Frame:
    def __init__(self, frame_index):
        self.index = frame_index
        self.landmarks = []
        self.init_landmarks()

    def set_landmark_params(self, landmark_index, x, y, z, visibility):
        self.landmarks[landmark_index].x = x
        self.landmarks[landmark_index].y = y
        self.landmarks[landmark_index].z = z
        self.landmarks[landmark_index].visibility = visibility

    def init_landmarks(self):
        for land in self.landmarks_desc.keys():
            self.landmarks.append(self.Landmark(land, self.landmarks_desc.get(land), set_x=None, set_y=None))

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    class Landmark:
        def __init__(self, landmark_index, set_name, set_x, set_y, set_z=0, set_visibility=0):
            self.index = landmark_index
            self.name = set_name
            self.x = set_x
            self.y = set_y
            self.z = set_z
            self.visibility = set_visibility

    landmarks_desc = {
        0: "nose",
        1: "left eye (inner)",
        2: "left eye",
        3: "left eye (outer)",
        4: "right eye (inner)",
        5: "right eye",
        6: "right eye (outer)",
        7: "left ear",
        8: "right ear",
        9: "mouth (left)",
        10: "mouth (right)",
        11: "left shoulder",
        12: "right shoulder",
        13: "left elbow",
        14: "right elbow",
        15: "left wrist",
        16: "right wrist",
        17: "left pinky",
        18: "right pinky",
        19: "left index",
        20: "right index",
        21: "left thumb",
        22: "right thumb",
        23: "left hip",
        24: "right hip",
        25: "left knee",
        26: "right knee",
        27: "left ankle",
        28: "right ankle",
        29: "left heel",
        30: "right heel",
        31: "left foot index",
        32: "right foot index",
    }

# class PersonEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Person):
#             return {"name": obj.name, "age": obj.age}
#         return super().default(obj)
