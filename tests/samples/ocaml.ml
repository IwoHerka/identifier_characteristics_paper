let x = 10


(* 1. Using 'let' *)
let add x y = x + y


(* 2. Using 'let' with 'in' for local scope *)
let subtract x y = 
    let neg y = -y in
    x + neg y


(* 3. Using a named function within another function *)
let multiply x y = 
    let inner_multiply m n = m * n in
    inner_multiply x y


(* 4. Defining a recursive function with 'let rec' *)
let rec factorial n =
    if n = 0 then 1 else n * factorial (n - 1)


(* 5. Using anonymous function (Lambda) *)
let divide = fun x y -> x / y


(* 6. Using function keyword for pattern matching *)
let abs x = 
    function
    | x when x >= 0 -> x
    | _ -> -x


(* 7. Defining a function with labeled arguments *)
let rec pow ~base ~exp =
    if exp = 0 then 1 else base * pow ~base ~exp:(exp - 1)


(* 8. Defining a function with optional arguments *)
let rec gcd ?(a=0) b =
    if a = 0 then b else gcd ~a:(b mod a) ~b:a

