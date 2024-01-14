add :: Int -> Int -> Int
add 0 y = y
add x y = x + y


max' :: Ord a => a -> a -> a
max' x y
    | x >= y    = x
    | otherwise = y


add :: Int -> Int -> Int
add = \x y -> x + y


square :: Int -> Int
square = (^2)


factorial :: Integer -> Integer
factorial n =
    let fact 0 = 1
        fact m = m * fact (m - 1)
    in fact n


-- In case of nesting, nested functions are treated as their own
factorial :: Integer -> Integer
factorial n = fact n
    where
        fact 0 = 1
        fact m = m * fact (m - 1)


sumList :: [Int] -> Int
sumList = foldr (+) 0


getInputAndPrint :: IO ()
getInputAndPrint = do
  input <- getLine
  putStrLn ("You entered: " ++ input)
