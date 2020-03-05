#include <math.h>
#include "dataTypes.hpp"
#include "DriveTrain.hpp"

// Stolen from https://www.roboteq.com/index.php/applications/applications-blog/entry/driving-mecanum-wheels-omnidirectional-robots
//             https://github.com/cporter/ftc_app/blob/rr/pre-season/TeamCode/src/main/java/soupbox/Mecanum.java
void DriveTrain::setDriveSpeed(char x, char y, char rotation)
{
    // Get the values to -1 to 1 so we can do powers without going off the charts
    const double xInterim = pow(x / MAX_MOTOR_VALUE, SPEED_EXPONET);
    const double yInterim = pow(y / MAX_MOTOR_VALUE, SPEED_EXPONET);
    const double rotationInterim = pow(rotation / MAX_MOTOR_VALUE, SPEED_EXPONET);

    // Get the speed based off the hypotenuse. Make sure we don't go past [-1, 1]
    const double speed = fmax(-MAX_INTERIM_VALUE, fmin(MAX_INTERIM_VALUE, sqrt((xInterim * xInterim) + (yInterim + yInterim))));
    const double direction = atan2(xInterim, yInterim);

    // left front, right front, left rear, right rear
    // This also converts from [-1, 1] to [-100, 100] (or whatever the values are in the constants)
    const double rfWheel = (speed * sin(direction + (M_PI / 4.0)) - rotationInterim) * MAX_MOTOR_VALUE;
    const double rrWheel = (speed * cos(direction + (M_PI / 4.0)) - rotationInterim) * MAX_MOTOR_VALUE;
    const double lfWheel = (speed * cos(direction + (M_PI / 4.0)) + rotationInterim) * MAX_MOTOR_VALUE;
    const double lrWheel = (speed * sin(direction + (M_PI / 4.0)) + rotationInterim) * MAX_MOTOR_VALUE;

/*
#ifdef DEBUG
    Serial.print(x);
    Serial.print("\t");
    Serial.print(y);
    Serial.print("\t");
    Serial.print(xInterim);
    Serial.print("\t");
    Serial.print(yInterim);
    Serial.print("\t");
    Serial.print(speed);
    Serial.print("\t");
    Serial.print(direction);
    Serial.print("\t");
    Serial.print(rfWheel);
    Serial.print("\t");
    Serial.print(rrWheel);
    Serial.print("\t");
    Serial.print(lfWheel);
    Serial.print("\t");
    Serial.println(lrWheel);
#endif
*/

    m_prizm->setMotorPower(RIGHT_FRONT_WEEL_INDEX, rfWheel);
    m_prizm->setMotorPower(RIGHT_REAR_WEEL_INDEX, rrWheel);

    m_expansion->setMotorPower(WHEEL_EXPANSION, LEFT_FRONT_WEEL_EXPANSION_INDEX, lfWheel * LEFT_WHEEL_EXPANSION_MULTIPLE);
    m_expansion->setMotorPower(WHEEL_EXPANSION, LEFT_REAR_WEEL_EXPANSION_INDEX, lrWheel * LEFT_WHEEL_EXPANSION_MULTIPLE);
}
