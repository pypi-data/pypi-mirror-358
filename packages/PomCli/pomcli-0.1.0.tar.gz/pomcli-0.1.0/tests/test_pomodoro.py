import unittest
import time
import logging
from pomcli.pomodoro import PomodoroTimer

class TestPomodoroTimer(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("pomodoro_test")
        self.logger.setLevel(logging.DEBUG)
        self.log_output = []
        handler = logging.StreamHandler(self._LogCapture(self.log_output))
        handler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
        self.logger.handlers = [handler]

    class _LogCapture:
        def __init__(self, output_list):
            self.output_list = output_list
        def write(self, msg):
            if msg.strip():
                self.output_list.append(msg.strip())
        def flush(self):
            pass

    def test_start_and_stop(self):
        timer = PomodoroTimer(work_minutes=0, break_minutes=0, logger=self.logger)
        timer.start()
        self.assertIn("INFO:Starting Pomodoro: 0 minutes of work.", self.log_output)
        self.assertIn("INFO:Time for a break: 0 minutes.", self.log_output)
        self.assertIn("INFO:Pomodoro session complete!", self.log_output)
        timer.stop()
        self.assertIn("INFO:Pomodoro stopped.", self.log_output)

    def test_stop_midway(self):
        timer = PomodoroTimer(work_minutes=0.001, break_minutes=0, logger=self.logger)
        import threading
        t = threading.Thread(target=timer.start)
        t.start()
        time.sleep(0.5)
        timer.stop()
        t.join()
        self.assertIn("INFO:Pomodoro stopped.", self.log_output)

if __name__ == "__main__":
    unittest.main()

