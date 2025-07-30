import json

from primus_safe_pulsekit import HardwareInfo


def test_get_hardware_info():
    hw = HardwareInfo()
    hw.load()
    print(hw.model_dump_json())

if __name__ == '__main__':
    test_get_hardware_info()