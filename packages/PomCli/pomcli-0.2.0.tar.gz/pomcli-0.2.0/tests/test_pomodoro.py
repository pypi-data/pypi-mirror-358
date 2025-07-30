import logging
import time
import unittest

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
        self.assertIn("INFO:Pomodoro round 1 of 1", self.log_output)
        self.assertIn("INFO:Starting Pomodoro: 0 minutes of work.", self.log_output)
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

    def test_repetitions(self):
        timer = PomodoroTimer(work_minutes=0, break_minutes=0, repetitions=3, logger=self.logger)
        timer.start()
        rounds = [msg for msg in self.log_output if "Pomodoro round" in msg]
        self.assertEqual(len(rounds), 3)
        self.assertIn("INFO:Pomodoro round 1 of 3", rounds[0])
        self.assertIn("INFO:Pomodoro round 2 of 3", rounds[1])
        self.assertIn("INFO:Pomodoro round 3 of 3", rounds[2])
        self.assertIn("INFO:Pomodoro session complete!", self.log_output)

    def test_tqdm_usage(self):
        try:
            from tqdm import tqdm
        except ImportError:
            self.skipTest("tqdm is not installed, skipping tqdm usage test.")

        timer = PomodoroTimer(work_minutes=0.05, break_minutes=0.05, repetitions=2, use_tqdm=True, logger=self.logger)
        timer.start()
        self.assertIn("INFO:Starting Pomodoro: 0.05 minutes of work.", self.log_output)
        self.assertIn("INFO:Time for a break: 0.05 minutes.", self.log_output)
        self.assertIn("INFO:Pomodoro session complete!", self.log_output)


if __name__ == "__main__":
    unittest.main()
