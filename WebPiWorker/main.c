#include <stdio.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <netinet/in.h>
#include <string.h>
#include <wiringPi.h>



//int k;

int pins[4] = {8, 9, 7, 15};

int state [4];

void on(int number);
void off(int number);
void allOff();
void allOn();

int main()
{
    for(int i=0;i<4;i++)
    {
        state[i]=0;
    }
    wiringPiSetup();
for (int k = 0; k<4; k++)
    {
        pinMode(pins[k], OUTPUT);
    }
  int welcomeSocket, newSocket, portNum, nBytes;    //SERVER
  char buffer[2];
  struct sockaddr_in serverAddr;
  struct sockaddr_storage serverStorage;
  socklen_t addr_size;
  int i;
  int j=0;
  int piID=11;
  i=0;
  welcomeSocket = socket(PF_INET, SOCK_STREAM, 0);

  portNum = 3125;

  serverAddr.sin_family = AF_INET;
  serverAddr.sin_port = htons(portNum);
  serverAddr.sin_addr.s_addr = inet_addr("192.168.3.13");
  memset(serverAddr.sin_zero, '\0', sizeof serverAddr.sin_zero);

  bind(welcomeSocket, (struct sockaddr *) &serverAddr, sizeof(serverAddr));

  if(listen(welcomeSocket,5)==0)
    printf("Listening\n");
  else
    printf("Error\n");

  addr_size = sizeof serverStorage;
allOff();
  // loop to keep accepting new connections
  while(1)
    {
    newSocket = accept(welcomeSocket, (struct sockaddr *) &serverStorage, &addr_size);
    if(1)
    {
    // fork a child process to handle the new connection
    nBytes = 1;
      printf("\n\nconnected\n");
      // loop while connection is active
      while(nBytes!=0)
        {
        nBytes = recv(newSocket,buffer,2,0);


        if(nBytes!=0)
        {

            int intId = buffer[1] - '0';
            printf("id is %i\n",intId);
            printf("%i\n",state[1]);
            printf("%s\n",buffer);
            if(buffer[0]=='Q')
            {
                if(state[intId]==0)
                {
                    printf("Thing is off on pin %d.", intId);
                    buffer[0]='0';
                }
                else if(state[intId]==1)
                {
                    printf("Thing is on.");
                    buffer[0]='1';
                }

            }
            else if(buffer[0]=='N')
            {
                on(intId);
                buffer[0]='0'; //sends 0 if ok. 1 if not
            }
            else if(buffer[0]=='F')
            {
                off(intId);
                buffer[0]='0';//ditto
            }
            else
            {
                buffer[0] = '1';
            }

            buffer[1]='5';
            send(newSocket,buffer,1,0);
        }

      }
      close(newSocket);
      //exit(0);
    }
    // close the socket and go back to listening for new connections
    else
    {
      close(newSocket);
    }
  }

  return 0;
}


void on(int number)

{
        if (number<4&&number>=0) {

            digitalWrite(pins[number], HIGH);
            state[number]= 1;
            printf("set piin %d high", number);

        } else {
            printf("\nrelay does not exist, to be honest");
        }
    }
void off(int number)
{
        if (number<4&&number>=0) {

            digitalWrite(pins[number], LOW);
            state[number]= 0;
        } else {
            printf("\nrelay does not exist, to be honest");
        }
    }
    void allOff()
    {
        for (int i =0;i<4;i++) {

            on(i);
        }
    }

void allOn()
{
        for (int j =0;j<4;j++) {

            off(j);
        }
    }
