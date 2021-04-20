# In settings.json first activate computer vision mode:
# https://github.com/Microsoft/AirSim/blob/master/docs/image_apis.md#computer-vision-mode
from setup_path import SetupPath
SetupPath.addAirSimModulePath()
import airsim


client = airsim.VehicleClient()
client.confirmConnection()

pose = client.simGetVehiclePose()
print("x={}, y={}, z={}".format(pose.position.x_val, pose.position.y_val,
                                pose.position.z_val))

angles = airsim.to_eularian_angles(client.simGetVehiclePose().orientation)
print("pitch={}, roll={}, yaw={}".format(angles[0], angles[1], angles[2]))

for i in range(5):
    print(f'camera {i}'.center(100, '='))
    camera_info = client.simGetCameraInfo(str(i))
    print(f'pose: {camera_info.pose}')
    print(f'fov: {camera_info.fov}')
    print(f'{camera_info.proj_mat}')
pose.position.x_val = pose.position.x_val + 1
client.simSetVehiclePose(pose, True)
