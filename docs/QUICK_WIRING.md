# Quick Wiring Guide

## Components Required
- Raspberry Pi (3B+ or newer)
- Waveshare SIM7600E-H 4G HAT
- Active SIM card
- NC (Normally Closed) photocell circuits
- 10kΩ pull-up resistors (optional, internal pull-up can be used)
- Female to Male jumper wires (at least 6)
- Power supply (5V, 3A recommended)
- Antenna for LTE HAT

## Detailed Connection Diagram

### Complete System Overview
```
                           [Antenna]
                              ║
┌──────────────────┐    ┌────╨─────────┐
│   Raspberry Pi   │    │   LTE HAT    │
│                  │    │              │
│  [GPIO HEADER]   │    │ [GPIO PINS]  │
│   ║ ║ ║ ║ ║ ║   │    │  ║ ║ ║ ║ ║   │
└───╨─╨─╨─╨─╨─╨───┘    └──╨─╨─╨─╨─╨───┘
     │ │ │ │ │            │ │ │ │ │
     └─┤ ├─┤ ├────────────┤ ├─┤ ├─┘
       └─┘ └─┘            └─┘ └─┘
    [Jumper Wires]    [Photocell Circuits]
```

### GPIO Header Pin Mapping
```
Raspberry Pi                    LTE HAT
┌─────────┬─────┐          ┌─────────┬─────┐
│  3V3  1 │ 2 5V│          │  3V3  1 │ 2 5V│◄────┐
│  SDA  3 │ 4 5V│          │  SDA  3 │ 4 5V│     │
│  SCL  5 │ 6 GN│◄────┐    │  SCL  5 │ 6 GN│◄────┤
│  GP4  7 │ 8 TX│◄─┐  │    │  GP4  7 │ 8 TX│     │
│  GND  9 │10 RX│◄─┼──┼────│  GND  9 │10 RX│◄────┤
│ GP17 11 │12 18│  │  │    │ PWR  11 │12 18│     │
│ GP27 13 │14 GN│  │  │    │ STA  13 │14 GN│     │
└─────────┴─────┘  │  │    └─────────┴─────┘     │
                   │  │                           │
Essential:         │  └───────── GND ────────────┘
TX->RX ───────────┘          5V ────────────────┘
```

### Detailed Power and Serial Connections
```
   Raspberry Pi                LTE HAT
      Pin 2 (5V) ──────────► Pin 2 (5V)
      Pin 6 (GND) ─────────► Pin 6 (GND)
      Pin 8 (TX) ──────────► Pin 10 (RX)    [CRITICAL: Cross TX/RX]
      Pin 10 (RX) ─────────► Pin 8 (TX)     [CRITICAL: Cross TX/RX]
      Pin 11 (GPIO17) ─────► Pin 11 (PWR_KEY)
      Pin 13 (GPIO27) ─────► Pin 13 (STATUS)
```

### Photocell Circuit Detail
```
Photocell Terminal Layout:
┌─────────────────────────────────────────────────┐
│                                                 │
│    ┌─────────── Photocell ──────────┐          │
│    │                                │          │
│    │   Power         Relay Contacts │          │
│    │  +    -         NO   C    NC  │          │
│    │  │    │         │    │    │   │          │
│    └──┼────┼─────────┼────┼────┼───┘          │
│       │    │                │    │             │
│       │    │                │    │             │
│    12V│   GND              │    │             │
│ Power │                    │    │             │
│ Supply│                    │    │             │
│       │                    │    │             │
└───────┴────────────────────┴────┴─────────────┘

Circuit 1 (Main Entrance):

Power Section:
   12V Power Supply
        │
    ┌───┴───┐
    │       │
    ▼       ▼
   (+)     (-)
Photocell  GND

Signal Section (Voltage Free Contacts):
   3.3V (Pi Pin 1)
        │
        ▼
   ┌───[10kΩ]
   │
   │
   │            ┌────────┐
   └────────────┤   C    │
                │        │ Photocell
                │   NC   │
                └────┬───┘
                     │
                     │
                     ▼
                  GPIO23 (Pin 16)

Circuit 2 (Exit Gate):

Power Section:
   12V Power Supply
        │
    ┌───┴───┐
    │       │
    ▼       ▼
   (+)     (-)
Photocell  GND

Signal Section (Voltage Free Contacts):
   3.3V (Pi Pin 1)
        │
        ▼
   ┌───[10kΩ]
   │
   │
   │            ┌────────┐
   └────────────┤   C    │
                │        │ Photocell
                │   NC   │
                └────┬───┘
                     │
                     │
                     ▼
                  GPIO24 (Pin 18)

Connection Summary:
┌────────────────────────────────────────────────────┐
│ 1. Power Connections (Each Photocell):            │
│    • (+) terminal → 12V power supply positive     │
│    • (-) terminal → Power supply ground           │
│                                                   │
│ 2. Signal Connections (Each Photocell):           │
│    • C terminal  → 3.3V via 10kΩ resistor        │
│    • NC terminal → GPIO pin                       │
│    • NO terminal → Not used                       │
└────────────────────────────────────────────────────┘

Operating Logic:
┌────────────────────────────────────────────────────┐
│ Normal State (Beam Aligned):                       │
│ • Internal relay energized                         │
│ • C and NC contacts connected                      │
│ • 3.3V reaches GPIO through NC contact            │
│ • GPIO reads HIGH                                  │
│                                                   │
│ Alarm State (Beam Broken):                        │
│ • Internal relay de-energized                     │
│ • C and NC contacts separated                     │
│ • GPIO pulled to ground                           │
│ • GPIO reads LOW                                  │
└────────────────────────────────────────────────────┘

Important Notes:
┌────────────────────────────────────────────────────┐
│ • Power and signal circuits are fully isolated     │
│ • Use C and NC terminals for fail-safe operation   │
│ • NO terminal is not used in this application     │
│ • Multiple photocells can share the same          │
│   12V power supply                                │
└────────────────────────────────────────────────────┘

### Step-by-Step Wiring Instructions

1. Power Circuit Connections
```
For each photocell:
1. Connect the (+) terminal to 12V DC power supply positive
2. Connect the (-) terminal to power supply ground (GND)
3. Verify the power LED on the photocell illuminates
```

2. Signal Circuit Connections
```
For Main Entrance (Circuit 1):
1. Connect photocell C (Common) terminal to:
   - Raspberry Pi 3.3V (Pin 1)
   - Through a 10kΩ pull-up resistor

2. Connect photocell NC (Normally Closed) terminal to:
   - Raspberry Pi GPIO23 (Pin 16)

For Exit Gate (Circuit 2):
1. Connect photocell C (Common) terminal to:
   - Raspberry Pi 3.3V (Pin 1)
   - Through a 10kΩ pull-up resistor

2. Connect photocell NC (Normally Closed) terminal to:
   - Raspberry Pi GPIO24 (Pin 18)

Note: The NO (Normally Open) terminal is not used
```

3. Ground Connections
```
1. Connect all GPIO ground connections to:
   - Raspberry Pi GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
2. Keep power supply ground separate from GPIO ground
```

### Why These Connections?

1. Power Circuit (12V)
```
Purpose: Powers the photocell's internal components
- (+) terminal needs 12V DC for reliable operation
- (-) terminal completes the power circuit
- Isolated from signal circuit for safety
```

2. Signal Circuit (3.3V)
```
Purpose: Provides fail-safe beam break detection
- C terminal gets 3.3V through pull-up resistor because:
  * Creates a reliable reference voltage
  * Pull-up resistor limits current for safety
  * 3.3V is Raspberry Pi's logic level

- NC terminal connects to GPIO because:
  * Normally Closed = closed when beam aligned
  * Opens when beam broken (fail-safe)
  * Direct connection to GPIO for instant detection

