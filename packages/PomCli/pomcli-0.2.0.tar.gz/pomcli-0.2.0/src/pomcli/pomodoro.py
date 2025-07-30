import logging
import time


class PomodoroTimer:
    def __init__(self, work_minutes=25, break_minutes=5, repetitions=1, logger=None, use_tqdm=False):
        """
        Initializes the Pomodoro timer.
        :param work_minutes: Work duration in minutes.
        :param break_minutes: Break duration in minutes.
        :param repetitions: Number of Pomodoro repetitions.
        :param logger: Logger instance for logging messages. If None, a default logger is created.
        :param use_tqdm: Whether to use tqdm for progress bar display.
        """
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.repetitions = repetitions
        self.is_running = False
        if logger is None:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
        self.logger = logger or logging.getLogger(__name__)

        self.use_tqdm = use_tqdm

    def start(self):
        """
        Starts the Pomodoro timer.
        """
        self.is_running = True
        for i in range(self.repetitions):
            self.logger.info(f"Pomodoro round {i + 1} of {self.repetitions}")
            self.logger.info(f"Starting Pomodoro: {self.work_minutes} minutes of work.")
            self._countdown(self.work_minutes * 60, "Work")
            if i < self.repetitions - 1:
                self.logger.info(f"Time for a break: {self.break_minutes} minutes.")
        self.logger.info("Pomodoro session complete!")
        self.is_running = False

    def _countdown(self, seconds, label):
        if self.use_tqdm:
            try:
                from tqdm import tqdm
            except ImportError:
                self.logger.warning("tqdm is not installed. Progress bar will not be shown.")
                tqdm = None
        else:
            tqdm = None
        seconds = int(seconds)
        iterator = tqdm(range(seconds), desc=f"{label} Timer",
                        ncols=70) if self.use_tqdm and 'tqdm' in locals() and tqdm else range(seconds)
        for s in iterator:
            if not self.is_running:
                break
            mins, secs = divmod(int(seconds - s - 1), 60)
            timeformat = f'{mins:02d}:{secs:02d}'
            self.logger.debug(f'{label} Timer: {timeformat}')
            time.sleep(1)

    def stop(self):
        self.is_running = False
        self.logger.info("Pomodoro stopped.")


def main():
    import argparse
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(description="Simple Pomodoro CLI Timer")
    parser.add_argument('--work', type=float, default=25, help='Work duration in minutes (default: 25)')
    parser.add_argument('--break_time', type=float, default=5, help='Break duration in minutes (default: 5)')
    parser.add_argument('--repetitions', type=int, default=1, help='Number of Pomodoro repetitions (default: 1)')
    parser.add_argument('--tqdm', action='store_true', help='Show progress bar using tqdm')
    args = parser.parse_args()
    timer = PomodoroTimer(work_minutes=args.work, break_minutes=args.break_time, repetitions=args.repetitions,
                          use_tqdm=args.tqdm)
    timer.start()


if __name__ == "__main__":
    main()
