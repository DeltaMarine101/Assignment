import math


# Find the highest common factor
def get_hcf(a, b):
    for i in a:
        if i in b:
            return i
    return ''


# Get the coefficient of a value
def get_coefficient(val):
    if isinstance(val, Power):
        return 1.0
    else:
        temp = val.factors()
        hf = 0.0
        for i in temp:
            if isinstance(i, float):
                if abs(i) >= abs(hf):
                    hf = i
        if hf == 0:
            return 1.0
        else:
            return hf


# val
class Element:
    def __init__(self, val):
        if isinstance(val, int):
            val = float(val)
        self.value = val

    # Return the factors of the element
    def factors(self):
        if isinstance(self.value, float):
            if self.value % 1 == 0:
                fact = set()
                temp = abs(self.value)
                if self.value < 0:
                    fact.add(-1)
                for i in range(1, math.floor(math.sqrt(temp)) + 1):
                    if self.value % i == 0:
                        fact.add(float(i))
                        fact.add((temp//i))
                return sorted(list(fact), reverse=True)
            else:
                return [self.value]
        else:
            return [self.value]

    # Simplify
    def simplify(self):
        if isinstance(self.value, Element):
            return self.value
        else:
            return self.new()

    # Sub in a value as a variable
    def sub(self, var, val):
        if self.value == var:
            self.value = val

    # Create new self
    def new(self):
        return Element(self.value)

    # Solve self
    def solve(self):
        return self.new()

    # Solve as decimal
    def force_solve(self):
        if isinstance(self.value, Element):
            return self.value
        else:
            return self

    # Addition operator handling
    def __add__(self, other):
        if isinstance(other, Element):
            if isinstance(other.value, float) and isinstance(self.value, float):
                return Element(other.value + self.value)
            else:
                return ExpressionA((self, other)).simplify()
        else:
            return ExpressionA((self, other)).simplify()

    # Multiplication operator handling
    def __mul__(self, other):
        # If element
        if isinstance(other, Element):
            if isinstance(other.value, float) and isinstance(self.value, float):
                return Element(other.value * self.value)
            elif other.value == self.value:
                return Power(self.value, Element(2.0))
            else:
                return ExpressionM((self, other))

        # If Power
        elif isinstance(other, Power):
            if isinstance(other.base, Element):
                if other.base.value == self.value:
                    return Power(self, other.power + Element(1.0)).simplify()
                else:
                    return ExpressionM((self, other))
            else:
                return ExpressionM((self, other))

        # If ExpressionM
        elif isinstance(other, ExpressionM):
            return ExpressionM((self, other)).simplify()

        # If ExpressionA
        elif isinstance(other, ExpressionA):
            out_array = []
            for i in other.value:
                out_array.append(i * self)
            return ExpressionA(out_array).simplify()

        # If fraction
        elif isinstance(other, Fraction):
            return Fraction(other.numerator * self, other.denominator).simplify()

        # If function
        elif isinstance(other, Function):
            return (other * self).simplify()

    # Division operator handling
    def __truediv__(self, other):
        if isinstance(other, Element):
            hcf = get_hcf(self.factors(), other.factors())
            if hcf != '':
                if isinstance(other.value, float) and isinstance(self.value, float):
                    if (self.value / other.value) % 1 == 0:
                        return Element(self.value / other.value)
                    else:
                        return Fraction(Element(self.value / hcf), Element(other.value / hcf))
                else:
                    return Element(1.0)
            else:
                return Fraction(self, other)

        else:
            return Fraction(self, other).simplify()

    # Power operator handling
    def __pow__(self, other):
        return Power(self, other).simplify()

    # Equality handling
    def __eq__(self, other):
        if isinstance(other, Element):
            return self.value == other.value
        else:
            return False

    # String representation
    def __str__(self):
        return str(self.value)


# Cosec calculation
def cosec(x):
    return 1/math.sin(x)


# Sec calculation
def sec(x):
    return 1/math.cos(x)


# Cot calculation
def cot(x):
    return 1/math.tan(x)


# Func(x)
class Function:
    # All funtions
    functions_map = {'sin': math.sin,
                     'cos': math.cos,
                     'tan': math.tan,
                     'cosec': cosec,
                     'sec': sec,
                     'cot': cot,
                     'arcsin': math.asin,
                     'arccos': math.acos,
                     'arctan': math.atan,
                     'degrees': math.degrees,
                     'radians': math.radians,
                     '√': math.sqrt,
                     'floor': math.floor,
                     'ceil': math.ceil,
                     'factorial': math.gamma,
                     'nl': math.log,
                     'log': math.log10,
                     'abs': abs}

    def __init__(self, val, t):
        self.value = val
        self.type = t

    # Return factors
    def factors(self):
        return [self.new()]

    # Simplify
    def simplify(self):
        return Function(self.value.simplify(), self.type)

    # Sub in a value as variable
    def sub(self, var, val):
        self.value.sub(var, val)

    # Create new self
    def new(self):
        return Function(self.value.new(), self.type)

    # Solve
    def solve(self):
        temp = self.value.force_solve()
        if isinstance(temp, Element):
            if isinstance(temp.value, float):
                if self.functions_map[self.type](temp.value) % 1 == 0:
                    return Element(self.functions_map[self.type](temp.value))
                else:
                    return Function(self.value.solve(), self.type)
            else:
                return Function(self.value.solve(), self.type)
        return Function(self.value.solve(), self.type)

    # Solve as decimal
    def force_solve(self):
        temp = self.value.force_solve()
        if isinstance(temp, Element):
            if isinstance(temp.value, float):
                return Element(self.functions_map[self.type](temp.value))
            else:
                return Function(self.value.force_solve(), self.type)
        return Function(self.value.force_solve(), self.type)

    # Addition operator handling
    def __add__(self, other):
        if isinstance(other, Function):
            if other.type == self.type and other.value == self.value:
                return ExpressionM((Element(2.0), self))
            else:
                return ExpressionA((self, other)).simplify()
        else:
            return ExpressionA((self, other)).simplify()

    # Multiplication operator handling
    def __mul__(self, other):
        if isinstance(other, Function):
            if other == self:
                return Power(self, Element(2.0))
            else:
                return ExpressionM((self, other)).simplify()
        else:
            return ExpressionM((self, other)).simplify()

    # Divide operator handling
    def __truediv__(self, other):
        if isinstance(other, Function):
            if other == self:
                return Element(1.0)
        return Fraction(self, other).simplify()

    # Power operator handling
    def __pow__(self, other):
        return Power(self, other).simplify()

    # Equality handling
    def __eq__(self, other):
        if isinstance(other, Function):
            return self.value.simplify() == other.value.simplify() and self.type == other.type
        else:
            return False

    # String representation
    def __str__(self):
        return self.type + '(' + str(self.value) + ')'


# val ^ val
class Power:
    def __init__(self, val, p):
        if isinstance(val, float) or isinstance(val, str):
            self.base = Element(val)
        else:
            self.base = val
        if isinstance(p, float) or isinstance(p, str):
            self.power = Element(p)
        else:
            self.power = p

    # Returns factors
    def factors(self):
        if isinstance(self.power, Element):
            if isinstance(self.power.value, float):
                if self.power.value < 1:
                    return []
        return self.base.factors()

    # Simplify
    def simplify(self):
        # Simplify base and power
        self.base = self.base.simplify()
        self.power = self.power.simplify()

        if isinstance(self.power, Element):
            # To the power of 0
            if self.power.value == 0:
                return Element(1.0)
            # To the power of 1
            elif self.power.value == 1:
                return self.base
            # To the power of -1
            elif self.power.value == -1:
                return Fraction(Element(1.0), self.base)
            # To the power of a negative
            elif isinstance(self.power.value, float):
                if self.power.value < 0:
                    return Fraction(Element(1.0), Power(self.base, Element(-self.power.value)))

        if isinstance(self.power, Fraction):
            # To the power of 0.5
            if self.power.numerator == 1 and self.power.numerator == 2:
                return Function(self.base, '√')
            # To the power of -0.5
            elif self.power.numerator == -1 and self.power.numerator == 2:
                return Fraction(Element(1.0), Function(self.base, '√'))

        # If base ^ power is an exact value
        if isinstance(self.base, Element) and isinstance(self.power, Element):
            if isinstance(self.base.value, float) and isinstance(self.power.value, float):
                if (self.base.value ** self.power.value) % 1 == 0:
                    return Element(self.base.value ** self.power.value)
                else:
                    return self
            else:
                return self
        else:
            return self

    # Sub in a value as a variable
    def sub(self, var, val):
        self.base.sub(var, val)
        self.power.sub(var, val)

    # Creates new self
    def new(self):
        return Power(self.base.new(), self.power.new())

    # Solve
    def solve(self):
        return (self.base.solve() ** self.power.solve()).simplify()

    # Solve as decimal
    def force_solve(self):
        temp_base = self.base.force_solve()
        temp_power = self.power.force_solve()
        if isinstance(temp_base, Element) and isinstance(temp_power, Element):
            if isinstance(temp_base.value, float) and isinstance(temp_power.value, float):
                return Element(temp_base.value ** temp_power.value)
            else:
                return self.solve()
        else:
            return self.solve()

    # Addition operator handling
    def __add__(self, other):
        if isinstance(other, Power):
            if other == self:
                return ExpressionM((Element(2.0), self))
            else:
                return ExpressionA((self, other))
        else:
            return ExpressionA((self, other))

    # Multiplication operator handling
    def __mul__(self, other):
        # If element
        if isinstance(other, Element):
            return other * self

        # If power
        elif isinstance(other, Power):
            return other * self

        # If ExpressionM
        elif isinstance(other, ExpressionM):
            return ExpressionM((self, other)).simplify()

        # If ExpressionA
        elif isinstance(other, ExpressionA):
            out_array = []
            for i in other.value:
                out_array.append(i * self)
            return ExpressionA(out_array).simplify()

        # If fraction
        elif isinstance(other, Fraction):
            return Fraction(other.numerator * self, other.denominator).simplify()

        # If function
        elif isinstance(other, Function):
            return (other * self).simplify()

    # Divide operator handling
    def __truediv__(self, other):
        if isinstance(other, Element):
            if isinstance(self.base, Element):
                if self.base.value == other.value:
                    return Power(Element(self.base), self.power + Element(-1.0)).simplify()
                else:
                    return Fraction(self, other)
            else:
                return Fraction(self, other)

        else:
            return Fraction(self, other).simplify()

    # Power operator handling
    def __pow__(self, other):
        return Power(self.base, other * self.power)

    # Equality handling
    def __eq__(self, other):
        if isinstance(other, Power):
            return self.base == other.base and self.power == other.power
        else:
            return False

    # String representation
    def __str__(self):
        return str(self.base) + '^' + str(self.power)


# {val * val * ...}
class ExpressionM:
    def __init__(self, val):
        self.value = []
        for i in val:
            if isinstance(i, ExpressionM):
                for j in i.value:
                    self.value.append(j)
            else:
                self.value.append(i)

    # Returns factors
    def factors(self):
        fact = []
        for i in self.value:
            for j in i.factors():
                fact.append(j)
        return fact

    # Simplify
    def simplify(self):
        temp = self.value

        old_temp = ''
        while old_temp != temp:
            old_temp = temp
            # Go through each element
            for i in range(len(temp)-1):
                b = False
                for j in range(i+1, len(temp)):
                    # Multiply together
                    if isinstance(temp[i], Element) and isinstance(temp[j], Element):
                        if isinstance(temp[i].value, float) and isinstance(temp[j].value, float):
                            temp[i] = temp[i] * temp[j]
                            temp.pop(j)
                            break
                    # If they have common factors
                    for f in temp[i].factors():
                        if f in temp[j].factors():
                            temp[i] = temp[i] * temp[j]
                            temp.pop(j)
                            temp.insert(0, '')
                            b = True
                            break
                    if b:
                        break

            for i in range(len(temp)):
                try:
                    if isinstance(temp[i], Element):
                        if temp[i].value == 1.0:
                            temp.pop(i)
                            temp.insert(0, '')
                except AttributeError:
                    pass

            while temp[0] == '':
                temp.pop(0)

        if len(temp) == 1:
            return temp[0]
        else:
            return ExpressionM(temp)

    # Sub in a value as a variable
    def sub(self, var, val):
        for i in self.value:
            i.sub(var, val)

    # Create new self
    def new(self):
        return ExpressionM([i.new() for i in self.value])

    # Solve
    def solve(self):
        temp = Element(1)
        for i in self.value:
            temp = temp * i.solve()
        return temp

    # Solve as decimal
    def force_solve(self):
        temp = self
        for i in range(len(temp.value)):
            temp.value[i] = temp.value[i].force_solve()

        return temp.solve()

    # Addition operator handling
    def __add__(self, other):
        return ExpressionA((self, other)).simplify()

    # Multiplication operator handling
    def __mul__(self, other):
        # If element
        if isinstance(other, Element):
            return ExpressionM((self, other)).simplify()

        # If power
        elif isinstance(other, Power):
            return ExpressionM((self, other)).simplify()

        # If expressionM
        elif isinstance(other, ExpressionM):
            return ExpressionM((self, other)).simplify()

        # If expressionA
        elif isinstance(other, ExpressionA):
            out_array = []
            for i in other.value:
                out_array.append(i * self)
            return ExpressionA(out_array).simplify()

        # If fraction
        elif isinstance(other, Fraction):
            return Fraction(other.numerator * self, other.denominator)

        # If function
        elif isinstance(other, Function):
            return (other * self).simplify()

    # Divide operator handling
    def __truediv__(self, other):
        if isinstance(other, Element):
            for i in range(len(self.value)):
                if other.value in self.value[i].factors():
                    self.value[i] = self.value[i] / other
                    return self.simplify()
            return Fraction(self, other).simplify()

        else:
            return Fraction(self, other).simplify()

    # Power operator handling
    def __pow__(self, other):
        out_array = []
        for i in self.value:
            out_array.append(i ** other)
        return ExpressionM(out_array).simplify()

    # Equality handling
    def __eq__(self, other):
        if isinstance(other, ExpressionM):
            return self.value == other.value
        else:
            return False

    # String representation
    def __str__(self):
        return '*'.join([str(i) for i in self.value])


# [val + val + ...]
class ExpressionA:
    def __init__(self, val):
        self.value = []
        for i in val:
            if isinstance(i, ExpressionA):
                for j in i.value:
                    self.value.append(j)
            else:
                self.value.append(i)

    # Returns factors
    def factors(self):
        fact = ''
        for i in self.value:
            if fact == '':
                fact = i.factors()
            else:
                temp = []
                for j in i.factors():
                    if j in fact:
                        temp.append(j)
                fact = temp
        return fact

    # Simplify
    def simplify(self):
        temp = self
        old_temp = ''

        while temp != old_temp:
            old_temp = temp

            ar = []
            for i in temp.value:
                ar.append(i.simplify())

            # Make array of coefficients and attached values
            coefficients = []
            values = []
            for i in ar:
                coefficients.append(get_coefficient(i))
                values.append((i / Element(get_coefficient(i))).solve().simplify())
            out = []
            count = len(values)
            while count > 0:
                val = values.pop(0)
                b = True
                # Go through each element
                for i in range(len(values)):
                    # If the first value equals the current value
                    try:
                        temp_val1 = Element(abs(val.value))
                        temp_val2 = Element(abs(values[i].value))
                    except AttributeError:
                        temp_val1 = val
                        temp_val2 = values[i]
                    if temp_val1 == temp_val2:
                        # Add coefficients
                        neg1 = 1
                        neg2 = 1
                        try:
                            if val.value < 0:
                                neg1 = -1
                            if values[i].value < 0:
                                neg2 = -1
                        except AttributeError:
                            pass
                        out.append(Element(neg1*coefficients[0] + neg2*coefficients[i+1]) * val)
                        values.pop(i)
                        coefficients.pop(0)
                        coefficients.pop(i)
                        b = False
                        count -= 1
                        break
                if b:
                    out.append(Element(coefficients.pop(0)) * val)
                count -= 1
            temp = ExpressionA([i.simplify() for i in out])
        if len(temp.value) == 1:
            return temp.value[0]
        else:
            return temp

    # Sub in a value as a variable
    def sub(self, var, val):
        for i in self.value:
            i.sub(var, val)

    # Create new self
    def new(self):
        return ExpressionA([i.new() for i in self.value])

    # Solve
    def solve(self):
        temp = self.new()
        for i in range(len(temp.value)):
            temp.value[i] = temp.value[i].solve()
        return self.simplify()

    # Solve as decimal
    def force_solve(self):
        temp = self.new()
        for i in range(len(temp.value)):
            temp.value[i] = temp.value[i].force_solve()

        return temp.simplify()

    # Addition operator handling
    def __add__(self, other):
        return ExpressionA((self, other)).simplify()

    # Multiplication operator handling
    def __mul__(self, other):
        if isinstance(other, Fraction):
            Fraction(self * other.numerator, other.denominator).simplify()
        else:
            out_array = []
            for i in self.value:
                out_array.append(i * other)
            return ExpressionA(out_array).simplify()

    # Divide operator handling
    def __truediv__(self, other):
        if isinstance(other, Element):
            if other.value in self.factors():
                out_array = []
                for i in self.value:
                    out_array.append(i / other)
                return ExpressionA(out_array).simplify()
            else:
                return Fraction(self, other).simplify()
        else:
            return Fraction(self, other).simplify()

    # Power operator handling
    def __pow__(self, other):
        return Power(self, other).simplify()

    # Equality handling
    def __eq__(self, other):
        if isinstance(other, ExpressionA):
            return self.value == other.value
        else:
            return False

    # String representation
    def __str__(self):
        return '(' + ' + '.join([str(i) for i in self.value]) + ')'


# (val / val)
class Fraction:
    def __init__(self, num, den):
        self.numerator = num
        self.denominator = den

    # Returns factors
    def factors(self):
        return self.numerator.factors()

    # Simplify
    def simplify(self):
        # Simplify top and bottom
        temp = Fraction(self.numerator.simplify(), self.denominator.simplify())

        # Combine the numerator fraction
        if isinstance(temp.numerator, Fraction):
            temp = Fraction(temp.numerator.numerator, temp.denominator * temp.numerator.denominator)

        # Combine the denominator fraction
        if isinstance(temp.denominator, Fraction):
            temp = Fraction(temp.numerator * temp.denominator.denominator, temp.denominator.numerator)

        # If top equals bottom
        if temp.numerator == temp.denominator:
            return Element(1.0)

        while True:
            # Divide the top and bottom by the highest common factor
            hcf = get_hcf(temp.numerator.factors(), temp.denominator.factors())
            if hcf == '' or hcf == 1.0:
                if isinstance(temp.denominator, Element):
                    if temp.denominator.value == 1:
                        return temp.numerator
                return temp
            temp.numerator = temp.numerator / Element(hcf)
            temp.denominator = temp.denominator / Element(hcf)

    # Sub in a value as a variable
    def sub(self, var, val):
        self.numerator.sub(var, val)
        self.denominator.sub(var, val)

    # Create new self
    def new(self):
        return Fraction(self.numerator.new(), self.denominator.new())

    # Solve
    def solve(self):
        return self.numerator.solve() / self.denominator.solve()

    # Solve as decimal
    def force_solve(self):
        # Solve top and bottom
        temp_num = self.numerator.force_solve()
        temp_den = self.denominator.force_solve()

        # Force solve fraction
        if isinstance(temp_num, Element) and isinstance(temp_num, Element):
            if isinstance(temp_num.value, float) and isinstance(temp_den.value, float):
                return Element(temp_num.value / temp_den.value)
            else:
                return temp_num / temp_den
        else:
            return temp_num / temp_den

    # Addition operator handling
    def __add__(self, other):
        if isinstance(other, Fraction):
            return Fraction((self.numerator * other.denominator) + (other.numerator * self.denominator),
                            self.denominator * other.denominator).simplify()
        else:
            return ExpressionA((self, other)).simplify()

    # Multiplication operator handling
    def __mul__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.numerator * other.numerator, self.denominator * other.denominator).simplify()
        else:
            return other * self

    # Divide operator handling
    def __truediv__(self, other):
        return Fraction(self, other).simplify()

    # Power operator handling
    def __pow__(self, other):
        return Fraction(self.numerator ** other, self.denominator ** other).simplify()

    # Equality handling
    def __eq__(self, other):
        if isinstance(other, Fraction):
            return self.numerator == other.numerator and self.denominator == other.denominator
        else:
            return False

    # String representation
    def __str__(self):
        return str(self.numerator) + '/' + str(self.denominator)
