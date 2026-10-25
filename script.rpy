

define mc = Character("Tony", color="#5B709D")
define butcher = Character("Shank", color="#473228")
define deer = Character("Doe", color="#7F4234")
define friend = Character("Vaelthir", color="#3F392D")

#Minigame setup:

init python:
    import mechanics
    import time

    def move_maze_player(direction):
        if not mechanics.maze_ready():
            return
        result = mechanics.move_player(direction)
        if result == "win":
            renpy.hide_screen("maze_screen")
            renpy.jump("after_maze")
        elif result == "wall":
            renpy.notify("*bumps into a wall*")
        elif result == "cobweb":
            renpy.notify("*gets stuck in a cobweb*")
        renpy.restart_interaction()

    def qte_begin():
        global qte_start
        global qte_active
        global qte_end
        mechanics.reset_qte()
        mechanics.new_qte()
        qte_end = ""
        qte_start = time.time()
        qte_active = True
        renpy.show_screen("qte_screen")

    def qte_advance(key):
        global qte_start
        global qte_active
        global qte_end
        if qte_active == False:
            return
        result = mechanics.resolve_qte(key, qte_start)
        messages = {
            "dodged": "Dodged!",
            "hurt": "Ouch! -1 HP",
            "hit": "Hit! Ogre -1 HP",
            "missed": "Missed!"}
        renpy.notify(messages[result])
        state = mechanics.qte_state()
        if state != "continue":
            qte_active = False
            if state == "win":
                qte_end = "ogre"
            else:
                qte_end = "player"
            renpy.restart_interaction()
            return
        mechanics.new_qte()
        qte_start = time.time()
        renpy.hide_screen("qte_screen")
        renpy.show_screen("qte_screen")
        renpy.restart_interaction()

    def qte_finish():
        global qte_end
        winner_is_player = (qte_end == "ogre")
        qte_end = ""
        renpy.hide_screen("qte_screen")
        if winner_is_player:
            renpy.jump("QTE_success")
        else:
            renpy.jump("QTE_fail")

    def qte_press(key):
        qte_advance(key)

    def qte_timeout():
        qte_advance(None)

    def fox_tick_screen():
        mechanics.fox_tick()
        renpy.restart_interaction()

    def fox_whack(index):
        result = mechanics.whack(index)
        if result == "miss":
            renpy.notify("*miss*")
        elif result == "hit" and mechanics.check_foxes():
            fox_end()
        renpy.restart_interaction()

    def fox_end():
        renpy.hide_screen("fox_screen")
        if mechanics.check_foxes():
            renpy.jump("fox_success")
        else:
            renpy.jump("fox_fail")
    

#Variables:

define TILE = 60
define GRASS = "#4f9a3a"
default qte_start = 0.0
default qte_active = False
default qte_end = ""
define FOX_SIZE = int(config.screen_height * 0.24)

transform fade_away:
    alpha 1.0
    pause 0.3
    linear 1.2 alpha 0.0

transform oh_no:
    zoom 0.2
    linear 0.12 zoom 1.2
    linear 0.08 zoom 1.0

#Screens:

screen maze_screen():
    modal True
    key "K_UP" action Function(move_maze_player, "u")
    key "K_w" action Function(move_maze_player, "u")
    key "K_DOWN" action Function(move_maze_player, "d")
    key "K_s" action Function(move_maze_player, "d")
    key "K_LEFT" action Function(move_maze_player, "l")
    key "K_a" action Function(move_maze_player, "l")
    key "K_RIGHT" action Function(move_maze_player, "r")
    key "K_d" action Function(move_maze_player, "r")
    frame:
        align (0.5, 0.5)
        background Solid("#2b2b2b")
        padding (6, 6)
        grid 10 10:
            spacing 0
            for row in mechanics.get_maze():
                for spot in row:
                    fixed:
                        xysize (TILE, TILE)
                        add Solid("#2b2b2b")
                        if spot == "W":
                            add Transform("assets/wall.png", size=(TILE, TILE))
                        elif spot == "C":
                            add Transform("assets/cobweb.png", size=(TILE, TILE))
                        elif spot == "X":
                            add Transform("assets/item.png", size=(TILE, TILE))
                        elif spot == "P":
                            add Transform("assets/player.png", size=(TILE, TILE))
    text "Arrow keys/WASD to move" align (0.5, 0.97) size 22 color "#e8e8e8"

