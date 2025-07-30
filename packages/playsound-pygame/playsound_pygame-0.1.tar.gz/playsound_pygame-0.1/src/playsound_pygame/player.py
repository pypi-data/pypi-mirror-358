import pygame

def playsound_pygame(soundfile):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.init()

    sound = pygame.mixer.Sound(soundfile)
    sound.play()

    while pygame.mixer.get_busy():
        pygame.time.delay(100)
