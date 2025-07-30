import time
import logging

class PomodoroTimer:
    def __init__(self, work_minutes=25, break_minutes=5, logger=None):
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.is_running = False
        self.logger = logger or logging.getLogger(__name__)

    def start(self):
        self.is_running = True
        self.logger.info(f"Starting Pomodoro: {self.work_minutes} minutes of work.")
        self._countdown(self.work_minutes * 60, "Work")
        self.logger.info(f"Time for a break: {self.break_minutes} minutes.")
        self._countdown(self.break_minutes * 60, "Break")
        self.logger.info("Pomodoro session complete!")
        self.is_running = False

    def _countdown(self, seconds, label):
        while seconds > 0 and self.is_running:
            mins, secs = divmod(int(seconds), 60)
            timeformat = f'{mins:02d}:{secs:02d}'
            self.logger.debug(f'{label} Timer: {timeformat}')
            time.sleep(1)
            seconds -= 1

    def stop(self):
        self.is_running = False
        self.logger.info("Pomodoro stopped.")

def main():
    import argparse
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(description="Simple Pomodoro CLI Timer")
    parser.add_argument('--work', type=float, default=25, help='Work duration in minutes (default: 25)')
    parser.add_argument('--break_time', type=float, default=5, help='Break duration in minutes (default: 5)')
    args = parser.parse_args()
    timer = PomodoroTimer(work_minutes=args.work, break_minutes=args.break_time)
    timer.start()

if __name__ == "__main__":
    main()
