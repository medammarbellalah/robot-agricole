#define ENA 3   // Broche de contrôle de vitesse du moteur gauche
#define IN1 A0   // Broche de commande directionnelle 1 du moteur gauche
#define IN2 A1   // Broche de commande directionnelle 2 du moteur gauche
#define ENB 5  // Broche de contrôle de vitesse du moteur droit
#define IN3 A2  // Broche de commande directionnelle 1 du moteur droit
#define IN4 A3 
// Define the pins for ultrasonic sensors
const int trigPin1 = 6;
const int echoPin1 = 9;
const int trigPin2 = 11;
const int echoPin2 = 10;

// Define variables to store distance values
long duration1, leftDistance;
long duration2, rightDistance;


// Variables pour le contrôle PID

double Kp = 0.8; // Terme proportionnel
double Kd = 0.5; // Terme dérivé
double Ki = 0.4; // Terme  
double lastError = 0;
double integral = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Define pin modes
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);
}

void loop() {
  // Measure distance from the first ultrasonic sensor
  digitalWrite(trigPin1, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin1, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin1, LOW);
  duration1 = pulseIn(echoPin1, HIGH);
  leftDistance = duration1 * 0.034 / 2;

  // Measure distance from the second ultrasonic sensor
  digitalWrite(trigPin2, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin2, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin2, LOW);
  duration2 = pulseIn(echoPin2, HIGH);
  rightDistance = duration2 * 0.034 / 2;

  // Print distance values to the serial monitor
  Serial.print("Distance from sensor 1: ");
  Serial.print(leftDistance);
  Serial.println(" cm");
  Serial.print("Distance from sensor 2: ");
  Serial.print(rightDistance);
  Serial.println(" cm");

 double error = leftDistance - rightDistance;
  integral += error;
  
  double derivative = error - lastError;
  lastError = error;
  
  double correction = Kp * error + Ki * integral + Kd * derivative;
  
  // Vitesses des moteurs
  double leftSpeed = 70 - correction;
  double rightSpeed = 70 + correction;
  
  // Contrôle du moteur gauche
  analogWrite(ENB, abs(leftSpeed));
  if (leftSpeed > 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }

  
  // Contrôle du moteur droit
  analogWrite(ENA, abs(rightSpeed));
  if (rightSpeed > 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }
  
  // Delay before next measurement
  delay(100);
}
