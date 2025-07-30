<h1 align="center">My Output</h1>
<h3 align="center">An aesthetic replacement to print()</h3>

<hr>

<h6 align="center"><b>Development Status:</b> Early Development</h6>
<p align="center">
  <a href="https://pypi.org/project/myoutput/">
	<img src="https://img.shields.io/pypi/v/colour?color=0f8fa3&label=PyPI&logo=python&logoColor=white&style=plastic" alt="PyPI">
  </a>
</p>

## About
MyOutput is a Python package that enables users to customize the appearance of standard output (print) and input prompts in the terminal.
Currently, the available customization options include coloured text and additional linebreaks.

Supported colours:
- black
- red
- green
- yellow
- blue
- magenta
- cyan
- white

and their brighter version with the prefix bright and an underscore (ex. bright_black).

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install MyOutput.

```python
pip install myoutput
```

## Usage
```python
import myoutput

# set print output to yellow
myoutput.set_print_colour("yellow")
print("Hello!")  # Output: (yellow text) Hello!

# set input prompts to red
myoutput.set_input_colour("red")
input("Enter your name: ")  # Prompt appears in red

# return current print output colour
print(myoutput.get_print_colour())  # Output: yellow

# return current input prompt colour
print(myoutput.get_input_colour())  # Output: red

# enable additional linebreak after each print
myoutput.set_linebreak(True)
print("Linebreak test")  # Output: (yellow text, with extra linebreak before)

# restore the original print and input function
myoutput.restore_output()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit)