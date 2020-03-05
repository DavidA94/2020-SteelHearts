#include <PRIZM.h>
#include "dataTypes.hpp"
#include "DriveTrain.hpp"
#include "DataMarkers.hpp"

// ========== BEGIN GLOBALS :( ==========
const PRIZM prizm;
const EXPANSION expansion;
const DriveTrain driveTrain(&prizm, &expansion);

// These are used to blink the LEDs so we know what is going on
unsigned long redInterval = 200;
unsigned long redPreviousMillis = 0;
int redLedState = LOW;

unsigned long greenInterval = 200;
unsigned long greenPreviousMillis = 0;
int greenLedState = LOW;
bool blinkGreen = false;
int blinkGreenCount = 0;

// This is used to know what to call once the correct DataMarker is identified
void (*dataHandler)() = nullptr;

// ========== END GLOBALS :) ==========

void blinkGreenLed(unsigned long currentMillis)
{
    // No-op if we're not using green
    if (!blinkGreenLed) // || blinkGreenCount == 0)
    {
        return;
    }

    if (currentMillis - greenPreviousMillis >= greenInterval)
    {
        // save the last time the LED changed
        greenPreviousMillis = currentMillis;

        // Figure out the right state and set it
        greenLedState = greenLedState == LOW ? HIGH : LOW;
        prizm.setGreenLED(greenLedState);

        --blinkGreenCount;
    }
}

void blinkRedLed(unsigned long currentMillis)
{
    if (currentMillis - redPreviousMillis >= redInterval)
    {
        // save the last time the LED changed
        redPreviousMillis = currentMillis;

        // Figure out the right state and set it
        redLedState = redLedState == LOW ? HIGH : LOW;
        prizm.setRedLED(redLedState);
    }
}

void handleSetWheelSpeed()
{
    const int NEEDED_BYTES = 3;
    const int MAX_MOTOR_VALUE = 100;

    // Don't read the data until we have enough
    if (Serial.available() >= NEEDED_BYTES)
    {
        // Serial.read() returns a single byte of data. The data we are being sent is in the form of
        // a standard byte, or unsigned char [0. 255]. We need our values to allow for negatives, so
        // we use a char type instead. The incoming values will be [0, 200], but the code is written
        // such that it expects a range of [-100, 100], which is what the motors take in. The values
        // need to be subtracted so that they are in that range, and stored in a char which can hold
        // [-128, 127]
        char x = Serial.read() - MAX_MOTOR_VALUE;
        char y = Serial.read() - MAX_MOTOR_VALUE;
        char r = Serial.read() - MAX_MOTOR_VALUE;

        driveTrain.setDriveSpeed(x, y, r);

        // Make sure we clear this so the main loop will re-evaluate what to call next
        dataHandler = nullptr;
    }
}

void setup()
{
    Serial.begin(9600);
    prizm.PrizmBegin();
}

void loop()
{
    // Blink the Red LED every <INTERVAL> ms so we know things are working
    unsigned long currentMillis = millis();
    blinkGreenLed(currentMillis);
    blinkRedLed(currentMillis);

    // If we have any serial data
    if (Serial.available() > 0)
    {
        if (dataHandler == nullptr)
        {
            byte data = Serial.read();
            // Serial.print("Got data=");
            // Serial.println(data);

            if (data == DataMarkers::SetWheelSpeed)
            {
                dataHandler = &handleSetWheelSpeed;
                dataHandler();
            }
            else if (data == DataMarkers::BlinkWaitingForController)
            {
                blinkGreen = true;
                blinkGreenCount = -1;
                greenInterval = 500;
            }
            else if (data == DataMarkers::BlinkControllerConnected)
            {
                blinkGreen = true;
                blinkGreenCount = 10;
                greenInterval = 200;
            }
        }
        else
        {
            dataHandler();
        }
    }
}
