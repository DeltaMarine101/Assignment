import re
from tkinter import *
from Classes import *
from PIL import Image, ImageDraw, ImageTk


# Searches for brackets
def find_brackets(form):
    if '(' in form and ')' in form:
        for g, q in form:
            if q == ')':
                for j in range(g, -1, -1):
                    if form[j] == '(':
                        return [j, g]
    else:
        return False


def solve(form):

    try:
        # Convert float to fraction
        for j, q in form:
            if isinstance(q, Element):
                temp = q.new()
                if isinstance(temp.value, float):
                    den = 1
                    while temp.value % 1 != 0:
                        den *= 10
                        temp.value *= 10
                    form[j] = Fraction(temp, Element(den)).simplify()

        # Solve brackets ( and )
        while find_brackets(form):
            index = find_brackets(form)
            form = form[:index[0]] + [solve(form[index[0] + 1:index[1]])] + form[index[1] + 1:]

        # Find functions eg. sin, cos, tan
        temp_map = list(Function.functions_map.keys())
        while any((j in temp_map) for j in form):
            for h, q in form:
                if q in temp_map:
                    if not isinstance(form[h + 1], str):
                        form = form[:h] + [Function(form[h + 1], q).simplify()] + form[h + 2:]
                        break

        # Find powers
        while '^' in form:
            for h, q in form:
                if q == '^':
                    form = form[:h - 1] + [(form[h - 1] ** form[h + 1]).simplify()] + form[h + 2:]
                    break

        # Find times and divide
        while '*' in form or '/' in form:
            for h, q in form:
                if q == '*':
                    form = form[:h - 1] + [(form[h - 1] * form[h + 1]).simplify()] + form[h + 2:]
                    break
                if q == '/':
                    form = form[:h - 1] + [(form[h - 1] / form[h + 1]).simplify()] + form[h + 2:]
                    break

        # Find addition
        while '+' in form:
            for h, q in form:
                if q == '+':
                    form = form[:h - 1] + [(form[h - 1] + form[h + 1]).simplify()] + form[h + 2:]
                    break

        return form[0]

    except (ValueError, IndexError, ZeroDivisionError, TypeError, AttributeError):
        return 'Error'

# View control variables
radius = 150
zoom = 16.0
center = (0, 0)
graph_true = False

# Initialise GUI
root = Tk()
root.configure(background='#222')
root.wm_title('Calculator')
img = PhotoImage(file='resources/calc.png')
root.tk.call('wm', 'iconphoto', root._w, img)

graph = Frame(root, bg='#222')
graph.pack(side=RIGHT)

viewport = Canvas(graph, width=radius * 2 + 1, height=radius * 2 + 1, highlightthickness=2, highlightbackground="#444",
                  cursor='fleur')
viewport.configure(background='#222')
viewport.pack()

buttons = Frame(root, bg='#222')
buttons.pack()

textDisplay = Frame(buttons, height=4, width=43, bg='#222')
textDisplay.grid(row=0, column=0, columnspan=7)

textDisplay.grid_rowconfigure(1, pad=10)

answerOut = Text(textDisplay, font=('Arial', 14), height=1, width=25, fg='#FFF', bg='#222', borderwidth=0,
                 state="disabled")
answerOut.tag_config('right', justify=RIGHT)
answerOut.grid(column=0, row=0, pady=(15, 0))

formulaOut = Text(textDisplay, font=('Arial', 12), height=1, pady=2, padx=5, width=35, fg='#111',
                  bg='#EEE', borderwidth=0)
formulaOut.grid(column=0, row=1)


# Draw the cartesian plane
def draw_plane(color='#65c050'):
    viewport.delete("all")
    viewport.create_rectangle(radius + center[0] * zoom, 0, radius + center[0] * zoom, radius * 2 + 1, fill=color,
                              outline=color)
    viewport.create_rectangle(0, radius + center[1] * zoom, radius * 2 + 1, radius + center[1] * zoom, fill=color,
                              outline=color)

    # Draw scale numbers
    # Top
    viewport.create_text(radius + center[0] * zoom - 15, 8,
                         text=str(round((radius+zoom*center[1])/zoom, 2)), fill='#DDD')
    # Bottom
    viewport.create_text(radius + center[0] * zoom - 15, radius*2-5,
                         text=str(-round((radius-zoom*center[1])/zoom, 2)), fill='#DDD')
    # Left
    viewport.create_text(20, radius + center[1] * zoom-10,
                         text=str(-round((radius+zoom*center[0])/zoom, 2)), fill='#DDD')
    # Right
    viewport.create_text(radius*2-20, radius + center[1] * zoom-10,
                         text=str(round((radius-zoom*center[0])/zoom, 2)), fill='#DDD')