screen qte_screen():
    modal True
    zorder 100
    add Solid(GRASS)
    if qte_end == "":
        timer mechanics.get_qte_time() action Function(qte_timeout)
        for k in mechanics.QTE_KEYS.values():
            key ("K_" + k) action Function(qte_press, k)
        vbox:
            align (0.5, 0.12)
            spacing 10
            text "[mechanics.get_qte_prompt()]" size 64 xalign 0.5 color "#ffffff" outlines [(3, "#000000", 0, 0)]
            text "Press [mechanics.get_qte_key()!u]!" size 48 xalign 0.5 color "#ffffff" outlines [(3, "#000000", 0, 0)]
            bar:
                xalign 0.5
                xsize 320
                ysize 10
                thumb None
                left_bar Solid("#ffffff")
                right_bar Solid("#00000066")
                value AnimatedValue(value=0, range=mechanics.get_qte_time(), delay=mechanics.get_qte_time(), old_value=mechanics.get_qte_time())
    else:
        timer 1.8 action Function(qte_finish)

    # Player on the left
    vbox:
        xalign 0.12
        yalign 0.65
        spacing 12
        fixed:
            xysize (260, 260)
            xalign 0.5
            if qte_end == "player":
                add "assets/player.png" fit "contain" xysize (260, 260) at fade_away
            else:
                add "assets/player.png" fit "contain" xysize (260, 260)
        text "You" size 30 xalign 0.5 color "#ffffff" outlines [(2, "#000000", 0, 0)]
        bar:
            xsize 260
            ysize 24
            thumb None
            left_bar Solid("#3ddc5a")
            right_bar Solid("#00000088")
            value StaticValue(mechanics.get_player_hp(), mechanics.QTE_PLAYER_HP)
        text "HP: [mechanics.get_player_hp()] / [mechanics.QTE_PLAYER_HP]" size 26 xalign 0.5 color "#ffffff" outlines [(2, "#000000", 0, 0)]

    # Ogre on the right
    vbox:
        xalign 0.88
        yalign 0.65
        spacing 12
        fixed:
            xysize (260, 260)
            xalign 0.5
            if qte_end == "ogre":
                add "assets/ogre.png" fit "contain" xysize (260, 260) at fade_away
            else:
                add "assets/ogre.png" fit "contain" xysize (260, 260)
            if qte_end == "" and mechanics.get_qte_prompt() == "Dodge!":
                add "assets/exclamation.png" fit "contain" xysize (70, 70) xalign 0.5 ypos 0 yanchor 1.0 at oh_no
        text "Ogre" size 30 xalign 0.5 color "#ffffff" outlines [(2, "#000000", 0, 0)]
        bar:
            xsize 260
            ysize 24
            thumb None
            left_bar Solid("#e04040")
            right_bar Solid("#00000088")
            value StaticValue(mechanics.get_ogre_hp(), mechanics.QTE_OGRE_HP)
        text "HP: [mechanics.get_ogre_hp()] / [mechanics.QTE_OGRE_HP]" size 26 xalign 0.5 color "#ffffff" outlines [(2, "#000000", 0, 0)]

screen fox_screen():
    modal True
    add Solid(GRASS)
    timer mechanics.FOX_TICK repeat True action Function(fox_tick_screen)
    timer mechanics.FOX_ROUND_TIME action Function(fox_end)
    frame:
        align (0.5, 0.45)
        background None
        grid 3 3:
            spacing 10
            for i, cell in enumerate(mechanics.get_foxes()):
                if cell == "F":
                    imagebutton:
                        idle Transform("assets/fox_hole.png", size=(FOX_SIZE, FOX_SIZE))
                        action Function(fox_whack, i)
                else:
                    imagebutton:
                        idle Transform("assets/hole.png", size=(FOX_SIZE, FOX_SIZE))
                        action Function(fox_whack, i)
    text "Hits: [mechanics.get_fox_score()] / [mechanics.FOX_TARGET]" align (0.5, 0.94) size 32 color "#ffffff" outlines [(2, "#000000", 0, 0)]

