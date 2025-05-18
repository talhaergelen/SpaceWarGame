import pygame
from network import Network
import os

pygame.init()

WIDTH, HEIGHT = 1600, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2 Oyunculu Uzay Oyunu")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
FPS = 60

PLAYER_WIDTH, PLAYER_HEIGHT = 60, 60
BULLET_SPEED = 10
PLAYER_SPEED = 7

# Font tanımla
FONT = pygame.font.SysFont('comicsans', 40)
BIG_FONT = pygame.font.SysFont('comicsans', 80)

# Resimleri yükle
def load_image(name):
    try:
        image = pygame.image.load(name)
        return image
    except pygame.error as e:
        print(f"Resim yüklenemedi: {name}")
        print(str(e))
        return None

# Resim dosyalarının yolları - bu dosyaların kodunuzla aynı klasörde olduğunu varsayıyorum
# Eğer farklı bir yerdeyse, tam yollarını belirtin
BACKGROUND_IMG = load_image("image\\arkaplan2.jpg")
PLAYER1_IMG = load_image("image\\gemi11.png")
PLAYER2_IMG = load_image("image\\gemi22.png")
METEOR_IMG = load_image("image\\asteroit.png")
# Resimleri boyutlandır
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (WIDTH, HEIGHT))
PLAYER1_IMG = pygame.transform.scale(PLAYER1_IMG, (PLAYER_WIDTH, PLAYER_HEIGHT))
PLAYER2_IMG = pygame.transform.scale(PLAYER2_IMG, (PLAYER_WIDTH, PLAYER_HEIGHT))
METEOR_IMG = pygame.transform.scale(METEOR_IMG, (60, 60))  # Meteor boyutu

clock = pygame.time.Clock()

