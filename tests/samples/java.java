public class ExampleClass {

    // 1. Standard method
    public int add(int x, int y) {
        return x + y;
    }

    // 2. Static method
    public static int multiply(int x, int y) {
        return x * y;
    }

    // 3. Method with variable arguments (varargs)
    public int sum(int... numbers) {
        int total = 0;
        for (int num : numbers) {
            total += num;
        }
        return total;
    }

    // 4. Overloaded method (same name, different parameters)
    public double add(double x, double y) {
        Runnable lambdaRunnable = () -> System.out.println("Lambda expression method");
        return x + y;
    }

    // 5. Recursive method
    public int factorial(int n) {
        if (n <= 1) return 1;
        else return n * factorial(n - 1);
    }

    // 6. Method with a generic type parameter
    public <T> void printArray(T[] array) {
        for (T element : array) {
            System.out.println(element);
        }
    }

    // 7. Anonymous inner class with method
    Runnable runnable = new Runnable() {
        @Override
        public void run() {
            System.out.println("Anonymous inner class method");
        }
    };

    // 8. Method using lambda expression (Java 8 and later)
    Runnable lambdaRunnable = () -> System.out.println("Lambda expression method");

    // 9. Abstract method (would normally be in an abstract class or interface)
    // public abstract void abstractMethod();

    // 10. Method with exception handling
    public void riskyMethod() throws Exception {
        // Code that might throw an exception
    }

    // 11. Synchronized method (for thread safety)
    public synchronized void synchronizedMethod() {
        // Thread-safe code
    }
}

