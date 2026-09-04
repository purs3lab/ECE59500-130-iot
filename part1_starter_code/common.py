import machine

# Feel free to change the name and type of storage as needed
PIN_STORE = "pin_store.json"

characters = [
    ["1","2","3","A"],
    ["4","5","6","B"],
    ["7","8","9","C"],
    ["*","0","#","D"]
]

# Update based on your wiring
row_pins = [6, 7, 8, 9]
# Update based on your wiring
col_pins = [10, 11, 12, 13]

rows = [machine.Pin(p, machine.Pin.OUT) for p in row_pins]
# Internal pull-down - no external resistor needed on the column lines
cols = [machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_DOWN) for p in col_pins]

# Initialize all row pins to low
for r in rows:
    r.value(0)

# Read the current key pressed on the keypad
def read_key():
    for i, r in enumerate(rows):
        r.value(1)
        for j, c in enumerate(cols):
            if c.value() == 1:
                r.value(0)
                return characters[i][j]
        r.value(0)
    return None