def draw_window(player_info, other_info, meteors, player_id, game_active, countdown, countdown_time, game_over, winner, time_left):
    # Arkaplan
    WIN.blit(BACKGROUND_IMG, (0, 0))

    # Orta çizgi
    pygame.draw.line(WIN, (0, 0, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 10)

    # Eğer oyun aktif değil ve geri sayım başlamadıysa "Oyuncu bekleniyor..." mesajı göster
    if not game_active and not countdown:
        waiting_text = BIG_FONT.render("Oyuncu Bekleniyor...", 1, WHITE)
        WIN.blit(waiting_text, (WIDTH//2 - waiting_text.get_width()//2, HEIGHT//2 - waiting_text.get_height()//2))
        
        info_text = FONT.render("İkinci oyuncunun bağlanması bekleniyor", 1, WHITE)
        WIN.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 + 80))
        
        pygame.display.update()
        return

    # Oyuncular
    player_pos = player_info["pos"]
    other_pos = other_info["pos"]
    
    if player_id == 0:
        WIN.blit(PLAYER1_IMG, (player_pos[0], player_pos[1]))
        WIN.blit(PLAYER2_IMG, (other_pos[0], other_pos[1]))
    else:
        WIN.blit(PLAYER2_IMG, (player_pos[0], player_pos[1]))
        WIN.blit(PLAYER1_IMG, (other_pos[0], other_pos[1]))

    # Mermiler
    for bullet in player_info["bullets"]:
        pygame.draw.circle(WIN, BLUE, (int(bullet[0]), int(bullet[1])), 5)
    for bullet in other_info["bullets"]:
        pygame.draw.circle(WIN, RED, (int(bullet[0]), int(bullet[1])), 5)

    # Meteorlar
    for mx, my in meteors:
        WIN.blit(METEOR_IMG, (mx - 30, my - 30))  # Merkezden çizildiği için 30 piksel kaydırıyoruz
    
    # Puanlar ve cephane
    score_text = FONT.render(f"Puan: {player_info['score']}", 1, WHITE)
    ammo_text = FONT.render(f"Mermi: {player_info['ammo']}", 1, WHITE)
    enemy_score_text = FONT.render(f"Rakip Puan: {other_info['score']}", 1, WHITE)
    
    WIN.blit(score_text, (10, 10))
    WIN.blit(ammo_text, (10, 50))
    WIN.blit(enemy_score_text, (WIDTH - enemy_score_text.get_width() - 10, 10))
    
    # Kalan süre
    if game_active and not game_over:
        time_text = FONT.render(f"Süre: {time_left}", 1, WHITE)
        WIN.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 10))
    
    # Geri sayım
    if countdown:
        countdown_text = BIG_FONT.render(f"{countdown_time}", 1, WHITE)
        WIN.blit(countdown_text, (WIDTH//2 - countdown_text.get_width()//2, HEIGHT//2 - countdown_text.get_height()//2))
        
        get_ready = FONT.render("Hazırlanın!", 1, WHITE)
        WIN.blit(get_ready, (WIDTH//2 - get_ready.get_width()//2, HEIGHT//2 - get_ready.get_height()//2 - 100))
    
    # Oyun sonu
    if game_over:
        if (winner == player_id):
            result_text = BIG_FONT.render("KAZANDIN!", 1, (0, 255, 0))
        else:
            result_text = BIG_FONT.render("KAYBETTİN!", 1, RED)
        
        WIN.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - result_text.get_height()//2))
        
        reason_text = None
        if player_info["hit"]:
            reason_text = FONT.render("Meteora çarptın!", 1, WHITE)
        elif other_info["hit"]:
            reason_text = FONT.render("Rakip meteora çarptı!", 1, WHITE)
        elif time_left <= 0:
            if player_info["score"] > other_info["score"]:
                reason_text = FONT.render("Daha fazla puan topladın!", 1, WHITE)
            else:
                reason_text = FONT.render("Rakip daha fazla puan topladı!", 1, WHITE)
        
        if reason_text:
            WIN.blit(reason_text, (WIDTH//2 - reason_text.get_width()//2, HEIGHT//2 + 80))
        
        restart_text = FONT.render("Yeniden başlamak için ENTER'a basın", 1, WHITE)
        WIN.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 150))

    pygame.display.update()


def main():
    run = True
    n = Network()
    player_id = n.id

    pos = [400, 900] if player_id == 0 else [1200, 900]
    bullets = []
    new_bullet = None
    reset_requested = False

    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # Oyun aktifse ve bitmemişse ateş et
                if event.key == pygame.K_SPACE and game_active and not game_over and player_info["ammo"] > 0:
                    new_bullet = [pos[0] + PLAYER_WIDTH // 2, pos[1]]
                    bullets.append(new_bullet)  # Hemen yerel listeye ekle
                
                # Oyun bittiyse yeniden başlat
                if event.key == pygame.K_RETURN and game_over:
                    reset_requested = True
        
        send_data = {
            "pos": pos,
            "bullets": bullets,
            "new_bullet": new_bullet,
            "reset": reset_requested
        }
        
        # Her döngüde yeni mermi sıfırla
        new_bullet = None
        reset_requested = False

        try:
            game_data = n.send(send_data)
            player_info = game_data[player_id]
            other_info = game_data[1 - player_id]
            meteors = game_data["meteors"]
            game_active = game_data["game_active"]
            countdown = game_data["countdown"]
            countdown_time = game_data["countdown_time"]
            game_over = game_data["game_over"]
            winner = game_data["winner"]
            time_left = game_data["time_left"]
            
            # Mermi ve cephane bilgilerini sunucudan güncelle
            bullets = player_info["bullets"]
        except Exception as e:
            print("Bağlantı hatası!", e)
            break
        
        # Tuş girişleri sadece oyun aktifse ve oyun bitmemişse işlenir
        if game_active and not game_over:
            keys = pygame.key.get_pressed()
            
            if player_id == 0:  # Sol oyuncu
                if keys[pygame.K_LEFT] and pos[0] > 0:
                    pos[0] -= PLAYER_SPEED
                if keys[pygame.K_RIGHT] and pos[0] < (WIDTH // 2) - PLAYER_WIDTH:
                    pos[0] += PLAYER_SPEED
            else:  # Sağ oyuncu
                if keys[pygame.K_LEFT] and pos[0] > WIDTH // 2:
                    pos[0] -= PLAYER_SPEED
                if keys[pygame.K_RIGHT] and pos[0] < WIDTH - PLAYER_WIDTH:
                    pos[0] += PLAYER_SPEED

            # Yukarı/aşağı hareket
            if keys[pygame.K_UP] and pos[1] > 0:
                pos[1] -= PLAYER_SPEED
            if keys[pygame.K_DOWN] and pos[1] < HEIGHT - PLAYER_HEIGHT:
                pos[1] += PLAYER_SPEED
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # Oyun aktifse ve bitmemişse ateş et
                if event.key == pygame.K_SPACE and game_active and not game_over and player_info["ammo"] > 0:
                    new_bullet = [pos[0] + PLAYER_WIDTH // 2, pos[1]]
                
                # Oyun bittiyse yeniden başlat
                if event.key == pygame.K_RETURN and game_over:
                    reset_requested = True

        # Mermileri yukarı taşı
        for b in bullets[:]:
            b[1] -= BULLET_SPEED
            if b[1] < 0:
                bullets.remove(b)

        draw_window(player_info, other_info, meteors, player_id, game_active, countdown, countdown_time, game_over, winner, time_left)

    pygame.quit()

if __name__ == "__main__":
    main()