from pomcli.pomodoro import PomodoroTimer

if __name__ == "__main__":
    PomodoroTimer(work_minutes=0.1, break_minutes=0.05, repetitions=2, use_tqdm=True).start()  # Short times for demo
