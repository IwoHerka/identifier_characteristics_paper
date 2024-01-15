-module(my_module).
-export([public_function/1, func/1, func/2, recursive_function/1, say_hello/0]).
-export([handle_call/3, handle_cast/2, init/1]). 


% Named functions (public and private)
public_function(Arg) ->
    % public function body.
    private_function(Arg).


private_function(Arg) ->
    % private function body.


% anonymous functions
anonymous_function_demo() ->
    Add = fun(A, B) -> A + B end,
    Result = Add(1, 2),
    Result.


% functions with multiple clauses and guards
func(X) when is_number(X) ->
    % logic for numbers.
    X + 1;
func(X) when is_list(X) ->
    % logic for lists.
    length(X).


% function overloading
func(A) ->
    % one argument
    A * 2;
func(A, B) ->
    % two arguments
    A + B.


% recursive function
recursive_function(0) ->
    done;
recursive_function(N) when N > 0 ->
    recursive_function(N - 1).


% OTP behaviours
init(Args) ->
    % initialization logic
    {ok, Args}.
handle_call(Request, _From, State) ->
    % handling synchronous calls
    {reply, ok, State}.
handle_cast(Msg, State) ->
    % handling asynchronous messages
    {noreply, State}.



% macro-based function definitions
-define(SAY_HELLO(Name), io:format("Hello, ~p~n", [Name])).

say_hello() ->
    ?SAY_HELLO("World").


% higher-order functions
higher_order_function_demo() ->
    HigherOrder = fun(Func, Arg) -> Func(Arg) end,
    Add = fun(A) -> A + 10 end,
    HigherOrder(Add, 5).