# Draw lines between the 2 points
def precision(x1, y1, x2, y2):
    y2 = round(float(y2), 10)
    viewport.create_line(round(x1 + radius), round(radius - y1), round(x2 + radius),
                         radius - y2, fill='#EEE')


draw_plane()

# Make global variables
formula = ''
prev_formula = ''
rendered = False
decimal_value = False

antialias_rendering = False

prevRendered = {}

pattern = re.compile("\s*(?:(-?(?:(?:\d+\.\d+)|(?:\d+)))|(" +
                     '|'.join(sorted(list(Function.functions_map.keys()), reverse=True)) +
                     "|\()|(\+|\-|\*|/|\^|\))|(.))")


# Compile formula into an object
def create_object():
    global formula, prevRendered

    prevRendered = {}

    equation = formulaOut.get(0.0, END).replace(' ', '')

    tokens = []

    # HELPER FUNCTIONS
    def previous_is(previous_value):
        return len(tokens) != 0 and tokens[-1] == previous_value

    def previous_type_is(previous_type):
        return len(tokens) != 0 and isinstance(tokens[-1], previous_type)

    def pre_elem_parenthesis():
        return previous_is(')') or previous_type_is(Element)

    # Creates list of tokens
    for number, function, operator, variable in pattern.findall(equation):
        # Searches for numbers
        if number:
            val = float(number)
            if pre_elem_parenthesis():
                if val < 0:
                    tokens.append('+')
                else:
                    tokens.append('*')
            tokens.append(Element(val))

        # Searches for functions eg. sin, cos, abs
        elif function:
            if pre_elem_parenthesis():
                tokens.append('*')
            tokens.append(function)

        # Checks for operators -> [+, -, *, /, ^, )]
        elif operator:
            if operator == '-':
                if pre_elem_parenthesis():
                    tokens.append('+')
                tokens.append(Element(-1.0))
                continue
            tokens.append(operator)

        # Checks for single letter variables
        elif variable:
            if pre_elem_parenthesis():
                tokens.append('*')
            tokens.append(Element(variable))

    formula = solve(tokens)
    calculate()


# Display equation out
def equation_out(data, add=''):
    answerOut.configure(state="normal")
    answerOut.delete("1.0", END)
    if decimal_value:
        try:
            # Solve the equation
            temp = data.new()
            temp.sub('π', 3.141592653589793238462643383279502884197)
            temp.sub('e', 2.71828182845904523536028747135)
            answerOut.insert(END, add + str(temp.force_solve()), 'right')
        except (ValueError, ZeroDivisionError, AttributeError):
            answerOut.insert(END, 'Error', 'right')
    else:
        try:
            answerOut.insert(END, add + str(data.solve()), 'right')
        except (ValueError, ZeroDivisionError, AttributeError):
            answerOut.insert(END, 'Error', 'right')

    answerOut.configure(state="disabled")


