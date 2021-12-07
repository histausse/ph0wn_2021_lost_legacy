# Lost Legacy

This is a CTF from [ph0wn](https://ph0wn.org/) 2021.

Thanks to the team at ph0wn for the great CTF!

## Subject: 

```
Pico the Croco has dug an old floppy disk of one of his first hacks, when he managed to infiltrate an authentification system. The small authenticator program (its size is 3 records only...) is still there along with the Id database (only 5 records), but unfortunately the system disk has faded up.

Hopefully there are emulators and archives on the net that will allow him to run the program again, but now the program asks him for an id and a password, and Pico doesn't fully remember his own id (and don't ask him for his password, that's more than 35 years old after all).

Yet, Pico remembers Niklaus Wirth was recognized by the authentication system, and that Pr. Wirth never hid his password ("Oberon is as simple as possible"). Of course the authenticator has all the ids, passwords and greetings in the greetings file, but they are all encrypted. That's too bad because there's a first flag for you in his greeting, and even a second flag in Pico's password (really? wow, that sounds like an anomaly in space-time continuum...).

Pico would gladly accept help from Martin Odersky or Peter Sollich, but these guys are way too busy now, so will you help him and catch these flags ? It's time to reverse that M-Code, in every sense...

Flags: There are 2 flags to find for this challenge, 1 for "Lost Legacy 1" and 1 for "Lost Legacy 2". You should normally find the first flag (for "Lost Legacy 1") before the second, but it is not totally impossible you find them in a different order. If this is the case and you find a valid flag but it is "not valid", try it on "Lost Legacy 2" (or reciprocally).
```

This challenge provides us with a `.sym`, a `.cmd` and a `database.bin`. 

Obviously, `file` does not recognize the format:

```
$ file greet.mcd
greet.mcd: DOS 2.0 backup id file, sequence 1
$ file greet.sym
greet.sym: data
$ file database.bin
database.bin: data
```

The instructions give us a few names an mention Oberon (I'm still not sure if it is a language, an OS, or both).

After some research arround the subject (and a big hint on the discord :eyes:), I arrived to the conclusion that the `.sym` is bytecode from Modula 2.

More research on Modula brought me to this github user: [Oric4ever](https://github.com/Oric4ever).

## Run the program:

First, he have a emulator to run this program on linux:

```
git clone https://github.com/Oric4ever/Turbo-Modula-2-Reloaded.git
cd Turbo-Modula-2-Reloaded/vm_linux
make
cp ../m2.dsk image.dsk
sudo mount -o loop ./image.dsk /mnt
sudo mkdir /mnt/EXAMPLES.DIR/PHOWN.DIR
sudo cp ../../greet.* /mnt/EXAMPLES.DIR/PHOWN.DIR/
sudo cp ../../database.bin /mnt/EXAMPLES.DIR/PHOWN.DIR/
./m2  # start the emulator
cd examples
cd phown
greet # start the program
```

Let's test `greet.mcd` to see if it works. Try the given credentials:

```
Id : Niklaus Wirth
Pwd: Oberon is as simple as possible
Access granted...
Much respect, Professor, dear author of Pascal, Modula(-2), Oberon...
```

It works!

## Reverse

Now, we need a way to analyse the code. Once again, Oric4ever saves us by providing a dissassembler:

```
git clone https://github.com/Oric4ever/Reversing-Turbo-Modula2.git
cd Reversing-Turbo-Modula2
gcc unassemble.c -o unassemble
./unassemble ../greet.mcd
```

It takes a minute to get used to the syntax. The main point is the use of the stack for everything. Some functions/instructions are not really clear on what they take as argmument, but on the whole, it is readable.

There are 3 main procedures: `proc2` is the main function, `proc1` takes an array as argument and cipher it in place, `proc3` takes a byte in input and returns a byte. `proc2` maps its input with `proc3`. For more details on `proc1` and `proc3`, see the equivalent code in `cipher.py`

### Patching

In `proc2`, we can see that the program decipher the greeting message from the database when the access is granted. Let's try to trick it to display a message without having the password.

Here is the line (`00d0`) that check if the access is granted:

```
00cf  27        load local word-7                   # <-- word-7 = access granted
00d0  e3 20     jpfalse 00f2
00d2  8c 0a  .. load immediate string "granted..."
```

Reminder: the jump destination is given by an offset in the binary instruction: `0x00f2=0x00d2+0x20`.

If we replace the `20` by `0` in the binary, the jump will do nothing. Let's try that:

To patch the file, we can open `greet.mcd` with vim and use the command `:%!xxd` to get an hexa representation of the file. We just have to find the byte to modify and change it, but be carefull not to touch anything else (`xxd` is touchy, even replacing a space by another space can have strange results on the binary). When it's done, `:%!xxd -r` to get back the binary format, save the file, put it on the emulator, and:


```
# greet2
Id : plop
Pwd: plop
Access granted...
(Intergalactic) Digital Research, Inc. Welcome, CEO, greetings to Dorothy...
```

Patching works! But we can only get the greeting for the last user of the database.

Well, no probleme, let's patch a little more. Adding code in the middle of a binary is tricky, it might broke the program in a lot of ways, so it is better to replace existing code by new code. Good think the tests that check if the user and the password match take some place. We can override those (after all, who need authentication?). We want to read the greating message from the file, apply `proc1` to it, then print the result. Here is the code:

```
23        load local word-3
82 18     load stack address 24
8d 4f     load immediate 79
f1        call proc1    
23        load local word-3
82 18     load stack address 24
8d 4f     load immediate 79
f0 07     call TERMINAL.WriteString
f0 06     call TERMINAL.WriteLn

27        load local word-7 # to override the test after this code
27        load local word-7
27        load local word-7
27        load local word-7
```

We add `27` at the end to finish overiding the previous code. `nop` instructions would do the job, but I'm too lazzy to look for the right op-code. Loading `word-7` to the stack is harmless and do the job.

Here is the diff in the binary:


```
000000b0: de02 27b6 e31d 2223 8d3f f01b 2423 8d10  ..'..."#.?..$#..
000000c0: 8d10 c4a0 de0a 2523 8208 8d20 8d20 c4a0  ......%#... . ..
000000d0: 37e4 278c 0741 6363 6573 7320 96f0 0727  7.'..Access ...'
```

```
000000b0: de02 27b6 e31d 2223 8d3f f01b 2382 188d  ..'..."#.?..#...
000000c0: 4ff1 2382 188d 4ff0 07f0 0627 2727 2727  O.#...O..'''''''
000000d0: 37e4 278c 0741 6363 6573 7320 96f0 0727  7.'..Access ...'
```

```
# greet
Id : histausse
Pwd: lik3sPl4typ0des
Much respect, Professor, dear author of Pascal, Modula(-2), Oberon...
Greetings to a Turbo Modula-2 author! We will miss Borland...
Welcome to a Turbo Modula-2 author! and congrats for Scala!
YES!!! Ph0wn{Pico hack3d this place!} Greetings to Axelle & Ludo...
(Intergalactic) Digital Research, Inc. Welcome, CEO, greetings to Dorothy...
Access denied.
```

We could try the same approche to print passwords, but sadly, the program compares the ciphered version of the IDs/Pwds in input with the already ciphered version from the database.

We could continue to do crazy stuff by patching the programe: for instance, `proc1` is likely to be a bijection, so applying `proc1` to the cipher text enought times will endup deciphering the text. But its not worth it.

Relevent XKCD: https://xkcd.com/378

### Reversing and breaking the encryption procedure

`proc1` can be translated by:

```python
def proc1(leng:int, s:str):
    for w2 in range(leng):
		w3 = s[w2]
		s[w2] = proc3(w2+s[w2])
```

And `proc3` by:

```python
def proc3(a:int)->int:
    w3 = 1
	w2 = 1
	w4 = a & 255
	while (w2 <= w4):
		w3 *= 3
		while (w3 > 256):
			w3 -= 257
		w2 += 1
    return w3 & 255
```

There is an usable version of those functions in `cipher.py`. Let's test it:

```
$ python cipher.py "Niklaus Wirth"
0x9d
0xd
0x5e
0x4b
0xc9
0x99
0x33
0xa0
0x57
0xe2
0x5c
0xab
0xeb
$ xxd database.bin | head -n 1
00000000: 9d0d 5e4b c999 33a0 57e2 5cab eb98 0000  ..^K..3.W.\.....
```

As you can see, we get back the ciphered version of `"Niklaus Wirth"` found in the database.

Now, let's break it.

We have a small problem: we have to find the number of time a loop is executed. We will have to do the hypothesis that `w2 > (a & 255)` is equivalent to `(w3 & 255) == proc3(a)`. From this hypothesis, it is not too hard to write a `decipher` function:

```python
def decipher(l:list[int])->str:
    values = []
    for i, c in enumerate(l):
        w3 = 1
        w2 = 0 # There is a small off by one :)
        while (w3 & 255) != c:
            w3 *= 3
            while (w3 > 256):
                w3 -= 257
            w2 += 1
        values.append(chr(w2-i))
    return "".join(values)
```

My problem now is that I'm not too sure about how the database is parsed. It looks alligned enought, so in doubt, I will decipher every chunks of `32` bytes alligned to `16` bytes:

```python
def read_database():
    with open("database.bin", "br") as db:
        for i in range(40):
            db.seek(i*16)
            chunk = db.read(32)
            try:
                print(decipher(chunk))
            except Exception as e:
                print(e)
```

Not very elegent, but good enough:

```
$ python decipher.py
Niklaus Wirthrq?RUb_^YcQccY]
Oberon is as simple as possible
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
FF!#Õ^~&6n¹k)ÒBÏ1L½
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
Turbo Modula-2qponmlkjihgfedcba
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
|MübW[ð®4]Å¿:
66]hKæZ¬Êß N
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
Scala4everutsrqponmlkjihgfedcba
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
!ÇÝæ¼Ç"ÌWçFwaxgÍâ>®\
chr() arg not in range(0x110000)
Pico le crocorq@X g^kD="XQS[c
Ph0wn{TM2 hacks NW's work!}dcba
^g70{1tsrq¤XÄ
             á Õt3l
©´hÔñ°£åC|ÉÜ(R°t{ã+ß¯É¹
Ù'ì8bÀó;£ï¿ÙÉ*ë!¼#t!¿®½
er9BU ¤/¤¾ÍÃnÒ'ß#
Ó~â(7ï3uIRe0´?Q³UwaxgÍâ>®\
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
Gates is nuts!qponmlkjihgfedcba
chr() arg not in range(0x110000)
Î9Ï ·=Ä)aîAy§ËG0·d¦
xÈ
U} VeÎtu±\K&
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
chr() arg not in range(0x110000)
```

Now, can see that `Pico le croco` uses the password `Ph0wn{TM2 hacks NW's work!}` :)

Just for fun:

```
# greet
Id : Pico le croco
Pwd: Ph0wn{TM2 hacks NW's work!}
Access granted...
YES!!! Ph0wn{Pico hack3d this place!} Greetings to Axelle & Ludo...
```
