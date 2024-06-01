#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>
#include <semaphore.h>
#include <math.h>

#define _USE_MATH_DEFINES
#define MAX_BULLETS 3
#define MAX_PLAYERS 3
#define BOARD_WIDTH 800
#define BOARD_HEIGTH 600
#define TANK_SPEED 5
#define TANK_WIDTH 100
#define TANK_HEIGHT 110
#define TANK_PICK_WIDTH 170
#define TANK_PICK_HEIGTH 150
#define BULLET_SPEED 10
#define DELAY 100000
#ifndef M_PI
    #define M_PI 3.14159265358979323846
#endif


//ENUMS


//STRUCTS
typedef struct{
    float x;
    float y;
} Point;

typedef struct{
    Point position;
    short isAlive;
    int direction;
} Bullet;

typedef struct{
    Point position;
    int turnover_deg;
    char colour;
    short isAlive;
    Bullet bullets[MAX_BULLETS];
} Tank;

typedef struct{
    sem_t game_semaphore;
    Tank tanks[MAX_PLAYERS];
    float board_width;
    float board_height;
} Game;

typedef struct
{
    int client_id;
    Game* game;
} Incoming_client_info;

typedef struct{
    int socket_fd;
    struct sockaddr_in client_address;
    short is_active;
} Client;

//HELPER FUNCTIONS
int count_bullets(const Tank* tank);
void init_tank(Tank* tank, char color,float x, float y);
void append_player_tank(int player_id, Game* game, char color,float x, float y);
Point random_position();
void delete_player_tank(int palyer_id, Game* game);
void init_game(Game* game){
    if(sem_init(&game->game_semaphore,0,1) != 0){
        perror("Game sempahore initialization failed\n");
        exit(EXIT_FAILURE);
    }
    game->board_height = (float)BOARD_WIDTH;
    game->board_width = (float)BOARD_HEIGTH;
    
    for(int i = 0; i < MAX_PLAYERS; i++){
        game->tanks[i].isAlive = 0;
    }
}

Point random_position(){
    Point point;
    point.x = (float)rand() / ((float)RAND_MAX / ((float)BOARD_WIDTH));
    point.y = (float)rand() / ((float)RAND_MAX / ((float)BOARD_HEIGTH));
    return point;
}
int count_bullets(const Tank* tank){
    int out = 0;
    for(int i = 0; i < MAX_BULLETS; i++){
        if(tank->bullets->isAlive) out++;
    }
    return out;
}

void init_tank(Tank* tank,char color,float x, float y){
    tank->turnover_deg = 0;
    tank->position.x = x;
    tank->position.y = y;
    tank->colour = color;
    tank->isAlive = 1;
}

void append_player_tank(int player_id, Game* game, char color,float x, float y){
    sem_wait(&game->game_semaphore);
    init_tank(&game->tanks[player_id], color, x, y);
    sem_post(&game->game_semaphore);
}

void delete_player_tank(int palyer_id, Game* game){
    sem_wait(&game->game_semaphore);
    game->tanks[palyer_id].isAlive = 0;
    sem_post(&game->game_semaphore);
}


//GLOBALS
sem_t client_semaphore;
Client clients[MAX_PLAYERS];
int active_players = 0;




//MAIN LOGIC FUNCTIONS
void make_move(int client_id, char move, Game* game);
void update_tank(Tank* tank, char move);
void update_bullets(Game* game);
void check_bullet_hits(Game* game);
void* client_handler(void* args){
    Incoming_client_info client_info = *((Incoming_client_info*) args);
    int client_id = client_info.client_id;
    Game* game = client_info.game;
    Client client;
    char buffer[1];
    Point position = random_position();

    sem_wait(&client_semaphore);
    client = clients[client_id];
    sem_post(&client_semaphore);
    
    recv(client.socket_fd, buffer, 1, 0);
    printf("New player add with colour of %c\n", buffer[0]);
    append_player_tank(client_id, game, buffer[0],position.x, position.y);
    memset(buffer, 0, 1);

    while(1){
        int bytes_recived = recv(client.socket_fd, buffer, 1, 0);
        printf("Move %c", buffer[0]);
        if(bytes_recived <= 0){
            delete_player_tank(client_id, game);
            sem_wait(&client_semaphore);
            close(client.socket_fd);
            clients[client_id].is_active = 0;
            active_players--;
            sem_post(&client_semaphore);
            pthread_exit(NULL);
        }
        make_move(client_id, buffer[0], game);
        memset(buffer, 0, 1);
    }

}

void* game_handler(void* args){
    Game* game = (Game*)args;
    while(1){
        //printf("xdsdd%d\n", (int)sizeof(game->tanks));
        sem_wait(&client_semaphore);
        sem_wait(&game->game_semaphore);
        for(int i = 0; i < MAX_PLAYERS; i++){
            if(clients[i].is_active){
                send(clients[i].socket_fd, game->tanks, sizeof(game->tanks), 0);
            }
        }
        sem_post(&client_semaphore);
        //update bullet position and check for colission;
        update_bullets(game);
        sem_post(&game->game_semaphore);
       usleep(DELAY);
    }
}

