#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define MAX_TIME 85
#define DHT11PIN 11  /*this is GPIO 7 for wiringpi */
int dht11_val[5]={0,0,0,0,0};

int dht11_read_val()
{
  uint8_t lststate=HIGH;
  uint8_t counter=0;
  uint8_t j=0,i;
  for(i=0;i<5;i++)
     dht11_val[i]=0;
  pinMode(DHT11PIN,OUTPUT);
  digitalWrite(DHT11PIN,LOW);
  delay(18);
  digitalWrite(DHT11PIN,HIGH);
  delayMicroseconds(40);
  pinMode(DHT11PIN,INPUT);
  for(i=0;i<MAX_TIME;i++)
  {
    counter=0;
    while(digitalRead(DHT11PIN)==lststate){
      counter++;
      delayMicroseconds(1);
      if(counter==255)
        break;
    }
    lststate=digitalRead(DHT11PIN);
    if(counter==255)
       break;
    // top 3 transistions are ignored
    if((i>=4)&&(i%2==0)){
      dht11_val[j/8]<<=1;
      if(counter>16)
        dht11_val[j/8]|=1;
      j++;
    }
  }
  // verify cheksum and print the verified data
  if((j>=40)&&(dht11_val[4]==((dht11_val[0]+dht11_val[1]+dht11_val[2]+dht11_val[3])& 0xFF)))
  {
    return (dht11_val[2]);
  }
  else
    return (9999);
}

int main(void)
{
  int t=0;
  int count=0;
  float avg = 0;
  int temp[3] = {0, 0, 0};

  if(wiringPiSetup()==-1)
      exit(1);

  /* let's read 3 correct temperature values*/
  while(count < 3) {
      t = dht11_read_val();
      if (t != 9999) {
          temp[count] = t;
          count++;
      }
      delay(500);
  }

  /*calculate the average temperature out of the 3 reads from sensor*/
  avg = (temp[0] + temp[1] + temp[2])/3;

  printf("%.2f", avg);

  return 0;
}