#The story:

label start:
    scene bg bedroom
    with fade
    "{font=fonts/OpenSans-Italic.ttf}My eyes flutter open instinctively, only to regret my decision a few mere seconds later as the morning sun's rays blind me.{/font}"
    mc "Aughh, I hate mornings..."
    "{font=fonts/OpenSans-Italic.ttf}I rub my eyes in an attempt to wake up, proceeding to see the same old ceiling I see daily.{/font}"

    scene bg mirror
    with fade
    "{font=fonts/OpenSans-Italic.ttf}After dragging myself out of bed and brushing my teeth, I begin to get ready for the day.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}Looking around the room for my clothes, I catch a glance of the short figure in the mirror staring back at me.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}I've always resented my short stature since it served me no purpose, only bringing me shame and inconvenience.{/font}"

    scene bg town
    with fade
    "{font=fonts/OpenSans-Italic.ttf}I headed out on a walk around town, looking forward to getting my errands over with as soon as possible.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}Stopping by the butcher's shop first to grab a slice of my favourite meat.{/font}"

    scene bg butchers_shop
    with fade
    show butcher normal:
        xalign 0.8
    show tony normal:
        xalign 0.2
    "{font=fonts/OpenSans-Italic.ttf}As I approach the thick-bearded Mr. Shank, I notice the worried expression on his rather wrinkled face.{/font}"
    mc "Mr. Shank, are you alright? You don't seem quite good today."
    butcher "Oh good! I'm glad you're here, Tiny Tony, I need your help urgently."
    hide tony normal
    show tony uncomfortable:
        xalign 0.2
    "{font=fonts/OpenSans-Italic.ttf}Oh god, not again...I'm not the biggest fan of that nickname.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}But I know deep inside Mr. Shank's just trying to lighten the mood, even if it means making fun of my height.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}I wonder what he needs this time around?{/font}"
    mc "No worries Mr. Shank, your saviour has arrived. What is it that you need my help with?"
    butcher "Thank you young lad!"
    butcher "A sneaky fox made its way to my table and stole the chub of meat I was about to slice."
    butcher "That's my best seller! Please tell me you'll chase after that fox and swipe my meat back from that lil' swiper.."
    "{font=fonts/OpenSans-Italic.ttf}I let out a soft sigh. It's too early for these shenanigans..but I really need that meat too.{/font}"
    mc "Sure Mr. Shank. Just give me a moment yeah?"

    scene black
    with fade
    "{font=fonts/OpenSans-Italic.ttf}The fox's burrows are scattered across the field. Every time it pops its head up, I have to grab my chance!{/font}"

label start_fox:
    window hide
    $ mechanics.reset_foxes()
    $ mechanics.fox_tick()
    show screen fox_screen
    $ renpy.pause(hard=True)

label fox_success:

    "{font=fonts/OpenSans-Italic.ttf}Got it! I snatch the meat right out of the fox's jaws.{/font}"
    jump after_fox

label fox_fail:
    "{font=fonts/OpenSans-Italic.ttf}The fox is too quick and slips away. Let's try that again...{/font}"
    jump start_fox

