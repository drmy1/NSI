from machine import Pin, Timer  # type: ignore

led = Pin("LED", Pin.OUT)
timer = Timer()  # type: ignore


def blink(timer):
    led.toggle()


timer.init(freq=2, mode=Timer.PERIODIC, callback=blink)
