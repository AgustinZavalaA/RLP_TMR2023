import platform
import unittest

from RLP_TMR2023.hardware_controllers.motors_controller import motors_controller_factory


class TestHardwareController(unittest.TestCase):
    def test_singleton_functionality(self):
        # TODO: add test for other controllers
        if platform.machine() not in ['x86_64', 'aarch64']:
            self.skipTest("This test is only for x86_64 and aarch64")

        m1 = motors_controller_factory(platform.machine())
        m2 = motors_controller_factory(platform.machine())

        self.assertEqual(m1, m2)
        self.assertEqual(id(m1), id(m2))

    def test_motors_controller_mock(self):
        if platform.machine() not in ['x86_64', 'aarch64']:
            self.skipTest("This test is only for x86_64 and aarch64")

        m = motors_controller_factory("x86_64")
        self.assertEqual(m.__class__.__name__, 'MotorsControllerMock')

    def test_motors_controller_raspberry(self):
        if platform.machine() not in ['x86_64', 'aarch64']:
            self.skipTest("This test is only for x86_64 and aarch64")

        m = motors_controller_factory("aarch64")
        self.assertEqual(m.__class__.__name__, 'MotorsControllerRaspberry')

    # TODO: add test for other controllers


if __name__ == '__main__':
    unittest.main()
