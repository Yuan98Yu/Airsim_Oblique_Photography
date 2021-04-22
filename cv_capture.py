# In settings.json first activate computer vision mode:
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode
import pprint
import argparse
import os
import json
from itertools import product

import pandas as pd
from setup_path import SetupPath
SetupPath.addAirSimModulePath()
import airsim


class ImgCapture:
    def __init__(self, cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as file:
            self.cfg = json.load(file)
        self.client = airsim.VehicleClient()
        self.client.confirmConnection()
        self.pos_list = self.generate_path(self.cfg)
        self.camera_list = ["Down", "Front", "Back", "Left", "Right"]
        self.reset()

    def reset(self):
        # currently reset() doesn't work in CV mode. Below is the workaround
        self.client.simSetVehiclePose(
            airsim.Pose(airsim.Vector3r(0, 0, 0),
                        airsim.to_quaternion(0, 0, 0)), True)
        self.log_table = pd.DataFrame(columns=('img_name', 'camera_x',
                                               'camera_y', 'camera_height'))
        # self.log_table.set_index('img_path')

    def navigate_and_catch_imgs(
            self,
            save_dir,
            pos_list,
            camera_list=["Down", "Front", "Back", "Left", "Right"]):
        os.makedirs(os.path.join(save_dir), exist_ok=False)
        self.reset()
        pass
        for idx, pos in enumerate(pos_list):
            self.catch_and_save_imgs(pos, idx, save_dir, camera_list)
        self.log_table.to_csv(os.path.join(save_dir, 'log.csv'))

    def generate_path(self, cfg, heading_step=None, side_step=None):
        target_region, height, side_overlap_rate, heading_overlap_rate = cfg[
            'target_region'], cfg['height'], cfg['side_overlap_rate'], cfg[
                'heading_overlap_rate']

        heading_length, side_length = target_region[1][0] - target_region[0][
            0], target_region[1][1] - target_region[0][1]
        # To Do
        FOV_degree = 90
        focal_length = 0.02
        frame_size = (0.02, 0.02)
        if heading_step is None:
            heading_step = self._get_step(height + 150, frame_size[0],
                                          focal_length, heading_overlap_rate)
        if side_step is None:
            side_step = self._get_step(height + 150, frame_size[1],
                                       focal_length, side_overlap_rate)
        print(f'heading_step: {heading_step}\n' f'side_step: {side_step}')

        heading_num, side_num = int(heading_length / heading_step), int(
            side_length / side_step)
        print(f'total_num: {heading_num * side_num}')
        pos_list = list()
        reverse = False
        for i in range(heading_num):
            tmp_list = list()
            for j in range(side_num):
                x, y = target_region[0][0] + i * heading_step, target_region[
                    0][1] + j * side_step
                tmp_list.append((x, y, height))
            if reverse:
                tmp_list.reverse()
            reverse = not reverse
            pos_list.extend(tmp_list)
        return pos_list

    def catch_and_save_imgs(
            self,
            pos,
            idx,
            save_dir,
            camera_list=["Down", "Front", "Back", "Left", "Right"]):
        print(f'pos {idx}: {pos}')
        self.client.simSetVehiclePose(
            airsim.Pose(airsim.Vector3r(*pos), airsim.to_quaternion(0, 0, 0)),
            True)

        # responses = self.client.simGetImages([
        #     airsim.ImageRequest("Down", airsim.ImageType.Scene),
        #     airsim.ImageRequest("Front", airsim.ImageType.Scene),
        #     airsim.ImageRequest("Back", airsim.ImageType.Scene),
        #     airsim.ImageRequest("Left", airsim.ImageType.Scene),
        #     airsim.ImageRequest("Right", airsim.ImageType.Scene)
        # ])
        responses = self.client.simGetImages([
            airsim.ImageRequest(camera_name, airsim.ImageType.Scene)
            for camera_name in camera_list
        ])

        for i, response in enumerate(responses):
            if response.pixels_as_float:
                # print("pos\n%s" % (pprint.pformat(response.camera_position)))
                airsim.write_pfm(
                    os.path.normpath(
                        os.path.join(save_dir, f'{idx}_{camera_list[i]}.pfm')),
                    airsim.get_pfm_array(response))
            else:
                # print("pos\n%s" % (pprint.pformat(response.camera_position)))
                img_name = f'{idx}_{camera_list[i]}_x{pos[0]}_y{pos[1]}.png'
                img_path = os.path.join(save_dir, img_name)
                airsim.write_file(img_path, response.image_data_uint8)
                self.log_table = self.log_table.append(
                    {
                        'img_name': img_name,
                        'camera_x': pos[0],
                        'camera_y': pos[1],
                        'camera_height': pos[2]
                    },
                    ignore_index=True)

    def _get_step(self, height, frame_length, focal_length, ovellap_ratio):
        x = frame_length * (-height) / focal_length
        step = x * (1 - ovellap_ratio)
        return step


def collect_imgs(args):
    capture = ImgCapture(cfg_path=args.cfg_path)
    capture.navigate_and_catch_imgs(args.save_dir, capture.pos_list,
                                    capture.camera_list)


def test(args):
    capture = ImgCapture(cfg_path=args.cfg_path)
    # region, height = capture.cfg['target_region'], capture.cfg['height']
    # path = list(map(lambda pos: (*pos, height), region))
    path = capture.generate_path(capture.cfg, heading_step=500, side_step=500)
    print(path)
    # capture.navigate_and_catch_imgs(args.save_dir, path, capture.camera_list)
    camera_list = ['Down']
    capture.navigate_and_catch_imgs(args.save_dir, path, camera_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', '-t', action='store_true')
    parser.add_argument('--cfg_path', '-c', type=str, default='./cfg.json')
    parser.add_argument('--save_dir', '-s', type=str, default='./imgs')
    args = parser.parse_args()
    if args.test:
        test(args)
    else:
        collect_imgs(args)
