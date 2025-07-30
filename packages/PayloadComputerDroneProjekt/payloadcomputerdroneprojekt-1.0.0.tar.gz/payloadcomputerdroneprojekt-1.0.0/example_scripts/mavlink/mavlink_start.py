# takeoff.py
import argparse
from pymavlink import mavutil


def takeoff(mav_connection, takeoff_altitude: float,
            tgt_sys_id: int = 1, tgt_comp_id=1):

    print("Heartbeat from system (system %u component %u)" %
          (mav_connection.target_system, mav_connection.target_component))

    print("Connected to PX4 autopilot")
    print(mav_connection.mode_mapping())
    mode_id = mav_connection.mode_mapping()["TAKEOFF"]
    print(mode_id)
    msg = mav_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    starting_alt = msg.alt / 1000
    takeoff_params = [0, 0, 0, 0, float("NAN"), float(
        "NAN"), starting_alt + takeoff_altitude]

    # Change mode to guided (Ardupilot) or takeoff (PX4)
    mav_connection.mav.command_long_send(
        tgt_sys_id, tgt_comp_id, mavutil.mavlink.MAV_CMD_DO_SET_MODE,
        0, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id, 0, 0, 0, 0, 0)

    ack_msg = mav_connection.recv_match(
        type='COMMAND_ACK', blocking=True, timeout=3)
    print(f"Change Mode ACK:  {ack_msg}")

    # Arm the UAS
    mav_connection.mav.command_long_send(
        tgt_sys_id, tgt_comp_id,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

    arm_msg = mav_connection.recv_match(
        type='COMMAND_ACK', blocking=True, timeout=3)
    print(f"Arm ACK:  {arm_msg}")

    # Command Takeoff
    mav_connection.mav.command_long_send(
        tgt_sys_id, tgt_comp_id,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, takeoff_params[0],
        takeoff_params[1], takeoff_params[2], takeoff_params[3],
        takeoff_params[4], takeoff_params[5], takeoff_params[6])

    takeoff_msg = mav_connection.recv_match(
        type='COMMAND_ACK', blocking=True, timeout=3)
    print(f"Takeoff ACK:  {takeoff_msg}")

    return takeoff_msg.result


def main():
    parser = argparse.ArgumentParser(
        description="A simple script to command a UAV to takeoff.")
    parser.add_argument("--altitude", type=int,
                        help="Altitude for the UAV to reach upon takeoff.",
                        default=10)

    args = parser.parse_args()
    mav_connection = mavutil.mavlink_connection('udpin:localhost:14445')
    takeoff(mav_connection, args.altitude)


if __name__ == "__main__":
    main()
