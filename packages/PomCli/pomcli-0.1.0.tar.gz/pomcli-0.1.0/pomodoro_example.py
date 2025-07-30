from pomcli.pomodoro import PomodoroTimer

if __name__ == "__main__":
    timer = PomodoroTimer(work_minutes=0.1, break_minutes=0.05)  # Short times for demo
    timer.start()
