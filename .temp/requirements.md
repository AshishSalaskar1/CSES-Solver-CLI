### Problem

- I want to solve problems on CSES problem set but locally and not online
- Source: <https://cses.fi/problemset/>
- Online site is slow plus has too much overload to run

### Data

- Site: <https://cses.fi/problemset/>
- I dont need these topics included from the site
  - Mathematics
  - String Algorithms
  - Geometry
  - Construction Problems\
    Additional Problems I and 

    <br />

### Solution

- Have a CLI that lets me run a python code file written locally in system and provide the CSES problem ID
- The cli should then run my code against all test cases n give me result analytics
- For this i need a locally stored mapping of problem\_link, ID and the test cases and then run my test cases against it

<br />

### How the CLI  would look for me

Usage style: python code\_file\_name.py problem\_number

-> finds the test cases for this problem number
-> runs my code
-> returns the results ( tells me which is failing and prints the input|expected output)
\-

QUESTIONS

- Can i run a particular test cases \[MOSTLY NOT NEEDED]

  <br />

TEST CASES

- Maybe 100 each -> can you estimate the size of that
- Generate test cases ( there are around 300 problem in teh CSES Set). I dont need very MLE type long test cases but the ones taken should cover n check the overall correctness of the solution
- I want to push this test case file ( im thinking of a sqlite db file maybe) into a git repo. So it should not be too large in size and hence you can decide the adequate number of test cases for each problen

CLI COMMANSD

1. invoke - full screen temrinal like lazygit
2. run -> code\_path.py problem\_number -> just runs n shows output < need to decide against which test case it runs >
3. test -> code\_path.py problem\_number ->

- runs code against all cases, shows some nice stats on successful cases (x/y)
- it then displays case nubmer on left side ( like a tab - green or red color -> red ones are failing at the top) ->
- when any case number is selected on right panel it should show input, output, expected output ( any other print debug stuff)
- red or failing cases should be at the top
- Im thiunking when u first test it just shows stats n maybe you have an option to deep dive into results -> which then shows this test case explorer kind of view

### HOW TO DEAL WITH INPUT

- In CSES its a file input ->
  -> OUTPUT is always a value returned by the codes main functions. Any prints are treated as debugging output
- Im thiking that i will surely have a `main()` function in each file that i supply but then how will you simulate the input

<br />

<br />

## Research Asks

- Check technical feasibility - which lang + framwork to use to build the CLI tool and which tool to use for the test case storage locally
- ONLY needs to support python for now ( in ffuture can be expanded to other languages )
- Main feature is the correctness n comprehensive of the  test case correct plus balancing it with size of the test case dataset locally
- The cli needs to be like a TUI and really interactive
- <br />

