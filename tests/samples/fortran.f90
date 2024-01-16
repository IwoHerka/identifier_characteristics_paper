module myModule
    implicit none
contains

    ! 1. Function with explicit type
    function add(x, y) result(sum)
        integer, intent(in) :: x, y
        integer :: sum
        sum = x + y
    end function add

    ! 2. Subroutine
    subroutine printMessage(message)
        character(len=*), intent(in) :: message
        print *, message
    end subroutine printMessage

    ! 3. Function without explicit type (type inferred from name)
    real function multiply(x, y)
        real, intent(in) :: x, y
        multiply = x * y
    end function multiply

    ! 4. Recursive function
    recursive function factorial(n) result(fact)
        integer, intent(in) :: n
        integer :: fact
        if (n <= 1) then
            fact = 1
        else
            fact = n * factorial(n - 1)
        end if
    end function factorial

    ! 5. Module procedure
    procedure, public :: computeAverage => average
    real function average(x, y)
        real, intent(in) :: x, y
        average = (x + y) / 2.0
    end function average

end module myModule

program main
    use myModule
    implicit none

    ! Example usage
    print *, add(3, 4)
    call printMessage('Hello, Fortran!')
    print *, multiply(3.0, 2.0)
    print *, factorial(5)
    print *, computeAverage(4.0, 6.0)
end program main

