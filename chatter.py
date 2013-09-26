import os
import shutil
import commands
import time
import copy
from datetime import datetime
import subprocess

def respond( message, sender=""):
    message = message.strip()
    print "Got message",message
    message = message.lower()
    words = message.split()
    hasPlease = False
    
    answer = 0
    now = datetime.now()

    if "what time is it" in message:
        answer = "The current time is " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
    
    if "what is the date" in message:
        answer = "Today's date is " + str(now.month)+"/"+str(now.day)+"/"+str(now.year)

    #WORK ON THIS -----------------------
    if "execute uptime" in message:
        fp = subprocess.Popen(['uptime'], stdout=subprocess.PIPE, shell=True)
        answer = fp.stdout.read()
        (out, err) = fp.communicate()
        fp.stdout.close()


    #WORK ON THIS -----------------------
    if "execute ls" in message:
        fp = subprocess.Popen(['ls'], stdout=subprocess.PIPE, shell=True)
        answer = fp.stdout.read()
        (out, err) = fp.communicate()
        fp.stdout.close()

    
    if "jerry" in message or "jerry wei" in message:
        answer = "OMG YOU SAID MY NAME!"
        
    for i, word in enumerate(words):
        if word == "please" or words[-1] == "please":
            hasPlease = True;
        
        if word == "open":
            try:
                myFile = open(words[i+1], "r+")
                answer = myFile.read()
                myFile.close()
            except IOError:
                answer = "Hey man, there was no file like that there!"

        #WORK ON THIS -----------------------
        if word == "execute" and words[i+1] == "ping":
            IP = words[i+2]
            fp = subprocess.Popen(['ping -c 2 ' + IP], stdout=subprocess.PIPE, shell=True)
            answer = fp.stdout.read()
            (out, err) = fp.communicate()
            fp.stdout.close()

        if word == "credits":
            answer = "jerry wei"

        try:
            if (word == "what") and ("time is it" not in message) and ("is the value of" not in message) and ("is the date" not in message):
                answer = "What's up with the Montreal weather?"
        except IndexError:
            answer = "What's cookin'?"

        if word == "what" and words[i+1] == "is" and words[i+2] == "the" and words[i+3] == "value" and words[i+4] == "of":
            try:
                value = eval(words[i+5])
                answer = "The answer is " + str(value)
            except (ValueError, TypeError) as e:
                answer = "Dude you might want to try typing in the right equation without spaces"
            
        if word == "how":
            answer = "How is Cong Yu going to mark all these assignments in time?"

        if word == "piglatin":
            pyg = 'ay'
    
            original = words[i+1]
            original = original.lower()
            first = original[0]
    
            if len(original) > 0 and original.isalpha():
                if first == "a" or first == "e" or first == "i" or first == "o" or first == "u":
                    answer = original + pyg
                else:
                    answer = original[1:] + first + pyg
            else:
                answer = "There appears to be an error! Try again!"

        if word == "help":
            answer = "the commands available are: open x, execute uptime, execute ls, execute ping IP, what is the date, and piglatin (1 word), what time is it, what is the value of X, credits, what *, how *, any string that has [jerry] in it, and help."
        elif answer == 0:
            answer = "That isn't a command! You should try using a command! Type [what is the date], [piglatin (1 word)] or [help] to see a list of commands!"

    if hasPlease == True:
        return "it's my pleasure! " + answer
    else:
        return answer
if __name__ == '__main__':
    respond("This is a test")
