from numpy import random as r

def run():
    enemy_hp=200
    self_hp=200
    while enemy_hp>0 and self_hp>0:
        edam=0
        sdam=0
        action = raw_input('what do you want? punch, nothing, shoot, knife, or the bomb?:      ')
        print ""
        if action=='punch':
            x=r.rand()
            if x<0.3:
                edam=r.rand()*10+10
                print "You kicked the enemy with your fist for", edam , "damage."
            elif x < 0.6:
                edam= r.rand()*20+5
                sdam= r.rand()*5+5
                print "you tried to punch your opponent, but tackled him instead."
                print "you did", edam, "damage and took", sdam, "damage."
            else:
                sdam = 12.875+8*r.rand()
                print "You mistook your opponent as yourself and kicked your own face"
                print "You did", sdam, "damage to yourself."
        elif action=='nothing':
            print 'You did nothing.'
            print 'Nothing happened'
        elif action=='shoot':
            x=r.rand()
            if x<0.2:
                edam=r.rand()*10+25
                print "You riddled the enemy with bullets for", edam , "damage."
            elif x < 0.4:
                edam= r.rand()*5+5
                sdam= r.rand()*5+5
                print "you took a picture with him."
                print "you did", edam, "damage and took", sdam, "damage."
            elif x<0.6:
                sdam = 30+17.5*r.rand()
                print "You tried to shoot your enemy, but the gun didn't work."
                print 'You looked down the barrel, and pressed the trigger. It worked that time.'
                print "You did", sdam, "damage to yourself."
            elif x<0.7:
                edam = 10 + 15*r.rand()
                print "You shot him with a water gun and did", edam, "damage."
            else:
                print "No, you are supposed to shoot your enemy, not a tree stump."
        elif action == 'knife':
            x=r.rand()
            if x<0.5:
                edam=r.rand()*20+10
                print "You stabbed him in the face for", edam , "damage."
            elif x < 0.6:
                edam= r.rand()*10+15
                sdam= r.rand()*10+25
                print "you charged at him with a two-sided knife. The side that pointed toward you was sharper."
                print "you did", edam, "damage and took", sdam, "damage."
            elif x<0.7:
                sdam = 25+10*r.rand()
                print "You charged at him with a two-sided knife."
                print 'The side that pointed toward him broke.'
                print "You did", sdam, "damage to yourself."
            elif x<0.8:
                sdam = 15 + 85*r.rand()
                print "You stabbed yourself, multiple times. It was much easier than stabbing your opponent. Sorry, you didn't specify a target."
                print "You took", sdam, "damage."
            else:
                print "You threw the knife at him. He tossed it back to you."
        elif action == 'the bomb':
            x=r.rand()
            if x<0.2:
                edam=r.rand()*100+20
                print "You strapped him to the bomb. It exploded and did", edam , "damage."
            elif x < 0.4:
                edam= r.rand()*6+4
                sdam= r.rand()*20+60
                print "you ate the bomb. It exploded, and the shock struck him."
                print "you did", edam, "damage and took", sdam, "damage."
            elif x<0.6:
                edam = 30+120*r.rand()
                print "You shoved the bomb down his throat."
                print "You did", edam, "damage."
            elif x<0.8:
                sdam = 50 + 75*r.rand()
                print "You gave the bomb to him. He gave it back to you."
                print "You took", sdam, "damage."
            else:
                sdam = 15 + 14*r.rand()
                print "You tried to play baseball with the bomb. Bad idea." 
                print "You took", sdam, "damage."
        enemy_hp=enemy_hp-edam
        self_hp=self_hp-sdam
        print "enemy health:", enemy_hp
        print "self health:", self_hp
        print ''
        x=None
        if enemy_hp<0 and self_hp<0: 
            if enemy_hp<self_hp: x=1
            elif self_hp<enemy_hp: x=-1
            else:
                x= 0
        elif enemy_hp<0: x= 1
        elif self_hp<0: x= -1
        if x==-1:
            print "You LOSE!"
        elif x==1:
            print "You WON!"
        elif x==0:
            print "you SOMEHOW tied."

