\
![](https://img.shields.io/badge/pratical_for-cryptography_number_generation_and_unpredictability-blue) ![](https://img.shields.io/badge/secretrandom-v1.1rc1-orange)  

# secretrandom

## The combination of the **random** and the **secrets** module for unpredictable number generation

#### Includes:

*   Password & passcode generation for authentication.
*   Random number generation as the random module.
*   Powered with **⚡true optimization and unpredictability.⚡**

- - -

## Documentation guide

All functions:

*   `randpwd()` — Password generation
*   `randcode()` — Passcode and PIN generation
*   `randint()` — Random whole integer generation
*   `randflt()` — Random float generation
*   `choice()` — For random choices
*   `shuffle()` — For random shuffles

### `randpwd()`

Generates strong or weak passwords based on the length (1st argument) and the strength (2nd argument).

```

import secretrandom

password = secretrandom.randpwd(17, 'strong')
print(password) # Prints out strong password with 17 chars.
    
```

NOT RECOMMENDED! Generate weak passwords for examples.

```

password = secretrandom.randpwd(0, 'weak')
print(password) # Prints out weak password like Tran$f0rm3rsr0ck!
    
```

### `randcode()`

Generates passcodes or PINs based on the length as the only argument.

```

passcode = secretrandom.randcode(6)
print(passcode) # Prints out passcode with 6 integers
    
```

### `randint()`

Random whole integer generator starting from 1st arg to 2nd arg with steps (3rd arg)

```

random_num = secretrandom.randint(1, 4)
print(random_num) # Prints out a number between 1-4
    
```

## OR

```

random_num = secretrandom.randint(1, 6, 2)
print(random_num) # Prints out a number either 2, 4, or 6
    
```

### `randflt()`

Random float generator from 1st arg to 2nd arg

```

random_flt = secretrandom.randflt(1, 2)
print(random_flt) # Prints out random float from 1 to 2 (like 1.673)
    
```

### `choice()`

Chooses part of a list of values.

```

choice = secretrandom.choice('abcd')
print(choice) # Prints out what it chose (either a, b, c, or d)
    
```

### `And finally shuffle()`

Shuffles a list of values.

```

data = ['a', 'b', 'c', 'd']
secretrandom.shuffle(data)
print(data) # Shuffles the list of values.
    
```

Any questions? Email [here](mailto:albeback01@gmail.com?subject=Python%20library%20secretrandom%20question.)