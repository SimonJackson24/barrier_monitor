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
Circuit 1 (Main Entrance):

     3.3V (Pin 1)
          │
          ▼
    ┌────[10kΩ]────┐
    │              │
    │              ▼
    │         GPIO17 (Pin 11)
    │              │
    └──► [Photocell] ──► GND
         (NC Contact)

Circuit 2 (Exit Gate):

     3.3V (Pin 1)
          │
          ▼
    ┌────[10kΩ]────┐
    │              │
    │              ▼
    │         GPIO27 (Pin 13)
    │              │
    └──► [Photocell] ──► GND
         (NC Contact)
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
   [Photocell 1] ----+---- [GPIO 17 (Pin 11)]
                     |
                    [10kΩ]
                     |
                    [3.3V (Pin 1)]
   ```

2. **Circuit 2 (Exit Gate)**
   ```
   [Photocell 2] ----+---- [GPIO 27 (Pin 13)]
                     |
                    [10kΩ]
                     |
                    [3.3V (Pin 1)]
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
