import pygame

def handle_collisions(player, enemies, bullets):
    # Projectile → Enemy
    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, bullet_list in hits.items():
        enemy.health -= 15 * len(bullet_list)
        if enemy.health <= 0:
            enemy.kill()
            # TODO: add sound_enemy_death

    # Player → Enemy
    if pygame.sprite.spritecollide(player, enemies, False):
        player.health -= 10
        # TODO: add sound_player_hit
        if player.health <= 0:
            # TODO: add sound_player_death
            return "dead"

    return "alive"