- Pull-up resistor (10kΩ):
  * Limits current to safe levels (~0.33mA)
  * Provides clean signal transition
  * Standard value for Raspberry Pi GPIO
```

3. Safety Features
```
This wiring creates a fail-safe system:
1. Beam break → NC contact opens → GPIO reads LOW
2. Power loss → NC contact opens → GPIO reads LOW
3. Wire break → Circuit opens → GPIO reads LOW
4. All failure modes trigger an alarm condition
```

### Common Issues and Solutions
```
1. No power LED on photocell:
   - Check 12V power supply connections
   - Verify power supply is outputting 12V
   - Check for reversed polarity

2. Always reading beam break:
   - Verify 3.3V at C terminal through pull-up
   - Check NC terminal connection to GPIO
   - Confirm beam alignment

3. Not detecting beam breaks:
   - Check GPIO pin number in software
   - Verify pull-up resistor connection
   - Test NC contact operation
```

### Testing Procedure
```
1. Power Test:
   - Measure 12V DC across photocell + and - terminals
   - Verify power LED is lit

2. Signal Test:
   With beam aligned:
   - Measure 3.3V at GPIO pin
   - Verify software reads HIGH

   With beam blocked:
   - Measure 0V at GPIO pin
   - Verify software reads LOW

3. Continuity Test:
   With beam aligned:
   - Check continuity between C and NC (should be connected)
   
   With beam blocked:
   - Check continuity between C and NC (should be open)
```

### LTE HAT Layout
```
┌────────────────────────────────┐
│    ┌──────┐      ┌──────┐     │
│    │ MAIN │      │ GNSS │     │
│    │ ANT  │      │ ANT  │     │
│    └──┬───┘      └──┬───┘     │
│       │             │         │
│   ┌───────────────────────┐   │
│   │     SIM7600E-H       │   │
│   │                      │   │
│   └───────────────────────┘   │
│      ▲   ▲   ▲   ▲   ▲       │
│     [GPIO HEADER PINS]        │
└────────────────────────────────┘
      PWR NET STA RX  TX
```

### LED Indicators Location
```
┌────────────────────┐
│    LTE HAT        │
│  ┌──┐ ┌──┐ ┌──┐   │
│  │~~│ │~~│ │~~│   │
│  └──┘ └──┘ └──┘   │
│  PWR  NET  STA    │
└────────────────────┘

LED States:
PWR: [■] Solid = On
NET: [~] Blinking = Searching
     [■] Solid = Connected
STA: [~] Blinking = Active
```

### Wiring Sequence
```
1. ┌────────────┐
   │ Power OFF  │
   └────────────┘

2. ┌────────────┐    ┌─────────────┐
   │Connect GND │ ──►│Connect 5V   │
   └────────────┘    └─────────────┘

3. ┌────────────┐    ┌─────────────┐
   │Cross TX/RX │ ──►│Power Control│
   └────────────┘    └─────────────┘

4. ┌────────────┐    ┌─────────────┐
   │Add Antenna │ ──►│Insert SIM   │
   └────────────┘    └─────────────┘

5. ┌────────────┐
   │ Power ON   │
   └────────────┘
```

## Critical Checks Before Power-Up
```
✓ GND connected first
✓ TX/RX properly crossed
✓ 5V connected last
✓ Antenna attached
✓ SIM card inserted
✓ No shorts between pins
```

## Troubleshooting Points
```
No Power:
[5V Pin] ──► Check voltage
[GND Pin] ──► Check continuity

No Communication:
[TX/RX] ──► Verify crossed
[Serial] ──► Check baud rate

No Network:
[Antenna] ──► Check connection
[SIM] ──► Check insertion
```

## Safety Checkpoints
```
[×] Never connect/disconnect while powered
[×] Never leave pins uninsulated
[×] Never force connectors
[×] Never run without antenna
[✓] Always connect GND first
[✓] Always power up last
[✓] Always verify connections twice
```

## LTE HAT Pin Connections

### Essential Connections (Minimum Required)
```
RPi GPIO Pin    ->   LTE HAT Pin
     2 (5V)     ->   2 (5V)
     6 (GND)    ->   6 (GND)
     8 (TX)     ->   10 (RX)
    10 (RX)     ->   8 (TX)
