/* Copyright 2016 University of Szeged.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "debugger.h"

#define PORT 5001
#define BLACKLOG 1
#define BUFFER_SIZE 1024

int sock, connected, true = 1; 
char* data[BUFFER_SIZE] , recv_data[BUFFER_SIZE]; 
ssize_t bytes_recieved;

struct sockaddr_in server_addr, client_addr;    
socklen_t sin_size = sizeof (struct sockaddr_in);

void remote_init()
{
  /** Server adress declaration */
  server_addr.sin_family = AF_INET;         
  server_addr.sin_port = htons(PORT); // host to network long (PORT)
  server_addr.sin_addr.s_addr = INADDR_ANY; // ip address
  bzero (&(server_addr.sin_zero), BLACKLOG); 

  if ((sock = socket (AF_INET, SOCK_STREAM, 0)) == -1)
  {
      printf ("Socket error!");
      exit(1);
  }

  if (setsockopt (sock,SOL_SOCKET, SO_REUSEADDR, &true, sizeof (int)) == -1)
  {
      printf ("Setsockopt error!");
      exit(1);
  }
  
  if (bind (sock, (struct sockaddr *)&server_addr, sizeof (struct sockaddr)) == -1)
  {
      printf ("Bind error, unable to bind!");
      exit(1);  
  }

  if (listen (sock, 5) == -1)
  {
      printf("Listen error!");
      exit(1);      
  }

  printf ("TCPServer Waiting for client on port %d. Please run client in /jerry-debugger folder.", PORT);
  fflush (stdout);

  // Connect from the client 
  connected = accept (sock, (struct sockaddr *)&client_addr, &sin_size);

  printf ("\n Connected from: (%s , %d)\n",
          inet_ntoa (client_addr.sin_addr), ntohs (client_addr.sin_port));
}

void send_to_client(uint8_t* data)
{
  // size_t size = strlen(data);
  
  // while (size > 0)
  // {
    send (connected, data, strlen((char*) data), 0);
    // sleep(1);
    // size--;
  // }
  // sleep(1);

  // bytes_recieved = recv(connected,recv_data,1024,0);
  // recv_data[bytes_recieved] = '\0';

  // if (strcmp(recv_data, "S") || strcmp(recv_data, "s"))
  // {
    // printf("Stopped, connection closed!\n");
    // close(connected);
    // close(sock);
  // }

  // else if (strcmp(recv_data , "G") || strcmp(recv_data , "g"))
  // {
  //   printf("Go on...\n");
  // }
}

// close socket connection
void connection_closed()
{
  printf("TCPServer connection closed on port %d.\n", PORT);
  close(connected);
  close(sock);
}