# Barrier Monitor System Wiring Guide

> 🚀 **Need it fast?** Check out our [Quick-Start Guide](QUICK_WIRING.md) for a 5-minute installation.

## Safety Precautions
⚠️ **IMPORTANT: Always disconnect power before making any connections**
- Ensure Raspberry Pi is powered off
- Wear anti-static protection when handling components
- Double-check all connections before powering on
- Follow proper electrical safety procedures

## LTE Mini HAT Installation

### Step 1: HAT Physical Installation
1. Align the Clipper LTE mini HAT with Raspberry Pi GPIO header
2. Ensure pin 1 (3.3V) aligns with HAT's pin 1 marker
3. Gently press HAT onto GPIO pins until fully seated
4. Secure HAT with provided mounting hardware

### Step 2: GPIO Connections
```
Clipper LTE Mini HAT    Raspberry Pi GPIO
Pin 1  (3.3V)     ->    Pin 1  (3.3V)
Pin 6  (GND)      ->    Pin 6  (GND)
Pin 8  (TX)       ->    Pin 10 (GPIO15/RX)
Pin 10 (RX)       ->    Pin 8  (GPIO14/TX)
```

### Step 3: Antenna Connection
1. Locate SMA connector on HAT
2. Attach provided antenna by screwing clockwise
3. Position antenna vertically for best reception
4. Keep antenna away from metal objects

### Step 4: SIM Card Installation
1. Locate SIM card holder on HAT
2. Insert SIM card with contacts facing down
3. Ensure correct orientation (notched corner aligned)
4. Gently push until it clicks into place

## Barrier Circuit Connections

### Main Components
- NC (Normally Closed) photocell circuits
- Pull-up resistors (10kΩ)
- Terminal blocks
- Shielded cable for long runs

### Circuit 1: Main Entrance
```
Photocell NC Contact 1  ->  Terminal Block A1
Terminal Block A1       ->  GPIO17 (Pin 11)
Photocell NC Contact 2  ->  GND (Pin 9)
10kΩ Pull-up Resistor   ->  Between GPIO17 and 3.3V
```

### Circuit 2: Rear Exit
```
Photocell NC Contact 1  ->  Terminal Block B1
Terminal Block B1       ->  GPIO27 (Pin 13)
Photocell NC Contact 2  ->  GND (Pin 25)
10kΩ Pull-up Resistor   ->  Between GPIO27 and 3.3V
```

## Cable Specifications

### Signal Cables
- Type: Shielded twisted pair
- Gauge: 22-24 AWG
- Maximum length: 100m
- Shield connected to GND at Pi end only

### Power Cables
- Type: Stranded copper
- Gauge: 18-20 AWG
- Maximum length: 50m
- Voltage drop: < 5% at maximum length

## Grounding and Shielding

### Ground Points
1. Raspberry Pi GND pins
2. Terminal block GND bus
3. Cable shields (Pi end only)
4. Earth ground connection

### Shielding Requirements
- Use shielded cable for all signal wires
- Connect shields at one end only (Pi end)
- Keep signal cables away from power cables
- Use separate conduits where possible

## Testing Connections

### LTE HAT Test
1. Power on system
2. Check LED indicators:
   - PWR: Solid on
   - NET: Blinking during registration
   - SIG: Blinking indicates signal strength
   - ACT: Flashes with data activity

### Circuit Testing
1. Test each circuit with voltmeter:
   - Normal state: 3.3V (pull-up active)
   - Triggered state: 0V (circuit broken)
2. Check resistance:
   - Circuit closed: < 1Ω
   - Circuit open: > 1MΩ

## Troubleshooting

### Common Issues

#### No LTE Connection
1. Check antenna connection
2. Verify SIM card seating
3. Confirm LED status
4. Test voltage at HAT pins

#### Circuit False Triggers
1. Check cable shielding
2. Verify pull-up resistors
3. Test for loose connections
4. Check for ground loops

#### Power Issues
1. Measure Pi supply voltage
2. Check terminal block connections
3. Verify cable resistance
4. Test for shorts to ground

## Maintenance

### Regular Checks
1. Inspect all connections monthly
2. Test circuit operation weekly
3. Check cable condition
4. Verify LED status
5. Clean any dust/debris

### Documentation
- Record any changes to wiring
- Keep voltage/resistance measurements
- Document troubleshooting steps
- Update diagrams as needed