# Calculate or render the value
def calculate():
    global rendered

    # time1 = time.clock()

    data = formula

    draw_plane()

    if graph_true:
        rendered = True
        last_y = ''

        # Antialiasing value
        antialias = 4
        resize = radius * antialias
        image = Image.new('RGBA', (resize * 2 + 1, resize * 2 + 1))
        draw = ImageDraw.Draw(image)

        try:
            # Sub in values from -radius to radius and draw them
            for x in range(-radius, radius + 2):
                x = (x / zoom) - center[0]

                # Render and store value in cache
                if x in prevRendered.keys():
                    y = prevRendered[x]
                else:
                    if isinstance(data, str):
                        continue
                    y = data.new()
                    y.sub('x', x)
                    y.sub('π', 3.141592653589793238462643383279502884197)
                    y.sub('e', 2.71828182845904523536028747135)

                    try:
                        # Solve the equation
                        y = y.force_solve().simplify()

                    except (ValueError, ZeroDivisionError, AttributeError):
                        continue

                    prevRendered[x] = y

                if not isinstance(y, Element):
                    continue

                if 'j' in str(y):
                    continue

                y = y.value

                try:
                    # Draw line between current point and last point
                    y = (y - center[1]) * zoom
                    x = (x + center[0]) * zoom

                    if antialias_rendering:
                        # Smooth
                        if not (abs(resize - y) < radius and abs(resize - float(last_y)) < radius) and \
                                        abs(float(last_y) - y) < radius*2+1:
                            draw.line((round(antialias * x + resize), round(resize - y * antialias),
                                       round(antialias * (x - 1) + resize),
                                       round(resize - float(last_y) * antialias)), fill='#FFF',
                                      width=round(antialias * 1.5))
                    else:
                        # Fast
                        if not (abs(resize - y) < radius and abs(resize - float(last_y)) < radius) and \
                                        abs(float(last_y) - y) < radius*2+1:
                            viewport.create_line(round(x + radius), round(radius - y),
                                                 round(x - 1 + radius), radius - round(float(last_y), 10), fill='#EEE')

                except ValueError:
                    pass

                last_y = y

            del draw
            if antialias_rendering:
                # Resize rendered image to get antialiasing
                image = ImageTk.PhotoImage(image.resize((radius * 2, radius * 2), Image.LINEAR))

                # Draw to canvas
                viewport.create_image((radius + 1, radius + 1), image=image)
                viewport.image = image

            # Display equation
            equation_out(data, 'y = ')

        except OverflowError:
            pass

    else:
        # Display equation
        equation_out(data)

    # print(time.clock()-time1)  # PERFORMANCE TESTING


# Clear all
def clear():
    global rendered, prevRendered, formula
    formula = ''
    prevRendered = {}
    rendered = False
    answerOut.configure(state="normal")
    answerOut.delete("1.0", END)
    answerOut.configure(state="disabled")
    formulaOut.delete("1.0", END)
    viewport.delete('all')
    draw_plane()


# Delete last value
def delete():
    temp = formulaOut.get(0.0, END).replace('\n', '')
    formulaOut.delete(0.0, END)
    formulaOut.insert(END, re.sub('(' + '|'.join(list(Function.functions_map.keys())) +
                                  '|[a-zA-Zπ]|\d|\-|\+|\*|÷|\.|\(|\)|\^)$', '', temp))


# GUI elements
graphControls = Frame(graph, bg='#222', pady=3)
graphControls.pack(side=BOTTOM)

zoomText = Text(graphControls, width=10, height=1, bg='#222', fg='#EEE', borderwidth=0)
zoomText.tag_config('center', justify=CENTER)
zoomText.insert(END, str(zoom) + '×', 'center')
zoomText.configure(state='disabled')


# Add to the formula
def add_formula(c):
    formulaOut.insert(END, str(c))


