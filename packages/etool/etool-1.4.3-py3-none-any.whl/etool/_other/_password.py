import string
import itertools
import random
class ManagerPassword:
    results = {
                'all_letters': string.ascii_letters, # All letters
                'upper_letters': string.ascii_uppercase, # Upper letters
                'lower_letters': string.ascii_lowercase, # Lower letters
                'digits': string.digits, # Digits
                'punctuation': string.punctuation, # Punctuation
                'printable': string.printable, # Printable
                'whitespace': string.whitespace, # Whitespace
            }


    @staticmethod
    def generate_pwd_list(dic, max_len):
        """
        description:Generate a password sequence of a specified length
        param {*} dic    Dictionary
        param {*} pwd_len    Maximum password length
        return {*} All possible passwords
        """
        k = itertools.product(dic, repeat=max_len)  # Iterator
        allkey = ("".join(i) for i in k)
        if max_len == 1:

            return list(allkey)
        return ManagerPassword.generate_pwd_list(dic, max_len - 1) + list(allkey)
    
    @staticmethod
    def random_pwd(pwd_len):
        """
        Randomly generate a password
        :param pwd_len: Password length
        :return: Random password
        """
        characters = ManagerPassword.results['all_letters'] + ManagerPassword.results['digits'] + ManagerPassword.results['punctuation']
        return ''.join(random.choice(characters) for _ in range(pwd_len))

    @staticmethod
    def convert_base(number_str:str | int, from_base:int, to_base:int) -> str: 
        """Support any base conversion (2<=base<=36)
        
        Parameters:
            number_str:str | int Input number or string
            from_base:int Input base
            to_base:int Output base
        
        Returns:
            str Converted string
        """
        if from_base < 2 or from_base > 36 or to_base < 2 or to_base > 36:
            raise ValueError("Base must be between 2 and 36")

        def char_to_digit(c:str) -> int:
            """Convert character to corresponding number (supports uppercase and lowercase letters)"""
            if c.isdigit():
                return int(c)
            return 10 + ord(c.upper()) - ord('A')

        def digit_to_char(n:int) -> str:
            """Convert number to corresponding character (supports up to 36 base)"""
            return str(n) if n < 10 else chr(ord('A') + n - 10)

        number_str = str(number_str)
        # Process empty input and symbols
        number_str = number_str.strip()
        if not number_str:
            return "0"
        
        negative = number_str[0] == '-'
        number_str = number_str[1:] if negative else number_str

        # Convert input string to decimal
        decimal_num = 0
        for c in number_str:
            digit = char_to_digit(c)
            if digit >= from_base:
                raise ValueError(f"Character {c} is invalid in {from_base} base")
            decimal_num = decimal_num * from_base + digit

        # Process special case for 0
        if decimal_num == 0:
            return '0'

        # Convert to target base
        result = []
        while decimal_num > 0:
            result.append(digit_to_char(decimal_num % to_base))
            decimal_num = decimal_num // to_base

        return ('-' if negative else '') + ''.join(reversed(result))


if __name__ == "__main__":
    print(ManagerPassword.convert_base("A1F", 16, 2))   # Output: 101000011111
    print(ManagerPassword.convert_base("-1101", 2, 16)) # Output: -D
    print(ManagerPassword.convert_base("Z", 36, 10))    # Output: 35

