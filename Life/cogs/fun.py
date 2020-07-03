"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.text_to_morse = {
            'A': '.-',     'B': '-...',   'C': '-.-.',   'D': '-..',    'E': '.',       'F': '..-.',
            'G': '--.',    'H': '....',   'I': '..',     'J': '.---',   'K': '-.-',     'L': '.-..',
            'M': '--',     'N': '-.',     'O': '---',    'P': '.--.',   'Q': '--.-',    'R': '.-.',
            'S': '...',    'T': '-',      'U': '..-',    'V': '...-',   'W': '.--',     'X': '-..-',
            'Y': '-.--',   'Z': '--..',    '0': '-----',  '1': '.----',  '2': '..---',   '3': '...--',
            '4': '....-',  '5': '.....',  '6': '-....',  '7': '--...',  '8': '---..',   '9': '----.',
            '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',  "/": '-..-.',
            '(': '-.--.', ')': '-.--.-', '&': '.-...',  ':': '---...', ';': '-.-.-.',  '=': '-...-',
            '+': '.-.-.',  '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.',
            ' ': ' '
        }
        self.bot.morse_to_text = {value: key for key, value in self.bot.text_to_morse.items()}

    @commands.command(name='morse')
    async def morse(self, ctx, *, text: commands.clean_content):
        """
        Converts the given text into morse code.

        `text`: The text to convert.

        This command supports the following characters:
         A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9 . , ? ' ! / ( ) & : ; = + - _ " $ @
        """

        morse_text = ' '.join([self.bot.text_to_morse.get(letter.upper(), letter) for letter in str(text).strip()])
        return await ctx.send_bin(f'`{morse_text}`')

    @commands.command(name='demorse')
    async def demorse(self, ctx, *, morse: commands.clean_content):
        """
        Converts the given morse code into text.

        `morse`:  The morse code to convert.

        If there are 3 spaces in between each morse word it will have the correct spacing in the output.
        """

        message = []
        for word in str(morse).strip().split('   '):
            message.append(''.join([self.bot.morse_to_text.get(letter.upper(), letter) for letter in word.split()]))
        message = " ".join(message)

        return await ctx.send_bin(f'`{message}`')

    @commands.command(name='binary')
    async def binary(self, ctx, *, text: commands.clean_content):
        """
        Converts the given text into it's binary form.

        'text`: The text to convert into binary.
        """

        binary = bin(int.from_bytes(str(text).encode('utf-8'), 'big'))[2:]
        binary.zfill(8 * ((len(binary) + 7) // 8))
        return await ctx.send_bin(f'`{binary}`')

    @commands.command(name='debinary')
    async def debinary(self, ctx, *, binary: commands.clean_content):
        """
        Converts the given binary into its text form.

        'binary`: The binary to convert into text.
        """

        try:
            n = int(str(binary).strip(' '), 2)
            text = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8') or '\0'
            return await ctx.send_bin(f'`{text}`')
        except ValueError:
            return await ctx.send('That was not a valid binary string.')


def setup(bot):
    bot.add_cog(Fun(bot))