label after_fox:
    scene bg butchers_shop
    with fade
    show tony happy:
        xalign 0.2
    show butcher happy:
        xalign 0.8
    "{font=fonts/OpenSans-Italic.ttf}I slam the ginormous cut of meat onto Mr. Shank's countertop.{/font}"
    mc "Here you go sir."
    butcher "Thank you so much, Tiny Tony!!"
    mc "No problem, Mr. Shank."
    "{font=fonts/OpenSans-Italic.ttf}I say as I wipe the sweat beading onto my forehead.{/font}"
    butcher "No seriously kid.. you saved me from a lot of trouble."
    butcher "How about this time around, your cut of meat is on me? Consider it a thank you gift."
    mc "No no sir, I cannot bring myself to accept that, I was just passing by and it was no biggie."
    butcher "I'm not taking no for an answer son, I insist. I'm glad to have you as a loyal customer."
    mc "Alright Mr. Shank. Thank you so much!!"
    butcher "Haha, no worries child. Now off you go."

    scene bg town
    with fade
    show tony happy
    "{font=fonts/OpenSans-Italic.ttf}Woah, I wasn't expecting free meat as a reward for chasing after critters. Not too shabby.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}As I'm skipping around with glee, I head to my next stop for the day; the fruit stand.{/font}"

    scene bg fruit stand
    with fade
    show doe scared:
        xalign 0.8
    show tony normal:
        xalign 0.2
    mc "Hello, Little Doe! How're you doing today?"
    deer "Horrible, absolutely horrible!"
    deer "Please help me! An ogre stole all my produce! I spent a week collecting all that for sale."
    deer "My rent's due in a week, and my mom can't afford it without my money from running this stall.."
    deer "Please help me get it back!"
    "{font=fonts/OpenSans-Italic.ttf}She begs with a pitiful expression on her face and tears welling up in her eyes. My heart sinks for her.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}Unable to say no, I put my stuff down near her stand.{/font}"
    hide doe scared
    show doe normal:
        xalign 0.8
    mc "Don't worry Doe, I'll help you get your stuff back in a jiffy."
    scene black
    with fade
    "{font=fonts/OpenSans-Italic.ttf}I track the ogre down in a clearing. He's huge, and he's not happy to see me. Time to dodge his swings and strike back!{/font}"

label start_qte:
    window hide
    $ qte_begin()
    $ renpy.pause(hard=True)

label QTE_success:
    "{font=fonts/OpenSans-Italic.ttf}The ogre crumples to the ground, and I grab the basket of produce.{/font}"
    jump after_qte

label QTE_fail:
    "{font=fonts/OpenSans-Italic.ttf}The ogre knocks me flat. I pick myself up and square off again...{/font}"
    jump start_qte

label after_qte:
    scene bg fruit stand
    with fade
    show tony happy:
        xalign 0.2
    show doe happy:
        xalign 0.8
    "{font=fonts/OpenSans-Italic.ttf}I return to the shop and hand over the basket of fruits to the young girl.{/font}"
    deer "Thank you so much, Mr. Tony!! I'll make sure to compensate for your troubles."
    "{font=fonts/OpenSans-Italic.ttf}She rewards me with a fresh batch of the ripest fruits she had to offer, at cost price. I made sure to pay her extra in the form of tips.{/font}"
    #fourth scene
    scene bg forest
    with fade
    show tony happy:
        xalign 0.2
    "{font=fonts/OpenSans-Italic.ttf}My mood skyrocketed seeing all the smiling faces around me. It feels good being able to help all those around me.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}As I make my way out of town towards the flower fields, I'm brought to a sudden halt as I bump into someone-{/font}"
    "{font=fonts/OpenSans-Italic.ttf}..my best friend, Vaelthir.{/font}"
    show vaelthir upset:
        xalign 0.8
    friend "Thank the heavens! Just the person I needed."
    friend "Tony, you've got to help me get my stuff from underneath the gardener's shed, I tried to get it myself but I'm far too large to slide under it and-"
    "{font=fonts/OpenSans-Italic.ttf}I stop him in the midst of his words.{/font}"
    hide vaelthir upset
    show vaelthir normal:
        xalign 0.8
    mc "Don't even worry about it, I've got you buddy."
    scene black
    with fade
    "{font=fonts/OpenSans-Italic.ttf}I squeeze under the gardener's shed. It's dark, cramped and full of cobwebs. Time to find Vaelthir's stuff!{/font}"

label start_maze:
    window hide
    $ mechanics.reset_maze()
    call screen maze_screen

label after_maze:
    scene bg end_cutscene
    with fade
    "{font=fonts/OpenSans-Italic.ttf}After returning Vaelthir's stuff to him, we sat down on a nearby bench to enjoy the sunset while munching on the fruits I got earlier.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}We took this opportunity to catch up, as it had been quite a while since we last got time together like this.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}As we talked on, I looked back on my day, reminiscing about all the ways I helped others today.{/font}"
    "{font=fonts/OpenSans-Italic.ttf}Looking out beyond the sunset's horizon, a wide smile formed on my face.{/font}"
    mc "I'm starting to realize something, Vaelthir..."
    mc "I'm just a little guy, but maybe it isn't so bad."
    return