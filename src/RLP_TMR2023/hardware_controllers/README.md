# Hardware Controllers

## Overview

This directory contains the hardware controllers for the RLP_TMR2023. The hardware controllers are responsible for
interfacing with the hardware of the robot.  
They follow the next structure:

- Every hardware controller is a class that inherits from the Singleton class.
- Every hardware controller has a `setup` method that initializes the hardware, **remember to never put code in the
  constructor**.
- Every hardware controller has a mock class.
- Every hardware controller only do one type of action. For example, the `MotorsController` only controls the motors.

## List of Hardware Controllers

- `MotorsController`: Controls the base motors of the robot.
- `CameraController`: Controls the camera and has all the utility functions of the robot.

### TODO

- `IMUController`: Controls the IMU.
- `ServosController`: Controls the servos of the robot (control the `arm`, `claw` and `tray`).
- `DistanceSensorsController`: Controls the distance sensors of the robot.
- `OLEDDisplayController`: Controls the OLED display of the robot.
- `BuzzerController`: Controls the buzzer of the robot.

### Responsibilities

#### Jesus

-IMUController
-BuzzerController
-OLEDDisplayController

#### Alfredo

-ServosController
-DistanceSensorsController
