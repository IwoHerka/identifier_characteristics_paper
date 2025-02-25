factorial n = fact n
    let fact 0 = 1
        fact m = m * fact (m - 1)
    in fact n