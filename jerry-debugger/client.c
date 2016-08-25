#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>

#define PORT 5001
#define BLACKLOG 1
#define BUFFER_SIZE 1024

int main()
{
        int sock, bytes_received;
        char recv_data[BUFFER_SIZE], send_data[BUFFER_SIZE];
        struct hostent *host;
        struct sockaddr_in server_addr;  

        host = gethostbyname("127.0.0.1");

        if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1)
        {
            perror("Socket error!");
            exit(1);
        }

        server_addr.sin_family = AF_INET;     
        server_addr.sin_port = htons(PORT);   
        server_addr.sin_addr = *((struct in_addr *)host->h_addr);
        bzero(&(server_addr.sin_zero),BLACKLOG); 

        if (connect(sock, (struct sockaddr *)&server_addr,
                    sizeof(struct sockaddr)) == -1) 
        {
            perror("Connected error!");
            exit(1);
        }

        printf("Succesfully connected to debugger!\n");

        while(1)
        {
          bytes_received = recv(sock,recv_data,1024,0);

          if ( bytes_received == 0 )
          {
            printf("\nNo more packages. Connection closed.\n");
            break;
          }

          recv_data[bytes_received] = '\0';
          printf("Received data = %s\n" , recv_data);
        }
        
        //   printf("\nStop[S] or Go[G]: ");
        //   gets(send_data);

        //   send(sock,send_data,strlen(send_data),0);

        //   if (strcmp(send_data, "G") || strcmp(send_data, "g")){
        //     send(sock,send_data,strlen(send_data), 0);
        //     printf("G");
        //   }
        //   else if (strcmp(send_data, "S") || strcmp(send_data, "S")){
        //     send(sock,send_data,strlen(send_data), 0);
        //     printf("S TO STOP AND QUIT");
        //     close(sock);
        //     quit = 1;
        //     break;
        //   }
        //   else {
        //     printf("Undefined command!");
        //   }
        // }

  return 0;
}
