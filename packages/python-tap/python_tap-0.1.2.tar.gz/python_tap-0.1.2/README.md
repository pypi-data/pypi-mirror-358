# Python Tap

A tool for REPL Driven Development.


## What is Python Tap?
Python Tap is used during development and when running code.
With this tool, you can store and process data such as function input parameters
or local variables. This is very useful when inspecting code and flows, and when
running code in a REPL. You will have all the _tapped_ data available in the session.

>It is closely related to the variables available when debugging, but you have the data available from anywhere in the code base.

You can use Python Tap when running code in debug mode too.

Python Tap itself, doesn't do any processing of data, but the functions you add to the `tap` does that.
Included in this library, there are default taps. You can also write your own, or add
any existing function accepting _*args_ and _**kwargs_ (such as a _logger_).

You decorate functions, or call the `tap` function directly.
The `tap` function will run the added _taps_ (functions) with the input to the target function.

> This library heavily inspired by the `tap>` feature in Clojure.

## Usage

``` python
from python_tap import tap


@tap
def my_function(message: str, data: dict):
    ...
    
    
my_function("hello world", {"key": "value"})
```

Python Tap will not do anything until adding a function to the `tap` storage. Let's do that.

``` python
import python_tap


# this is an example tap function
def print_data(*args, **kwargs):
    print(f"{args} {kwargs}")


# Add your function(s) to the tap storage
python_tap.add(print_data)

```

``` python
my_function("hello world", {"key": "value"})
```

The output:

``` shell
('hello world', {'key': 'value'}) {'tap_fn': <function my_function at 0x103d4d940>}
```

Adding the included _data storage_ tap, to be able to work with the input data at anytime in the REPL session.

``` python
from python_tap import taps


python_tap.add(taps.params.store)
```

Run the `my_function` again. This tap doesn't print anything, but it has stored all data.

``` python
# get the stored data from the function
tapped = taps.params.get(my_function)

# or get all stored data from all decorated functions
tapped = taps.params.get_all()


print(tapped["message"]) # will print the string "hello world"
print(tapped["data"]) # will print the dictionary {'key': 'value'}

```

Removing taps:

``` python
# Remove a single tap, i.e. the tap function
python_tap.remove(print_data)

# Or, remove all taps
python_tap.remove()
```