```

### Power Control Connections (Optional)
```
RPi GPIO Pin    ->   LTE HAT Pin
    11 (GPIO17) ->   11 (PWR_KEY)
    13 (GPIO27) ->   13 (STATUS)
```

### SPI Connections (If Using)
```
RPi GPIO Pin    ->   LTE HAT Pin
    19 (MOSI)   ->   19 (MOSI)
    21 (MISO)   ->   21 (MISO)
    23 (SCLK)   ->   23 (SCLK)
    24 (CE0)    ->   24 (CE0)
```

## Antenna Connections
```
[Main Antenna]    [GPS Antenna]
      ▼                ▼
   ┌──────────────────────┐
   │     LTE HAT         │
   └──────────────────────┘
```
- Screw the main antenna into the 'MAIN' port
- Screw the GPS antenna into the 'GNSS' port (if using GPS)

## Photocell Circuit Wiring

1. **Circuit 1 (Main Entrance)**
   ```
   [Photocell 1] ----+---- [GPIO 23 (Pin 16)]
                     |
                    [10kΩ]
                     |
                     |
                     |
                     ▼
                  GPIO23 (Pin 16)
   ```

2. **Circuit 2 (Exit Gate)**
   ```
   [Photocell 2] ----+---- [GPIO 24 (Pin 18)]
                     |
                    [10kΩ]───┐
                     |       |
                     |       └────────► C
                     |                 Photocell
                     |                   NC ────────┐
                     |                             ▼
                     |                        GPIO24 (Pin 18)
                     |                             │
                     └──────────────────────────────┘
                                               │
                                              GND
   ```

## Pin Layout Reference
```
Raspberry Pi GPIO Header
┌───────────────────────┐
│ 3V3  (1)  (2) 5V     │
│ SDA  (3)  (4) 5V     │
│ SCL  (5)  (6) GND    │
│ GP4  (7)  (8) TX     │
│ GND  (9) (10) RX     │
│ GP17(11) (12) GP18   │
│ GP27(13) (14) GND    │
│ GP22(15) (16) GP23   │
│ 3V3 (17) (18) GP24   │
│ MOSI(19) (20) GND    │
│ MISO(21) (22) GP25   │
│ SCLK(23) (24) CE0    │
│ GND (25) (26) CE1    │
└───────────────────────┘
```

## Power Connections

1. **Power Supply Requirements**
   - Use 5V, 3A power supply for Raspberry Pi
   - LTE HAT powered through GPIO 5V pin

2. **Power-up Sequence**
   ```
   1. Connect all wires
   2. Connect antennas
   3. Insert SIM card
   4. Power up Raspberry Pi
   ```

## Quick Test

1. **Check LTE Connection**
   ```bash
   # Check signal strength
   python3 test_lte.py
   ```

2. **Test Circuits**
   ```bash
   # Verify circuit connections
   python3 test_circuits.py
   ```

## LED Status Guide
```
LTE HAT LEDs:
PWR: Power status
NET: Network status
STA: System status

Normal Operation:
PWR: Solid ON
NET: Blinking = Searching
     Solid = Connected
STA: Blinking = Normal
```

## Troubleshooting

1. **No LTE Connection**
   - Check TX/RX wire connections
   - Verify they're not swapped
   - Check antenna connections
   - Verify SIM is properly inserted

2. **Circuit Issues**
   - Check GPIO pin numbers
   - Verify 3.3V and GND connections
   - Test pull-up resistors
   - Check photocell continuity

3. **Power Issues**
   - Verify 5V connection
   - Check GND connection
   - Monitor power LED status

## Safety Notes
- Double-check all connections before power-up
- Don't connect/disconnect while powered
- Keep antennas away from metal objects
- Ensure proper ventilation
