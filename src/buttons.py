from hardware_rev import HardwareRev
from machine import Pin, Timer # type: ignore
import time # type: ignore
from pca9535 import PCA9535


LONG_CLICK_DURATION_MS = 1000
def no_callback(button: int):
    print(f'Button {button} pressed')

class Buttons():
    gpio_button_pins: list[int]
    gpio_buttons: list[Pin]
    last_press_times: list[int]
    last_release_times: list[int]
    last_long_press_time: list[int]
    button_state: int
    debounce_time: int

    def __init__(self, hardware_rev, iox: PCA9535):
        if hardware_rev == HardwareRev.V1:
            self.gpio_button_pins = [0, 33, 35, 34]
        else:
            self.gpio_button_pins = [0]
        self.gpio_buttons = []
        self.debounce_time = 20
        self.button_pressed_callbacks = []

        # We will self-register the reset_button_long_press function 
        # so that we can reset the long press timer when the button is released
        self.button_released_callbacks = [self.reset_button_long_press]
        self.button_long_press_callbacks = []
        self.last_iox_state = 0
        self.iox = iox

        for index, pin in enumerate(self.gpio_button_pins):
            self.gpio_buttons.append(Pin(pin, Pin.IN))
            self.gpio_buttons[index].irq(handler=self.irq_falling, trigger=Pin.IRQ_FALLING)
            # TODO apparently doing multiple IRQs does not work for a single pin
            # https://www.reddit.com/r/esp32/comments/ia9bsa/esp32_micropython_pin_interrupts_for_both_rising/
            # self.gpio_buttons[index].irq(handler=self.button_released_handler, trigger=Pin.IRQ_RISING)

        print(f"Registered {len(self.gpio_buttons)} buttons")

        # V1 hardware uses all GPIO buttons
        if hardware_rev == HardwareRev.V2:
            timer = Timer(3)
            timer.init(mode=Timer.PERIODIC, period=50, callback=self.poll_buttons)
            self.iox_button_map = [
                1 << 10, # 0000 0100 0000 0000
                1 << 9,  # 0000 0010 0000 0000
                1 << 8,  # 0000 0001 0000 0000
                1 << 1,  # 0000 0000 0000 0010
                1 << 2,  # 0000 0000 0000 0100
            ]

        elif hardware_rev == HardwareRev.V3:
            # TODO add interrupt handler for pca9535
            pass
            
        
        total_buttons = len(self.gpio_buttons) + len(self.iox_button_map)
        self.last_press_times = [0 for _ in range(total_buttons)]
        self.last_release_times = [0 for _ in range(total_buttons)]
        self.last_long_press_time = [0 for _ in range(total_buttons)]


    def reset_button_long_press(self, button: int):
        print(f"Resetting long press for button {button}")
        self.last_press_times[button] = 0
        self.last_long_press_time[button] = 0


    # This is a wrapper that polls the button inputs
    def poll_buttons(self, timer):
        inputs = self.iox.read_all_pca9535_inputs()
        self.iox_button_handler(inputs)

        now = time.ticks_ms() # type: ignore
        for button_index,button_pressed in enumerate(self.last_press_times):
            # We don't support long press for the GPIO buttons
            if button_index == 0:
                continue

            # if the button doesn't have a last_press_time, then it isn't pressed
            # and we won't worry about this
            if not button_pressed:
                continue
            
            # Check if the long press has already fired
            if self.last_long_press_time[button_index]:
                continue

            
            time_since_pressed = time.ticks_diff(now, button_pressed) # type: ignore
            if time_since_pressed > LONG_CLICK_DURATION_MS:
                print(f"Long click detected for {button_index} after {time_since_pressed} ms")
                self.last_long_press_time[button_index] = now
                [callback(button_index) for callback in self.button_long_press_callbacks]
                
        
    # This handler can be refactored to be used either as fired by the interrupt
    # or by the polling function
    def iox_button_handler(self, inputs):
        pins_changed = inputs ^ self.last_iox_state
        if pins_changed:
            # TODO probably not super performance using the keys() method...
            for button_index,button_mask in enumerate(self.iox_button_map):
                button_index += len(self.gpio_buttons)
                if not pins_changed & button_mask:
                    continue
                
                button_state = not inputs & button_mask

                # Removing for performance reasons for now
                if button_index is None:
                    continue

                if button_state:
                    self.button_debounce_processor(button_index, self.last_press_times, self.button_pressed_callbacks)
                else:
                    # We can
                    # last_press_time = self.last_press_times.get(button_index, 0)
                    # press_duration = time.ticks_diff(time.ticks_ms(), last_press_time) # type: ignore
                    # print(f"You held the button down for {press_duration} ms")
                    self.button_debounce_processor(button_index, self.last_release_times, self.button_released_callbacks)
            self.last_iox_state = inputs


    def irq_rising(self, pin):
        print(f"Button released {pin}")
        button_index = self.gpio_buttons.index(pin)
        self.button_debounce_processor(button_index, self.last_release_times, self.button_released_callbacks)


    def irq_falling(self, pin):
        print(f"Button pressed {pin}")
        button_index = self.gpio_buttons.index(pin)
        self.button_debounce_processor(button_index, self.last_press_times, self.button_pressed_callbacks)


    def button_debounce_processor(self, button_index: int, times: list[int], callbacks):
        button = button_index
        last_release_signal = times[button_index]
        time_now = time.ticks_ms() # debounce  # type: ignore
        if last_release_signal+self.debounce_time >= time_now:
            return
        [callback(button) for callback in callbacks]
        times[button_index] = time_now

