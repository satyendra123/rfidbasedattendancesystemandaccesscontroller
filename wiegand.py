# i have made my own library file for wiegand protocol for esp32 micropython code. this wiegand protocol is used to read the access controller data using my esp32 or arduino microcontroller. i am using my esp32 micropython code to read the wiegand data
# i am using access controller based rfid card data and read the proximity card through it. it has VCC(Red), gnd(Black), D0(Green), D1(White), led(Blue), buzzer pin(Yellow). isme maine D0 ko pin 17 se aur D1 ko pin 16 se connect kiya hai esp32 ke sath
# Step-1 wiegand.py
from machine import Pin, Timer
import utime

CARD_MASK = 0b11111111111111110  # 16 ones
FACILITY_MASK = 0b1111111100000000000000000  # 8 ones

class Wiegand:
    def __init__(self, pin0, pin1, callback, timer_id=-1):
        """
        pin0 - the GPIO that goes high when a zero is sent by the reader
        pin1 - the GPIO that goes high when a one is sent by the reader
        timer_id - the Timer ID to use for periodic callbacks
        callback - the function called (with three args: card ID, facility code, and card count)
                   when a card is detected. Note that Micropython interrupt
                   implementation limitations apply to the callback!
        """
        self.pin0 = Pin(pin0, Pin.IN)
        self.pin1 = Pin(pin1, Pin.IN)
        self.callback = callback
        self.last_card = None
        self.next_card = 0
        self._bits = 0
        self.pin0.irq(trigger=Pin.IRQ_FALLING, handler=self._on_pin0)
        self.pin1.irq(trigger=Pin.IRQ_FALLING, handler=self._on_pin1)
        self.last_bit_read = None
        self.timer = Timer(timer_id)
        self.timer.init(period=50, mode=Timer.PERIODIC, callback=self._cardcheck)
        self.cards_read = 0

    def _on_pin0(self, newstate): 
        self._on_pin(0, newstate)

    def _on_pin1(self, newstate): 
        self._on_pin(1, newstate)

    def _on_pin(self, is_one, newstate):
        now = utime.ticks_ms()
        if self.last_bit_read is not None and now - self.last_bit_read < 2:
            # too fast
            return

        self.last_bit_read = now
        self.next_card <<= 1
        if is_one: 
            self.next_card |= 1
        self._bits += 1

    def get_card(self):
        if self.last_card is None:
            return None
        return ( self.last_card & CARD_MASK ) >> 1

    def get_facility_code(self):
        if self.last_card is None:
            return None
        # Specific to standard 26bit Wiegand
        return ( self.last_card & FACILITY_MASK ) >> 17

    def _cardcheck(self, t):
        if self.last_bit_read is None: 
            return
        now = utime.ticks_ms()
        if now - self.last_bit_read > 50:
            # too slow - new start!
            self.last_bit_read = None
            self.last_card = self.next_card
            self.next_card = 0
            self._bits = 0
            self.cards_read += 1
            self.callback(self.get_card(), self.get_facility_code(), self.cards_read)

#Step-2 main.py file
from machine import Pin
from wiegand import Wiegand

# Example callback function
def card_callback(card_id, facility_code, card_count):
    print("Card ID:", card_id)
    print("Facility Code:", facility_code)
    print("Card Count:", card_count)
    print()  # Add a newline for separation

# Initialize Wiegand instance with GPIO pins 16 and 17
wiegand_reader = Wiegand(pin0=16, pin1=17, callback=card_callback)

# output data
>>> %Run -c $EDITOR_CONTENT

MPY: soft reboot
>>> Card ID: 26182
Facility Code: 111
Card Count: 1

Card ID: 6164
Facility Code: 110
Card Count: 2

Card ID: 6164
Facility Code: 110
Card Count: 3

Card ID: 6164
Facility Code: 110
Card Count: 4

Card ID: 6164
Facility Code: 110
Card Count: 5

Card ID: 6164
Facility Code: 110
Card Count: 6

Card ID: 6164
Facility Code: 110
Card Count: 7

Card ID: 6164
Facility Code: 110
Card Count: 8

Card ID: 6164
Facility Code: 110
Card Count: 9

Card ID: 26182
Facility Code: 111
Card Count: 10