# Initialise GUI B]buttons
for i in range(9):
    Button(buttons, text=str(i + 1), font=('arial', 14), width=4, height=2, command=lambda j=i: add_formula(j + 1),
           bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=3 - (i // 3), column=i % 3)

symbols = ['+', '-', '*', '/', 'sin', 'cos', '(', ')']
for i, v in enumerate(symbols):
    Button(buttons, text=v, font=('arial', 14), width=4, height=2,
           command=lambda j=i: add_formula(symbols[j]),
           bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=i // 2 + 1,
                                                                                         column=i % 2 + 3)

Button(buttons, text='.', font=('arial', 14), width=4, height=2, command=lambda: add_formula('.'),
       bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=4, column=0)
Button(buttons, text='0', font=('arial', 14), width=4, height=2, command=lambda: add_formula('0'),
       bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=4, column=1)
Button(buttons, text='x', font=('arial', 14), width=4, height=2, command=lambda: add_formula('x'),
       bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=4, column=2)
Button(buttons, text='^', font=('arial', 14), width=4, height=2, command=lambda: add_formula('^'),
       bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=2, column=5)
Button(buttons, text='e', font=('arial', 14), width=4, height=2, command=lambda: add_formula('e'),
       bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=4, column=6)
Button(buttons, text='tan', font=('arial', 14), width=4, height=2, command=lambda: add_formula('tan'),
       bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=3, column=5)
Button(buttons, text='√', font=('arial', 14), width=4, height=2, command=lambda: add_formula('√'),
       bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=3, column=6)
Button(buttons, text='π', font=('arial', 14), width=4, height=2, command=lambda: add_formula('π'),
       bg='#65c050', activebackground='#80d575', cursor='hand2', borderwidth=0).grid(row=4, column=5)

Button(buttons, text="=", font=('arial', 14), width=4, height=2, command=create_object, bg='#65c050',
       activebackground='#80d575', cursor='hand2',
       borderwidth=0).grid(row=2, column=6)
Button(buttons, text="ac", font=('arial', 14), width=4, height=2, command=clear, bg='#65c050',
       activebackground='#80d575', cursor='hand2',
       borderwidth=0).grid(row=1, column=6)
Button(buttons, text="del", font=('arial', 14), width=4, height=2, command=delete, bg='#65c050',
       activebackground='#80d575', cursor='hand2',
       borderwidth=0).grid(row=1, column=5)


# Check button for graphing on/off
def check_graph():
    global graph_true

    graph_true = not graph_true

    viewport.delete('all')
    draw_plane()

    answerOut.configure(state="normal")
    answerOut.delete("1.0", END)
    answerOut.insert(END, str(formula), 'right')
    answerOut.configure(state="disabled")

    if graph_true:
        calculate()


# Check button for antialias on/off
def switch_rendering():
    global antialias_rendering

    antialias_rendering = not antialias_rendering

    calculate()


# Check button for decimal value on/off
def switch_decimal():
    global decimal_value

    decimal_value = not decimal_value

    calculate()


# Check boxes GUI initialisation
checkBoxes = Frame(root)
checkBoxes.pack()

Checkbutton(checkBoxes, text="Graph", bg='#65c050', activebackground='#80d575', fg="#111", cursor='hand2',
            command=check_graph).grid(row=0, column=0)

Checkbutton(checkBoxes, text="Antialias", bg='#65c050', activebackground='#80d575', fg="#111", cursor='hand2',
            command=switch_rendering).grid(row=0, column=1)

Checkbutton(checkBoxes, text="Decimal", bg='#65c050', activebackground='#80d575', fg="#111", cursor='hand2',
            command=switch_decimal).grid(row=0, column=3)

zoomText.pack(side=LEFT)

onCanvas = False
startPoint = (0, 0)


# Moving canvas with mouse
def motion(event):
    global startPoint, center
    if startPoint != (0, 0):

        distance_x = (event.x - startPoint[0]) / zoom
        distance_y = (event.y - startPoint[1]) / zoom

        startPoint = (event.x, event.y)
        center = (center[0] + distance_x, center[1] + distance_y)

        if rendered:
            calculate()
        else:
            draw_plane()


def enter(event):
    global onCanvas
    onCanvas = True


def leave(event):
    global onCanvas
    onCanvas = False


def clicked(event):
    global startPoint
    if onCanvas:
        startPoint = (event.x, event.y)


def released(event):
    global startPoint
    startPoint = (0, 0)


# Zooming in and out using scroll wheel
def scroll_zoom(event):
    global zoom
    if event.delta > 0:
        z = 2
    else:
        z = 0.5

    if z >= 1 and zoom < 5000:
        zoom *= z
    if z < 1 and zoom > 0.01:
        zoom *= z
    zoom = float(zoom)
    zoomText.configure(state='normal')
    zoomText.delete("1.0", END)
    zoomText.insert(END, str(zoom) + '×', 'center')
    zoomText.configure(state='disabled')
    if rendered:
        calculate()
    else:
        draw_plane()


viewport.bind('<Enter>', enter)
viewport.bind('<Leave>', leave)
root.bind('<Button-1>', clicked)
root.bind('<ButtonRelease-1>', released)
root.bind('<B1-Motion>', motion)
viewport.bind("<MouseWheel>", scroll_zoom)

root.resizable(width=FALSE, height=FALSE)
root.mainloop()