void update_bullets(Game* game){
    for(int i = 0; i < MAX_PLAYERS; i++){
        if(!game->tanks[i].isAlive) continue;
        for(int j = 0; j < MAX_BULLETS; j++){
            if(!game->tanks[i].bullets[j].isAlive) continue;
                game->tanks[i].bullets[j].position.x += BULLET_SPEED * cos(game->tanks[i].bullets[j].direction * M_PI /180);
                game->tanks[i].bullets[j].position.y -= BULLET_SPEED * sin(game->tanks[i].bullets[j].direction * M_PI /180);
            if(0 >= game->tanks[i].bullets[j].position.x || game->tanks[i].bullets[j].position.x >= BOARD_WIDTH ||
            0 >= game->tanks[i].bullets[j].position.y || game->tanks[i].bullets[j].position.x >= BOARD_HEIGTH){
                game->tanks[i].bullets[j].isAlive = 0;
            }
            puts("xd");
        }
    }
}
void make_move(int client_id, char move, Game* game){
    sem_wait(&game->game_semaphore);
    update_tank(&game->tanks[client_id], move);
    sem_post(&game->game_semaphore);
}

void update_tank(Tank* tank, char move){
    float new_x, new_y;
    switch(move){
        case 'L':
            tank->turnover_deg += 5;
            break;
        case 'R':
            tank->turnover_deg -= 5;
            break;
        case 'U':
            new_x = tank->position.x + TANK_SPEED * cos(tank->turnover_deg * M_PI /180);
            new_y = tank->position.y - TANK_SPEED * sin(tank->turnover_deg * M_PI /180);
            if(0 <= new_x <= BOARD_WIDTH - TANK_WIDTH && 0 <= new_y <= BOARD_HEIGTH - TANK_HEIGHT){
                tank->position.x = new_x;
                tank->position.y = new_y;
            }
            break;
        case 'D':
            new_x = tank->position.x - TANK_SPEED * cos(tank->turnover_deg * M_PI /180);
            new_y = tank->position.y + TANK_SPEED * sin(tank->turnover_deg * M_PI /180);
            if(0 <= new_x <= BOARD_WIDTH - TANK_WIDTH && 0 <= new_y <= BOARD_HEIGTH - TANK_HEIGHT){
                tank->position.x = new_x;
                tank->position.y = new_y;
            }
            break;
        case 'S':
            for(int i = 0; i < MAX_BULLETS; i++){
                if(!tank->bullets[i].isAlive){
                    tank->bullets[i].position.x = tank->position.x + (TANK_WIDTH/2) * cos(tank->turnover_deg * M_PI /180);
                    tank->bullets[i].position.y = tank->position.y - (TANK_WIDTH/2) * sin(tank->turnover_deg * M_PI /180);
                    tank->bullets[i].direction = tank->turnover_deg;
                    tank->bullets[i].isAlive = 1; 
                    break;
                }
            }
            break;
    }
}


int main(){
    srand(time(NULL));

    //Semaphore initialization
    if(sem_init(&client_semaphore, 0, 1) != 0){
        perror("Semaphore initialization failed\n");
        exit(EXIT_FAILURE);
    }

    //Server socket initialization
    int server_scoket_fd = socket(AF_INET, SOCK_STREAM, 0);
    
    if(server_scoket_fd == -1){
        perror("Error creating server socket");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_address.sin_port = htons(5001);

    if (bind(server_scoket_fd, (struct sockaddr*)&server_address, sizeof(server_address)) == -1) {
        perror("Error binding address to socket");
        exit(EXIT_FAILURE);
    }

    //game initialization
    Game game;
    init_game(&game);
    for(int i = 0; i < MAX_PLAYERS; i++){
        clients[i].is_active = 0;    
    }

    pthread_t game_thread;
    if(pthread_create(&game_thread, NULL, game_handler, &game) != 0){
        perror("Error initializing game thread");
        exit(EXIT_FAILURE);
    }

    if (listen(server_scoket_fd, MAX_PLAYERS) == -1) {
        perror("Error listening on socket");
        exit(EXIT_FAILURE);
    }

    printf("Server running at address: %s:%d\n", inet_ntoa(server_address.sin_addr), ntohs(server_address.sin_port));

    //MAIN-THREAD - new clients listener
    while(1){
        struct sockaddr_in client_address;
        socklen_t client_addr_len = sizeof(client_address);
        int incoming_socket_fd = accept(server_scoket_fd, (struct sockaddr*)&client_address, &client_addr_len);
        
        if (incoming_socket_fd == -1) {
            perror("Error accepting connection");
            continue;
        }
            
        if(active_players < MAX_PLAYERS){
            sem_wait(&client_semaphore);
            int client_id;
            for(int i = 0; i < MAX_PLAYERS; i++){
                if(clients[i].is_active == 0){
                    clients[i].socket_fd = incoming_socket_fd;
                    clients[i].client_address = client_address;
                    clients[i].is_active = 1;
                    client_id = i;
                    break;  
                }
            }
            Incoming_client_info* args =(Incoming_client_info*) malloc(sizeof(Incoming_client_info));
            args->client_id = client_id;
            args->game = &game;
            pthread_t client_thread;

            if(pthread_create(&client_thread, NULL, client_handler, args) != 0){
                perror("Error while creating a client thread");
                close(incoming_socket_fd);
            }

            printf("New client connected, address: %s and id: %d \n", inet_ntoa(client_address.sin_addr), client_id);
            active_players++;
            sem_post(&client_semaphore);
        }else{
            char* connection_refused_info = "Connection refused - maxiimum number of active players reached";
            //send(incoming_socket_fd, connection_refused_info, strlen(connection_refused_info), 0);
            printf("%s\n", connection_refused_info);
            close(incoming_socket_fd);
        }
    }

}