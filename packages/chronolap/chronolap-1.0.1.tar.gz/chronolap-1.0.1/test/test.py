from chronolap import ChronolapTimer
import time

def test_lap_count():
    timer = ChronolapTimer()
    timer.start()
    time.sleep(0.05)
    timer.lap("Lap 1")
    time.sleep(0.05)
    timer.lap("Lap 2")
    timer.stop()
    assert len(timer.laps) == 2