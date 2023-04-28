#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 30;    // variable to store the servo position
const int BUTTON_PIN = 10;  // the number of the pushbutton pin
const int LED_PIN =  4;   // the number of the LED pin

boolean DoorState = true; // true = locked, false = unlocked
int buttonState = 0;   // variable for reading the pushbutton status

void setup() {
  Serial.begin(9600);   // baud rate
  pinMode(2, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP); // unlock button
  myservo.attach(7);  // attaches the servo on pin 9 to the servo object
 
}


void loop() {

  if (Serial.available()) {

    switch(Serial.read()) {

      case '1': // unlocks the door

        if (DoorState == false) {break; }    // if door is already unlocked skip
        digitalWrite(2,HIGH); // unlock sequence
        
        for (pos = 30; pos <= 160; pos += 1) { // goes from 0 degrees to 180 degrees
          // in steps of 1 degree
          myservo.write(pos);              // tell servo to go to position in variable 'pos'
          delay(15);                       // waits 15ms for the servo to reach the position
        }

          delay(1000);
          digitalWrite(2,LOW);  
        DoorState = false;        // mark door as unlocked
        break;
        
      case '0': // locks the door
      
        if (DoorState == true) {break; }    // if door is already locked skip
        digitalWrite(4,HIGH); // lock sequence
      
        for (pos = 0; pos <= 180; pos += 1) { 
          // in steps of 1 degree
          myservo.write(pos);              
          delay(15);                       
        }
        for (pos = 180; pos >= 0; pos -= 1) { 
          myservo.write(pos);              
          delay(15);                       
        }
        delay(1000);
        digitalWrite(4,LOW);
        DoorState = true;        // mark door as locked
        Serial.println("0"); // tells the pi the door is locked
        break;
        
      default: break;
    }


    
  }


    // read the state of the pushbutton value:
    buttonState = digitalRead(BUTTON_PIN);

    // control LED according to the state of button
    if(buttonState == LOW && DoorState == false) {        // If button is pressing

        digitalWrite(4,HIGH); // lock sequence
      

        for (pos = 160; pos >= 30; pos -= 1) { 
          myservo.write(pos);              
          delay(15);                       
        }
        delay(1000);
        digitalWrite(4,LOW);
        DoorState = true;        // mark door as locked
        Serial.println("0"); // tells the pi the door is locked
             
  
    }
              
}
