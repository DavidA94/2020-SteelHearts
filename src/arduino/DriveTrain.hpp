#include <PRIZM.h>
#include "dataTypes.hpp"

class DriveTrain
{
private:
    const double MAX_MOTOR_VALUE = 100;
    const double MAX_INTERIM_VALUE = 1.0;
    const int SPEED_EXPONET = 3;

    // These should be on the main board
    const int RIGHT_FRONT_WEEL_INDEX = 1;
    const int RIGHT_REAR_WEEL_INDEX = 2;

    // These should be from the expansion
    const int WHEEL_EXPANSION = 1;
    const int LEFT_WHEEL_EXPANSION_MULTIPLE = -1;
    const int LEFT_FRONT_WEEL_EXPANSION_INDEX = 1;
    const int LEFT_REAR_WEEL_EXPANSION_INDEX = 2;

    PRIZM *m_prizm;
    EXPANSION *m_expansion;
    double m_rotation;

public:
    DriveTrain(PRIZM *prizm, EXPANSION *expansion) : m_prizm(prizm), m_expansion(expansion) {}

    void setDriveSpeed(char x, char y, char rotation);
};
