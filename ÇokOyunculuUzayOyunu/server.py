import socket
import pickle
from _thread import *
import random
import time

server = "10.66.114.86"  # KENDİ IP'n ile değiştir
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Server başlatıldı...")

players = {
    0: {"pos": [400, 900], "bullets": [], "ammo": 30, "score": 0, "hit": False},
    1: {"pos": [1200, 900], "bullets": [], "ammo": 30, "score": 0, "hit": False}
}

meteors = [[600, 0], [900, -300], [300, -600]]
meteor_speed = 5
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000

# Oyun durumu
game_active = False
game_start_time = 0
countdown_active = False
countdown_start = 0
connected_players = 0
game_over = False
winner = None

def reset_game():
    global players, meteors, game_active, game_start_time, countdown_active, countdown_start, game_over, winner
    
    players = {
        0: {"pos": [400, 900], "bullets": [], "ammo": 30, "score": 0, "hit": False},
        1: {"pos": [1200, 900], "bullets": [], "ammo": 30, "score": 0, "hit": False}
    }
    
    meteors = [[600, 0], [900, -300], [300, -600]]
    game_active = False
    game_start_time = 0
    countdown_active = False
    countdown_start = 0
    game_over = False
    winner = None

def threaded_client(conn, player):
    global connected_players, countdown_active, countdown_start, game_active, game_start_time, game_over, winner
    
    conn.send(str(player).encode())
    connected_players += 1
    
    # İki oyuncu bağlanınca geri sayımı başlat
    if connected_players == 2 and not countdown_active and not game_active:
        countdown_active = True
        countdown_start = time.time()
    
    while True:
        try:
            data = pickle.loads(conn.recv(4096))
            
            players[player]["pos"] = data["pos"]
            
            # Oyun aktifse mermileri işle
            if game_active and not game_over:
                # Yeni mermi ekle
                if "new_bullet" in data and data["new_bullet"] is not None and players[player]["ammo"] > 0:
                    players[player]["bullets"].append(data["new_bullet"])
                    players[player]["ammo"] -= 1
                
                # Mevcut mermileri güncelle
                if "bullets" in data:
                    players[player]["bullets"] = data["bullets"]
                
                # Meteorları hareket ettir
                for meteor in meteors:
                    meteor[1] += meteor_speed
                    if meteor[1] > SCREEN_HEIGHT:
                        meteor[0] = random.randint(0, SCREEN_WIDTH - 50)
                        meteor[1] = -50
                
                # Mermi-meteor çarpışma
                for i in range(2):
                    for bullet in players[i]["bullets"][:]:
                        for meteor in meteors[:]:
                            bx, by = bullet
                            mx, my = meteor
                            if abs(bx - mx) < 40 and abs(by - my) < 40:
                                meteors.remove(meteor)
                                players[i]["bullets"].remove(bullet)
                                players[i]["score"] += 5  # 5 puan ekle
                                meteors.append([random.randint(0, SCREEN_WIDTH - 50), -50])
                                break
                
                # Oyuncu-meteor çarpışma
                for i in range(2):
                    px, py = players[i]["pos"]
                    for meteor in meteors[:]:
                        mx, my = meteor
                        if abs(px + 30 - mx) < 50 and abs(py + 30 - my) < 50:  # Oyuncu merkezini kullan
                            players[i]["hit"] = True
                            game_over = True
                            # Diğer oyuncu kazanır
                            winner = 1 - i
                
                # Süre kontrolü (1 dakika)
                current_time = time.time()
                if current_time - game_start_time > 60:  # 60 saniye
                    game_over = True
                    # Puanı fazla olan kazanır, eşitlikse 0. oyuncu kazanır
                    if players[0]["score"] >= players[1]["score"]:
                        winner = 0
                    else:
                        winner = 1
            
            # Geri sayım kontrolü
            if countdown_active:
                current_time = time.time()
                if current_time - countdown_start > 3:  # 3 saniye geri sayım
                    countdown_active = False
                    game_active = True
                    game_start_time = current_time
            
            # Yanıt hazırla
            reply = {
                0: players[0],
                1: players[1],
                "meteors": meteors,
                "game_active": game_active,
                "countdown": countdown_active,
                "countdown_time": int(3 - (time.time() - countdown_start)) if countdown_active else 0,
                "game_over": game_over,
                "winner": winner,
                "time_left": int(60 - (time.time() - game_start_time)) if game_active and not game_over else 0
            }
            
            conn.sendall(pickle.dumps(reply))
            
            # Oyun bittiyse ve yeniden başlatma sinyali gelirse
            if game_over and "reset" in data and data["reset"]:
                reset_game()
                if connected_players == 2:
                    countdown_active = True
                    countdown_start = time.time()
        
        except Exception as e:
            print("Connection lost:", e)
            connected_players -= 1
            break

    print("Player", player, "disconnected")
    conn.close()

player_count = 0

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    
    start_new_thread(threaded_client, (conn, player_count))
    player_count += 1
    player_count %= 2  # Sadece 0 ve 1 oyuncu ID'leri