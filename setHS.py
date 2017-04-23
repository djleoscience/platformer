#brief file to reset high score

x = int(input("What do you want the new high score to be? "))
f = open("highscore.txt", 'w')
f.write(str(x))
f.close()



f = open("highscore.txt", 'r')
print(f.read())
f.close()
