Page: aider.chat_files/aider.chat/examples/README.html
----------------------------------------
   #[1]RSS Feed

   [2]Skip to main content

   [3]aider (BUTTON)

     * [4]Home
     * (BUTTON) [5]Installation
          + [6]Installing aider
          + [7]Optional steps
          + [8]Aider with docker
          + [9]Install with pipx
          + [10]GitHub Codespaces
     * (BUTTON) [11]Usage
          + [12]Tips
          + [13]In-chat commands
          + [14]Chat modes
          + [15]Tutorial videos
          + [16]Voice-to-code with aider
          + [17]Images & web pages
          + [18]Prompt caching
          + [19]Aider in your browser
          + [20]Specifying coding conventions
          + [21]Linting and testing
     * (BUTTON) [22]Connecting to LLMs
          + [23]OpenAI
          + [24]Anthropic
          + [25]Gemini
          + [26]GROQ
          + [27]Azure
          + [28]Cohere
          + [29]DeepSeek
          + [30]Ollama
          + [31]OpenAI compatible APIs
          + [32]OpenRouter
          + [33]Vertex AI
          + [34]Amazon Bedrock
          + [35]Other LLMs
          + [36]Editing format
          + [37]Model warnings
     * (BUTTON) [38]Configuration
          + [39]Options reference
          + [40]YAML config file
          + [41]Config with .env
          + [42]Advanced model settings
     * (BUTTON) [43]Troubleshooting
          + [44]File editing problems
          + [45]Model warnings
          + [46]Token limits
          + [47]Aider not found
          + [48]Dependency versions
          + [49]Using /help
     * (BUTTON) [50]Example chat transcripts
          + [51]Create a simple flask app with aider
          + [52]Modify an open source 2048 game with aider
          + [53]A complex multi-file change, with debugging
          + [54]Create a "black box" test case
          + [55]Automatically update docs with aider
          + [56]Build pong with aider and pygame.
          + [57]Complete a css exercise with aider
          + [58]Download, analyze and plot US Census data
          + [59]Editing an asciinema cast file with aider
          + [60]Hello aider!
          + [61]Honor the NO_COLOR environment variable
          + [62]Improve css styling of chat transcripts
          + [63]Semantic search & replace code with aider
     * (BUTTON) [64]More info
          + [65]Git integration
          + [66]Supported languages
          + [67]Repository map
          + [68]Scripting aider
          + [69]Infinite output
          + [70]Edit formats
          + [71]Analytics
          + [72]Privacy policy
          + [73]Release history
     * [74]FAQ
     * [75]Aider LLM Leaderboards
     * [76]Aider blog

     * [77]GitHub
     * [78]Discord

   Aider is AI pair programming in your terminal. Aider is on [79]GitHub
   and [80]Discord.

   ____________________

     * [81]GitHub
     * [82]Discord
     * [83]Blog

Example chat transcripts

   Below are some chat transcripts showing what it's like to code with
   aider. In the chats, you'll see a variety of coding tasks like
   generating new code, editing existing code, debugging, exploring
   unfamiliar code, etc.
     * [84]Hello World Flask App: Start from scratch and have aider create
       a simple Flask app with various endpoints, such as adding two
       numbers and calculating the Fibonacci sequence.
     * [85]Javascript Game Modification: Dive into an existing open-source
       repo, and get aider's help to understand it and make modifications.
     * [86]Complex Multi-file Change with Debugging: Aider makes a complex
       code change that is coordinated across multiple source files, and
       resolves bugs by reviewing error output and doc snippets.
     * [87]Create a Black Box Test Case: Aider creates a "black box" test
       case without access to the source of the method being tested, using
       only a [88]high level map of the repository based on ctags.
     * [89]Honor the NO_COLOR env var: The user pastes the NO_COLOR spec
       from no-color.org into the chat, and aider modifies the application
       to conform.
     * [90]Download, analyze and plot US Census data: Aider downloads
       census data, suggests some hypotheses to test, tests one and then
       summarizes and plots a graph of the results.
     * [91]Semantic Search & Replace: Updating a collection of function
       calls, which requires dealing with various formatting and semantic
       differences in the various function call sites.
     * [92]Pong Game with Pygame: Creating a simple Pong game using the
       Pygame library, with customizations for paddle size and color, and
       ball speed adjustments.
     * [93]CSS Exercise: Animation Dropdown Menu: A small CSS exercise
       involving adding animation to a dropdown menu.
     * [94]Automatically Update Docs: Automatically updating documentation
       based on the latest version of the main() function.
     * [95]Editing an Asciinema Cast File: Editing escape sequences in an
       asciinema screencast file.

What's happening in these chats?

   To better understand the chat transcripts, it's worth knowing that:
     * Each time the LLM suggests a code change, aider automatically
       applies it to the source files.
     * After applying the edits, aider commits them to git with a
       descriptive commit message.
     * The LLM can only see and edit files which have been "added to the
       chat session". The user adds files either via the command line or
       the in-chat /add command. If the LLM asks to see specific files,
       aider asks the user for permission to add them to the chat. The
       transcripts contain notifications from aider whenever a file is
       added or dropped from the session.

Transcript formatting

     This is output from the aider tool.

These are chat messages written by the user.

   Chat responses from the LLM are in a blue font like this, and often
   include colorized "edit blocks" that specify edits to the code. Here's
   a sample edit block that switches from printing "hello" to "goodbye":
hello.py
<<<<<<< ORIGINAL
print("hello")
=======
print("goodbye")
>>>>>>> UPDATED

