# sudoku
A nice little sudoku app in python written to see how far you get with current LLMs

*Use it* by simply running python googoku.py. Should be pretty self-explanatory. Use the "m" key to toggle between entering the final value and pencil notes. Cursor keys and such are supported.
Please note that it takes between a fraction of a second and several minutes to generate a new sudoku.

*Re-build it* by looking into the prompts folder; they contain the 4 or so prompts that I was using to generate the code. This is actually the main purpose of having this on Github; maybe you're interested in those prompts, as I've been fairly successful with them.

Please note: advanced_generator.py is the result of my session to create a nice solver. However, when creating the UI, gemini decided to pretty much ignore it and build its own solver / generator losely based on my ideas/code...

Also please note that I was using github copilot to add a few quality of life improvements that I had not initially specified, so if you want to see the output of the prompt for Google Gemini 2.5 pro, you need to sync version one of googoku.py
