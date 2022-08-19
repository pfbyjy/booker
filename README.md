# Booker
Booker is a command line utility that allows you to manage your reading list.

## Usage
Add the booker cli to your path.
`booker-cli --help`

## Development
### Setup
From the root of the project directory.
- python -m venv ./venv
- source venv/bin/activate
- install dependencies with `python -m pip install -r requirements.txt`
### Testing
#### Full Test Suite
From the root of the project directory
- `./run_tests` 
For more details see the usage section in the `./test` file.
Coverage data is uploaded [here](https://app.codecov.io/gh/pfbyjy/booker)

## Additional Feature
For the additional feature I went a bit meta and implemented a small library
that allows for Haskell style function composition in python. Object oriented
languages are often littered with exception handling and clunky composition.
I wanted to avoid that completely during this project so I set out with two goals
in mind. 
- Centralize exception handling
- Centralize error reporting 
- Simplify testing by guaranteeing that smaller pieces of functionality compose correctly
- provide a fluent means of composition that reduces code footprint.

The outcome is a library that I'm calling pipeline and it's based loosely on the idea of 
an either/applicative functor from haskell. 
The core components are a class Pipeline and a decorator @outcome.
@outcome performs the task of allowing a function to be "lifted" into the context of a pipeline,
and a pipeline allows multiple functions to be chained, such that the output of one is piped into
the next. The result is a setup that looks roughly as follows

```
@outcome(requires=('color', ), 
returns="augumented_color",
registers={
	OSError : FileNotFoundHandler
})
def a(color:str)->str:
	...
	...
	return ans

@outcome(requires=('augumented_color",),
returns("house")) # this does not register any Handlers, but the framework will handle unexpected errors.
def b(augumented_color: str) -> House:
	...
	...
	return ans


# now we chain them up like so

pipeline = Pipeline(initial_args={'color': 'blue'}) << a << b
return (~pipeline).yield_result()
```

The library introduces two new operators. 
- `<<` which can be read as `composed with`
- `~` which a unary operator that can be read as execute.

So the last two lines can be read as pipeline composed with function a, composed with function b.
return execute pipeline and yield result.

What this means for the developer is that once small functions are defined and tested, it is possible
to avoid the need to extensively test larger functionality as it follows that correctness in each stage
of the pipeline implies the correctness of the entire pipeline. The second thing it means is that there 
will be much less of a need for boilerplate and code duplication as tasks reduce to finding existing
functions that can be composed to build new features, only implementing what does not exist yet and implementing
new features by chaining together existing functions. As long as any new feature is some ordering of the existing
set of functionality, the only new code that needs to be written is the definition of the pipeline. Testing optional.

