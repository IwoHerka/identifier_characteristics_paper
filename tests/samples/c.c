#include <stdio.h>
#include <stdarg.h>


// Standard Function with Return Type and Parameters
int add(int a, int b) {
    return a + b;
}


// Function with No Return Type (void)
void sayHello() {
    printf("Hello, world!\n");
}


// Function with No Parameters
int getRandomNumber() {
    return rand(); // Returns a random number
}


// Function with Void Parameters
void logTime(void) {
    // Log the current time
}


// Function Returning a Pointer
int* getArray() {
    static int arr[10];
    // Initialize and manipulate arr
    return arr;
}


// Function with Pointer Parameters
void updateValue(int *value) {
    *value = 5;
}


// Variadic Function
double average(int count, ...) {
    va_list ap;
    int j;
    double sum = 0;

    va_start(ap, count);
    for (j = 0; j < count; j++) {
        sum += va_arg(ap, double);
    }
    va_end(ap);

    return sum / count;
}


// Function with Array Parameters
int sumOfElements(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}


// Inline Function
inline int max(int a, int b) {
    return (a > b) ? a : b;
}


// Function Prototypes
int multiply(int a, int b); // Prototype
							//

// ... other code ...

int multiply(int a, int b) { // Implementation
    return a * b;
}


// Static Function
static int internalFunction(int a) {
    return a * a;
}


int main() {
    // Test functions here
    return 0;
}
